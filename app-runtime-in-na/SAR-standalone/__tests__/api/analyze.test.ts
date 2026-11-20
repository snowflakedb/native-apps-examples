import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  query: vi.fn(),
}));

vi.mock('../../lib/snowflake', () => ({
  snowflake: { query: mocks.query },
}));

import { POST } from '../../app/api/analyze/route';

const generatedSql = "SELECT WAREHOUSE_NAME, COUNT(*) AS QUERY_COUNT FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY WHERE END_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP()) GROUP BY WAREHOUSE_NAME";

function request(body: unknown) {
  return new Request('http://localhost/api/analyze', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'sf-context-current-user-token': 'caller-token' },
    body: JSON.stringify(body),
  });
}

describe('POST /api/analyze', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('uses the least-privilege owner client for generation, evidence, and summary', async () => {
    mocks.query
      .mockResolvedValueOnce({ rows: [{ SQL_TEXT: generatedSql }], columns: [{ name: 'SQL_TEXT' }] })
      .mockResolvedValueOnce({ rows: [{ WAREHOUSE_NAME: 'WH', QUERY_COUNT: 4 }], columns: [{ name: 'WAREHOUSE_NAME' }, { name: 'QUERY_COUNT' }] })
      .mockResolvedValueOnce({ rows: [{ ANSWER: 'WH ran four queries.' }], columns: [{ name: 'ANSWER' }] });

    const incoming = request({ question: 'Which warehouse was busiest?' });
    const response = await POST(incoming);
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(mocks.query).toHaveBeenCalledTimes(3);
    expect(mocks.query.mock.calls[0][0]).toContain('CORTEX.COMPLETE');
    expect(mocks.query.mock.calls[0][1].binds[0]).toContain('Which warehouse was busiest?');
    expect(mocks.query.mock.calls[1][0]).toMatch(/^SELECT \* FROM \(.+\) AS ANALYST_RESULT LIMIT 200$/);
    expect(body).toMatchObject({
      answer: 'WH ran four queries.',
      columns: ['WAREHOUSE_NAME', 'QUERY_COUNT'],
      rows: [{ WAREHOUSE_NAME: 'WH', QUERY_COUNT: 4 }],
      rowCount: 1,
      source: 'SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY',
    });
  });

  it('rejects invalid input before querying Snowflake', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const response = await POST(request({ question: '   ' }));
    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: 'Ask a question about query activity.' });
    expect(mocks.query).not.toHaveBeenCalled();
  });

  it('does not execute generated SQL that escapes the approved source', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    mocks.query.mockResolvedValueOnce({
      rows: [{ SQL_TEXT: "SELECT q.USER_NAME FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q JOIN PRIVATE.PUBLIC.USERS u ON q.USER_NAME = u.NAME WHERE q.END_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())" }],
      columns: [{ name: 'SQL_TEXT' }],
    });

    const response = await POST(request({ question: 'Show user details' }));
    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: 'The query referenced an unapproved source.' });
    expect(mocks.query).toHaveBeenCalledTimes(1);
  });
});
