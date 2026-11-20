import { describe, expect, it } from 'vitest';
import { constrainSql, extractSql, normalizeQuestion, sqlGenerationPrompt } from '@/lib/analyst';

describe('analyst guardrails', () => {
  it('normalizes valid questions', () => expect(normalizeQuestion('  show failures ')).toBe('show failures'));
  it('rejects empty and oversized questions', () => {
    expect(() => normalizeQuestion('   ')).toThrow(/Ask a question/);
    expect(() => normalizeQuestion('x'.repeat(1001))).toThrow(/1,000/);
  });
  it('extracts fenced SQL', () => expect(extractSql('```sql\nSELECT 1;\n```')).toBe('SELECT 1'));
  it('allows only bounded query history selects and applies a hard limit', () => {
    const bounded = "SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY WHERE END_TIME >= DATEADD('day', -90, CURRENT_TIMESTAMP())";
    expect(constrainSql(bounded)).toMatch(/LIMIT 200$/);
    expect(() => constrainSql('DELETE FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY')).toThrow(/read-only/);
    expect(() => constrainSql('SELECT * FROM OTHER.TABLE')).toThrow(/QUERY_HISTORY/);
    expect(() => constrainSql(`${bounded}; DROP TABLE X`)).toThrow(/unsupported/);
  });
  it('rejects missing or excessive lookback windows', () => {
    expect(() => constrainSql('SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY')).toThrow(/last 90 days/);
    expect(() => constrainSql("SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY WHERE END_TIME >= DATEADD('day', -91, CURRENT_TIMESTAMP())")).toThrow(/last 90 days/);
  });
  it('rejects joins and subqueries against unapproved sources', () => {
    const lookback = "q.END_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())";
    expect(() => constrainSql(`SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q JOIN SECRET_DB.PUBLIC.USERS u ON q.USER_NAME = u.NAME WHERE ${lookback}`)).toThrow(/unapproved source/);
    expect(() => constrainSql(`SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q WHERE ${lookback} AND EXISTS (SELECT 1 FROM OTHER.TABLE)`)).toThrow(/unapproved source/);
    expect(() => constrainSql("SELECT 'SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY' FROM OTHER.TABLE WHERE END_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())")).toThrow(/QUERY_HISTORY/);
  });
  it('allows CTEs derived solely from query history', () => {
    const sql = "WITH recent AS (SELECT WAREHOUSE_NAME, END_TIME FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY WHERE END_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())) SELECT WAREHOUSE_NAME, COUNT(*) FROM recent GROUP BY WAREHOUSE_NAME";
    expect(constrainSql(sql)).toMatch(/LIMIT 200$/);
  });
  it('instructs Cortex to enforce the bounded window and source', () => {
    const prompt = sqlGenerationPrompt('what is slow?');
    expect(prompt).toContain("DATEADD('day', -90");
    expect(prompt).toContain('SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY');
    expect(prompt).toContain('200 rows');
  });
  it('defines total queued time from real query history columns', () => {
    const prompt = sqlGenerationPrompt('Which warehouses queued the longest?');
    expect(prompt).toContain('QUEUED_PROVISIONING_TIME');
    expect(prompt).toContain('QUEUED_REPAIR_TIME');
    expect(prompt).toContain('QUEUED_OVERLOAD_TIME');
    expect(prompt).toContain('TOTAL_QUEUED_TIME does not exist');
  });
});
