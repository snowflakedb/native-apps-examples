import { asCaller, snowflake } from '@/lib/snowflake';
import type { SarClient } from '@snowflake/sar-sdk';

/** Owner client or a caller view: both expose `query()`. */
export type SnowflakeQuery = Pick<SarClient, 'query'>;

/**
 * Who answered a query:
 * - "caller": the person viewing the deployed app (caller's rights ran).
 * - "dev": local dev or a Workspaces preview, where caller's rights does not
 *   apply and every query runs as the developer's or owner's credentials.
 */
export type Identity = 'caller' | 'dev';

/**
 * Caller's rights only applies to a deployed app (`next start`). Under `next dev`,
 * lib/snowflake.ts sets callerAsOwner on the SDK's createConnectionOptions() provider.
 */
export function callersRightsActive(): boolean {
  return process.env.NODE_ENV !== 'development';
}

/**
 * Run `load` with caller's rights in a deployed app. Missing caller context
 * and query failures propagate without retrying as the owner. Local dev and
 * previews use the developer's connection and label the result accordingly.
 *
 *   const { identity, ...data } = await withCaller((client) => load(client))
 */
export async function withCaller<T extends object>(
  load: (client: SnowflakeQuery) => Promise<T>,
): Promise<T & { identity: Identity }> {
  if (!callersRightsActive()) return { ...(await load(snowflake)), identity: 'dev' };
  return { ...(await load(await asCaller())), identity: 'caller' };
}

/** Single-query shorthand for withCaller. */
export async function queryAsCaller(sql: string) {
  return withCaller(async (client) => {
    const { rows } = await client.query(sql);
    return { rows };
  });
}

/**
 * A database to resolve INFORMATION_SCHEMA table functions against: the
 * session's current database, else the first one the role can see. Returns a
 * quoted identifier, ready to interpolate into SQL.
 */
export async function resolveDatabase(client: SnowflakeQuery = snowflake): Promise<string | null> {
  const current = await client.query<{ DB: string | null }>('SELECT CURRENT_DATABASE() AS DB');
  const db = current.rows[0]?.DB;
  if (db) return quoteIdent(db);
  const dbs = await client.query<{ name?: string }>('SHOW TERSE DATABASES LIMIT 1');
  const name = dbs.rows[0]?.name;
  return name ? quoteIdent(name) : null;
}

/** Quote a Snowflake identifier, e.g. a user name from CURRENT_USER(). */
export function quoteIdent(name: string): string {
  return `"${name.replace(/"/g, '""')}"`;
}
