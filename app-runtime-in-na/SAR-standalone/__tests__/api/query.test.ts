import { beforeEach, describe, expect, it, vi } from 'vitest';
import { GET } from '../../app/api/query/route';

const mocks = vi.hoisted(() => {
  const callerQuery = vi.fn();
  return {
    query: vi.fn(),
    callerQuery,
    asCaller: vi.fn(async () => ({ query: callerQuery })),
  };
});

vi.mock('../../lib/snowflake', () => ({
  snowflake: { query: mocks.query },
  asCaller: mocks.asCaller,
}));

const QUERY = `SELECT CURRENT_USER() AS "USER", CURRENT_ROLE() AS ROLE`;

describe('GET /api/query', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns service and caller results on success', async () => {
    mocks.query.mockResolvedValueOnce({ rows: [{ USER: 'SERVICE_USER', ROLE: 'SERVICE_ROLE' }] });
    mocks.callerQuery.mockResolvedValueOnce({
      rows: [{ USER: 'CALLER_USER', ROLE: 'CALLER_ROLE' }],
    });

    const response = await GET();
    const json = await response.json();

    expect(response.status).toBe(200);
    expect(json.service).toEqual({
      mode: 'service',
      result: { USER: 'SERVICE_USER', ROLE: 'SERVICE_ROLE' },
    });
    expect(json.caller).toEqual({
      mode: 'caller',
      result: { USER: 'CALLER_USER', ROLE: 'CALLER_ROLE' },
    });
    expect(mocks.query).toHaveBeenCalledWith(QUERY);
    expect(mocks.asCaller).toHaveBeenCalledTimes(1);
    expect(mocks.callerQuery).toHaveBeenCalledWith(QUERY);
  });

  it('includes caller error when the caller query throws', async () => {
    mocks.query.mockResolvedValueOnce({ rows: [{ USER: 'SERVICE_USER', ROLE: 'SERVICE_ROLE' }] });
    mocks.callerQuery.mockRejectedValueOnce(new Error('No sf-context-current-user-token header'));

    const response = await GET();
    const json = await response.json();

    expect(response.status).toBe(200);
    expect(json.service.result).toEqual({ USER: 'SERVICE_USER', ROLE: 'SERVICE_ROLE' });
    expect(json.caller.mode).toBe('caller');
    expect(json.caller.result).toBeNull();
    expect(json.caller.error).toContain('No sf-context-current-user-token');
  });

  it('returns null results when queries return empty rows', async () => {
    mocks.query.mockResolvedValue({ rows: [] });
    mocks.callerQuery.mockResolvedValue({ rows: [] });

    const response = await GET();
    const json = await response.json();

    expect(response.status).toBe(200);
    expect(json.service.result).toBeNull();
    expect(json.caller.result).toBeNull();
  });

  it('returns 500 when service query throws', async () => {
    mocks.query.mockRejectedValue(new Error('DB connection failed'));
    vi.spyOn(console, 'error').mockImplementation(() => {});

    const response = await GET();
    const json = await response.json();

    expect(response.status).toBe(500);
    expect(json.error).toBe('Query failed');
  });
});
