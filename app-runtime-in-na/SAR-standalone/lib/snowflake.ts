/**
 * Snowflake access for this app, backed by @snowflake/sar-sdk. Server code only: import it from
 * Server Components, Route Handlers, and Server Actions, never from a "use client" component.
 *
 *   import { snowflake, asCaller } from "@/lib/snowflake"
 *
 *   // Owner's rights: runs as the app's service identity.
 *   const { rows } = await snowflake.query("SELECT ... WHERE ID = ?", { binds: [id] })
 *
 *   // Caller's rights: runs as the user who opened the app.
 *   const caller = await asCaller()
 *   const { rows } = await caller.query("SELECT ...")
 *
 *   // A secret declared under the top-level `secrets:` key in app.yml.
 *   const { username, password } = await snowflake.secrets.getPassword("DB_CREDS")
 *
 * `snowflake` is the SDK's SarClient and `asCaller()` returns its CallerClient for the current
 * request. node_modules/@snowflake/sar-sdk/README.md documents the full API: result values,
 * streaming, long-running and detached queries, secrets, account REST calls, and errors.
 */

import { createSarClient, type CallerClient, type SarClient } from '@snowflake/sar-sdk';
import { createConnectionOptions, fromDefault } from '@snowflake/sar-sdk/auth';
import { createConnectionManager } from '@snowflake/sar-sdk/connections';
import { createFetchClient } from '@snowflake/sar-sdk/http';
import { createQueryClient } from '@snowflake/sar-sdk/query';
import { createSecretsClient } from '@snowflake/sar-sdk/secrets';
import { headers } from 'next/headers';
import driver from 'snowflake-sdk';

// The driver logs every connection at INFO level by default. Configure the module this
// client uses; the SDK does not configure a driver it did not load itself.
driver.configure({ logLevel: 'ERROR' });

// `next dev` sets this, locally and in a Snowsight workspace preview. A deployed app runs
// `next start`, so caller views there keep the signed-in user's identity.
const development = process.env.NODE_ENV === 'development';

function createClient(): SarClient {
  // fromDefault() reads the mounted platform token when one exists, and the default SnowCLI
  // profile otherwise. Cache the local SSO token: a dev server started in the background has
  // no TTY, and without this every query can open a new browser tab.
  const connection = fromDefault();
  connection.clientStoreTemporaryCredential = true;
  const options = createConnectionOptions(connection, { callerAsOwner: development });
  const connections = createConnectionManager(options, {
    driver,
    logger: (event) => console.log('[snowflake]', JSON.stringify(event)),
  });
  return createSarClient({
    queryClient: createQueryClient(connections),
    fetchClient: createFetchClient(options),
    secretsClient: createSecretsClient(),
  });
}

const globalForSnowflake = globalThis as typeof globalThis & { snowflakeClient?: SarClient };

function client(): SarClient {
  return (globalForSnowflake.snowflakeClient ??= createClient());
}

/**
 * One client per server process, kept across dev-server module reloads. It is created on first
 * use, not at import: `next build` imports every route, and fromDefault() throws where no
 * connection is configured, such as in CI.
 */
export const snowflake: SarClient = new Proxy({} as SarClient, {
  get(_target, key) {
    const target = client();
    const value: unknown = Reflect.get(target, key, target);
    return typeof value === 'function' ? value.bind(target) : value;
  },
});

/**
 * A caller's-rights view for the current request. Snowflake injects the calling user's token in
 * the `sf-context-current-user-token` ingress header. Under `npm run dev`, `callerAsOwner` makes
 * this view use the local connection instead. Use it within one request only.
 */
export async function asCaller(): Promise<CallerClient> {
  return snowflake.asCaller({ headers: await headers() });
}
