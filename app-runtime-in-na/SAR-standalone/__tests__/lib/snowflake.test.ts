import { beforeEach, describe, expect, it, vi } from 'vitest';

const sdk = vi.hoisted(() => {
  const callerView = { query: vi.fn() };
  const client = {
    query: vi.fn(),
    asCaller: vi.fn(() => callerView),
    secrets: { getPassword: vi.fn() },
  };
  const connections = { name: 'connections' };
  const queryClient = { name: 'queryClient' };
  const fetchClient = { name: 'fetchClient' };
  const secretsClient = { name: 'secretsClient' };
  return {
    callerView,
    client,
    connections,
    queryClient,
    fetchClient,
    secretsClient,
    createSarClient: vi.fn(() => client),
    createConnectionOptions: vi.fn((connection: object) => ({ connection })),
    createConnectionManager: vi.fn((_options: object, _settings: object) => connections),
    createQueryClient: vi.fn(() => queryClient),
    createFetchClient: vi.fn(() => fetchClient),
    createSecretsClient: vi.fn(() => secretsClient),
    fromDefault: vi.fn(() => ({ account: 'test' })),
    configure: vi.fn(),
  };
});

vi.mock('@snowflake/sar-sdk', () => ({ createSarClient: sdk.createSarClient }));
vi.mock('@snowflake/sar-sdk/auth', () => ({
  createConnectionOptions: sdk.createConnectionOptions,
  fromDefault: sdk.fromDefault,
}));
vi.mock('@snowflake/sar-sdk/connections', () => ({
  createConnectionManager: sdk.createConnectionManager,
}));
vi.mock('@snowflake/sar-sdk/query', () => ({ createQueryClient: sdk.createQueryClient }));
vi.mock('@snowflake/sar-sdk/http', () => ({ createFetchClient: sdk.createFetchClient }));
vi.mock('@snowflake/sar-sdk/secrets', () => ({ createSecretsClient: sdk.createSecretsClient }));
vi.mock('snowflake-sdk', () => ({ default: { configure: sdk.configure } }));
vi.mock('next/headers', () => ({
  headers: vi.fn(async () => new Headers({ 'sf-context-current-user-token': 'caller-token' })),
}));

async function load() {
  vi.resetModules();
  delete (globalThis as { snowflakeClient?: unknown }).snowflakeClient;
  return import('@/lib/snowflake');
}

describe('lib/snowflake', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubEnv('NODE_ENV', 'production');
  });

  it('reads the connection on first use, not at import', async () => {
    sdk.fromDefault.mockImplementationOnce(() => {
      throw new Error('no connection');
    });
    const { snowflake } = await load();

    expect(sdk.fromDefault).not.toHaveBeenCalled();
    expect(sdk.createConnectionManager).not.toHaveBeenCalled();
    expect(sdk.createQueryClient).not.toHaveBeenCalled();
    expect(sdk.createFetchClient).not.toHaveBeenCalled();
    expect(sdk.createSecretsClient).not.toHaveBeenCalled();
    expect(sdk.createSarClient).not.toHaveBeenCalled();

    expect(() => snowflake.query('SELECT 1')).toThrow('no connection');
    snowflake.query('SELECT 1');
    expect(sdk.client.query).toHaveBeenCalledWith('SELECT 1');
    expect(sdk.createSarClient).toHaveBeenCalledTimes(1);
  });

  it('creates one SDK client from the default connection and the configured driver', async () => {
    const { snowflake } = await load();
    snowflake.query('SELECT 1');
    snowflake.query('SELECT 2');

    expect(sdk.client.query).toHaveBeenCalledTimes(2);
    expect(sdk.configure).toHaveBeenCalledWith({ logLevel: 'ERROR' });
    expect(sdk.fromDefault).toHaveBeenCalledTimes(1);
    expect(sdk.createConnectionOptions).toHaveBeenCalledWith(
      { account: 'test', clientStoreTemporaryCredential: true },
      { callerAsOwner: false },
    );
    const options = sdk.createConnectionOptions.mock.results[0]?.value;
    expect(sdk.createConnectionManager).toHaveBeenCalledTimes(1);
    expect(sdk.createConnectionManager).toHaveBeenCalledWith(
      options,
      expect.objectContaining({
        driver: expect.objectContaining({ configure: sdk.configure }),
        logger: expect.any(Function),
      }),
    );
    expect(sdk.createQueryClient).toHaveBeenCalledExactlyOnceWith(sdk.connections);
    expect(sdk.createFetchClient).toHaveBeenCalledExactlyOnceWith(options);
    expect(sdk.createSecretsClient).toHaveBeenCalledExactlyOnceWith();
    expect(sdk.createSarClient).toHaveBeenCalledExactlyOnceWith({
      queryClient: sdk.queryClient,
      fetchClient: sdk.fetchClient,
      secretsClient: sdk.secretsClient,
    });
  });

  it('passes the structured SDK logger to the connection manager', async () => {
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    try {
      (await load()).snowflake.query('SELECT 1');
      const settings = sdk.createConnectionManager.mock.calls[0]?.[1] as {
        logger: (event: object) => void;
      };
      const event = { event: 'query-succeeded', queryId: 'test-query', rowCount: 1 };
      settings.logger(event);
      expect(log).toHaveBeenCalledWith('[snowflake]', JSON.stringify(event));
    } finally {
      log.mockRestore();
    }
  });

  it('exposes the client secrets API', async () => {
    const { snowflake } = await load();
    snowflake.secrets.getPassword('DB_CREDS');

    expect(sdk.client.secrets.getPassword).toHaveBeenCalledWith('DB_CREDS');
  });

  it('runs caller views as the developer under next dev', async () => {
    vi.stubEnv('NODE_ENV', 'development');
    const { asCaller } = await load();
    await asCaller();

    expect(sdk.createConnectionOptions).toHaveBeenCalledWith(expect.any(Object), {
      callerAsOwner: true,
    });
  });

  it('reuses the client across module reloads', async () => {
    (await load()).snowflake.query('SELECT 1');
    vi.resetModules();
    const { snowflake } = await import('@/lib/snowflake');
    snowflake.query('SELECT 2');

    expect(sdk.client.query).toHaveBeenCalledTimes(2);
    expect(sdk.createConnectionManager).toHaveBeenCalledTimes(1);
    expect(sdk.createQueryClient).toHaveBeenCalledTimes(1);
    expect(sdk.createFetchClient).toHaveBeenCalledTimes(1);
    expect(sdk.createSecretsClient).toHaveBeenCalledTimes(1);
    expect(sdk.createSarClient).toHaveBeenCalledTimes(1);
  });

  it('asCaller() scopes the client to the current request headers', async () => {
    const { asCaller } = await load();

    const caller = await asCaller();

    expect(caller).toBe(sdk.callerView);
    const [{ headers }] = sdk.client.asCaller.mock.calls[0] as unknown as [{ headers: Headers }];
    expect(headers.get('sf-context-current-user-token')).toBe('caller-token');
  });
});
