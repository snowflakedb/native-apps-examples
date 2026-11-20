export const MAX_ROWS = 200;
export const MAX_LOOKBACK_DAYS = 90;

const QUERY_HISTORY_COLUMNS = `
QUERY_ID, QUERY_TEXT, DATABASE_NAME, SCHEMA_NAME, QUERY_TYPE, USER_NAME,
ROLE_NAME, WAREHOUSE_NAME, WAREHOUSE_SIZE, WAREHOUSE_TYPE, CLUSTER_NUMBER,
QUERY_TAG, EXECUTION_STATUS, ERROR_CODE, ERROR_MESSAGE, START_TIME, END_TIME,
TOTAL_ELAPSED_TIME, BYTES_SCANNED, PERCENTAGE_SCANNED_FROM_CACHE,
BYTES_WRITTEN, BYTES_WRITTEN_TO_RESULT, BYTES_READ_FROM_RESULT, ROWS_PRODUCED,
ROWS_INSERTED, ROWS_UPDATED, ROWS_DELETED, PARTITIONS_SCANNED, PARTITIONS_TOTAL,
BYTES_SPILLED_TO_LOCAL_STORAGE, BYTES_SPILLED_TO_REMOTE_STORAGE,
BYTES_SENT_OVER_THE_NETWORK, COMPILATION_TIME, EXECUTION_TIME,
QUEUED_PROVISIONING_TIME, QUEUED_REPAIR_TIME, QUEUED_OVERLOAD_TIME,
TRANSACTION_BLOCKED_TIME, CREDITS_USED_CLOUD_SERVICES, QUERY_LOAD_PERCENT,
CHILD_QUERIES_WAIT_TIME, QUERY_RETRY_TIME, QUERY_RETRY_CAUSE,
FAULT_HANDLING_TIME, RELEASE_VERSION, QUERY_HASH, QUERY_PARAMETERIZED_HASH`;

const FORBIDDEN = /\b(INSERT|UPDATE|DELETE|MERGE|COPY|PUT|GET|REMOVE|ALTER|DROP|CREATE|TRUNCATE|CALL|EXECUTE|GRANT|REVOKE|SHOW|DESCRIBE|USE)\b/i;
const SOURCE_NAME = 'SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY';
const SOURCE = /\bSNOWFLAKE\.ACCOUNT_USAGE\.QUERY_HISTORY\b/i;
const SOURCE_RELATION = /\b(?:FROM|JOIN)\s+SNOWFLAKE\.ACCOUNT_USAGE\.QUERY_HISTORY\b/i;
const LOOKBACK = /\bEND_TIME\s*>=\s*DATEADD\s*\(\s*['"]?DAY['"]?\s*,\s*-(\d+)\s*,\s*CURRENT_TIMESTAMP\s*\(\s*\)\s*\)/i;

function assertApprovedSources(sql: string) {
  const ctes = new Set(
    [...sql.matchAll(/(?:\bWITH\b|,)\s*([A-Z_][\w$]*)\s+AS\s*\(/gi)].map((match) => match[1].toUpperCase()),
  );
  const sources = [...sql.matchAll(/\b(?:FROM|JOIN)\s+([A-Z_][\w$]*(?:\.[A-Z_][\w$]*){0,2})/gi)];
  if (sources.length === 0) throw new Error('The query must use QUERY_HISTORY.');
  for (const match of sources) {
    const source = match[1].toUpperCase();
    if (source !== SOURCE_NAME && !ctes.has(source)) {
      throw new Error('The query referenced an unapproved source.');
    }
  }
}

export function normalizeQuestion(value: unknown): string {
  if (typeof value !== 'string') throw new Error('Question must be text.');
  const question = value.trim();
  if (!question) throw new Error('Ask a question about query activity.');
  if (question.length > 1000) throw new Error('Question must be 1,000 characters or fewer.');
  return question;
}

export function extractSql(value: unknown): string {
  const raw = String(value ?? '').trim();
  const fenced = raw.match(/```(?:sql)?\s*([\s\S]*?)```/i)?.[1]?.trim();
  return (fenced ?? raw).replace(/;\s*$/, '').trim();
}

export function constrainSql(candidate: string): string {
  const sql = extractSql(candidate);
  if (!/^(SELECT|WITH)\b/i.test(sql)) throw new Error('The analyst did not return a read-only query.');
  if (FORBIDDEN.test(sql) || sql.includes(';')) throw new Error('The analyst returned unsupported SQL.');
  if (!SOURCE.test(sql) || !SOURCE_RELATION.test(sql)) throw new Error('The query must use QUERY_HISTORY.');
  assertApprovedSources(sql);
  const lookbackDays = Number(LOOKBACK.exec(sql)?.[1]);
  if (!lookbackDays || lookbackDays > MAX_LOOKBACK_DAYS) {
    throw new Error('The query must constrain END_TIME to the last 90 days.');
  }
  return `SELECT * FROM (${sql}) AS ANALYST_RESULT LIMIT ${MAX_ROWS}`;
}

export function sqlGenerationPrompt(question: string): string {
  return `You are a Snowflake operations analyst. Return only one Snowflake SQL SELECT statement, with no markdown or explanation.
Use only SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY. Use only columns from this exact schema:
${QUERY_HISTORY_COLUMNS}
Never invent columns. TOTAL_QUEUED_TIME does not exist. For total queued time, use
COALESCE(QUEUED_PROVISIONING_TIME, 0) + COALESCE(QUEUED_REPAIR_TIME, 0) + COALESCE(QUEUED_OVERLOAD_TIME, 0).
Never use SELECT *. Never expose QUERY_TEXT unless the question explicitly asks for it. Use END_TIME >= DATEADD('day', -90, CURRENT_TIMESTAMP()) and never query a longer period. Use UTC timestamps. Prefer aggregates and include clear aliases. Bound any detail result to 200 rows. Question: ${question}`;
}

export function summaryPrompt(question: string, columns: string[], rows: unknown[]): string {
  return `Answer the user's question using only the supplied Snowflake query result. Be concise and specific. State when evidence is insufficient. Mention that ACCOUNT_USAGE is UTC and can lag up to 45 minutes. Do not invent values or recommendations unsupported by the rows.\nQuestion: ${question}\nColumns: ${JSON.stringify(columns)}\nRows: ${JSON.stringify(rows).slice(0, 60000)}`;
}
