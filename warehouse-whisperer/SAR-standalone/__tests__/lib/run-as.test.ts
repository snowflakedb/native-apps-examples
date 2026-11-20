import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => {
  const caller = { query: vi.fn(), kind: 'caller' as const };
  const owner = { query: vi.fn(), kind: 'owner' as const };
  return { caller, owner, asCaller: vi.fn(async () => caller) };
});

vi.mock('../../lib/snowflake', () => ({
  snowflake: mocks.owner,
  asCaller: mocks.asCaller,
}));

import { queryAsCaller, quoteIdent, resolveDatabase, withCaller } from '../../lib/run-as';

describe('withCaller', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubEnv('NODE_ENV', 'production');
  });
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("labels a successful caller's-rights call as caller", async () => {
    const load = vi.fn().mockResolvedValue({ n: 1 });
    expect(await withCaller(load)).toEqual({ n: 1, identity: 'caller' });
    expect(load).toHaveBeenCalledWith(mocks.caller);
    expect(mocks.owner.query).not.toHaveBeenCalled();
  });

  it.each(['CALLER_CONTEXT_REQUIRED', 'AUTH_NOT_SUPPORTED'])(
    'propagates %s without invoking the loader or owner',
    async (code) => {
      const err = Object.assign(new Error('Caller context unavailable'), {
        name: 'SarError',
        code,
        details: {},
      });
      mocks.asCaller.mockRejectedValueOnce(err);
      const load = vi.fn();
      await expect(withCaller(load)).rejects.toBe(err);
      expect(load).not.toHaveBeenCalled();
      expect(mocks.owner.query).not.toHaveBeenCalled();
    },
  );

  it.each(['002003', '003001'])('never retries privilege error %s as owner', async (errorCode) => {
    const err = Object.assign(new Error('Caller query denied'), {
      name: 'SarError',
      code: 'QUERY_FAILED',
      details: { errorCode },
    });
    const load = vi.fn().mockRejectedValueOnce(err).mockResolvedValueOnce({ n: 2 });
    await expect(withCaller(load)).rejects.toBe(err);
    expect(load).toHaveBeenCalledExactlyOnceWith(mocks.caller);
    expect(mocks.owner.query).not.toHaveBeenCalled();
  });

  it.each([
    'SQL access control error: Insufficient privileges to operate on warehouse',
    'Object does not exist or not authorized.',
    'No sf-context-current-user-token header.',
    'SQL compilation error: syntax error line 1',
    'Statement reached its statement timeout',
  ])('propagates errors without classifying message text: %s', async (message) => {
    const err = new Error(message);
    const load = vi.fn().mockRejectedValueOnce(err).mockResolvedValueOnce({ n: 2 });
    await expect(withCaller(load)).rejects.toBe(err);
    expect(load).toHaveBeenCalledExactlyOnceWith(mocks.caller);
    expect(mocks.owner.query).not.toHaveBeenCalled();
  });

  it('does not retry an unrelated error whose cause matches the old heuristic', async () => {
    const err = new Error('Unrelated failure', { cause: new Error('Insufficient privileges') });
    const load = vi.fn().mockRejectedValueOnce(err).mockResolvedValueOnce({ n: 2 });
    await expect(withCaller(load)).rejects.toBe(err);
    expect(load).toHaveBeenCalledExactlyOnceWith(mocks.caller);
    expect(mocks.owner.query).not.toHaveBeenCalled();
  });

  it('uses caller queries in the single-query shorthand', async () => {
    mocks.caller.query.mockResolvedValueOnce({ rows: [{ n: 1 }] });
    expect(await queryAsCaller('SELECT 1')).toEqual({ rows: [{ n: 1 }], identity: 'caller' });
    expect(mocks.caller.query).toHaveBeenCalledExactlyOnceWith('SELECT 1');
    expect(mocks.owner.query).not.toHaveBeenCalled();
  });

  it('never labels dev or preview results as caller', async () => {
    vi.stubEnv('NODE_ENV', 'development');
    const load = vi.fn().mockResolvedValue({ n: 3 });
    expect(await withCaller(load)).toEqual({ n: 3, identity: 'dev' });
    expect(load).toHaveBeenCalledWith(mocks.owner);
    expect(mocks.asCaller).not.toHaveBeenCalled();
  });
});

describe('run-as helpers', () => {
  beforeEach(() => vi.clearAllMocks());

  it('quotes identifiers', () => {
    expect(quoteIdent('My Db')).toBe('"My Db"');
    expect(quoteIdent('a"b')).toBe('"a""b"');
  });

  it('resolves a quoted database name', async () => {
    mocks.owner.query
      .mockResolvedValueOnce({ rows: [{ DB: null }] })
      .mockResolvedValueOnce({ rows: [{ name: 'Mixed_Case' }] });
    expect(await resolveDatabase()).toBe('"Mixed_Case"');
    // Accounts can have thousands of databases; only the first is needed.
    expect(mocks.owner.query).toHaveBeenLastCalledWith('SHOW TERSE DATABASES LIMIT 1');
  });
});
