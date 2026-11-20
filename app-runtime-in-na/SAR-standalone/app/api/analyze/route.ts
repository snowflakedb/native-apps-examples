import { constrainSql, normalizeQuestion, sqlGenerationPrompt, summaryPrompt } from '@/lib/analyst';
import { snowflake } from '@/lib/snowflake';

export const dynamic = 'force-dynamic';

function errorResponse(error: unknown) {
  console.error('Warehouse analysis failed', error);
  const message = error instanceof Error && /Question|Ask a question|read-only|unsupported|QUERY_HISTORY|unapproved|last 90 days/.test(error.message)
    ? error.message
    : 'Analysis failed. Confirm your role can use Cortex AI and read SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY.';
  return Response.json({ error: message }, { status: 400 });
}

export async function POST(request: Request) {
  try {
    const question = normalizeQuestion((await request.json()).question);
    const generated = await snowflake.query<{ SQL_TEXT: string }>(
      `SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-70b', ?) AS SQL_TEXT`,
      { binds: [sqlGenerationPrompt(question)] },
    );
    const sql = constrainSql(generated.rows[0]?.SQL_TEXT ?? '');
    const result = await snowflake.query<Record<string, unknown>>(sql);
    const columns = result.columns.map((column) => column.name);
    const evidence = result.rows.slice(0, 200);
    const summarized = await snowflake.query<{ ANSWER: string }>(
      `SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-70b', ?) AS ANSWER`,
      { binds: [summaryPrompt(question, columns, evidence)] },
    );

    return Response.json({
      answer: summarized.rows[0]?.ANSWER ?? 'No summary was returned.',
      sql,
      columns,
      rows: evidence,
      rowCount: evidence.length,
      source: 'SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY',
      freshness: 'UTC; up to 45 minutes latency',
    });
  } catch (error) {
    return errorResponse(error);
  }
}
