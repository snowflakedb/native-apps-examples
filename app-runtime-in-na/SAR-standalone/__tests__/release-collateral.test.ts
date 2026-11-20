import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

const root = resolve(import.meta.dirname, '../..');
const read = (path: string) => readFileSync(resolve(root, path), 'utf8');

const variants = [
  {
    directory: 'na-warehouse-reference',
    packageName: 'WAREHOUSE_WHISPERER_NA_REFERENCE_PACKAGE',
    applicationName: 'WAREHOUSE_WHISPERER_NA_REFERENCE',
    warehouseMode: 'reference',
  },
  {
    directory: 'na-warehouse-in-app',
    packageName: 'WAREHOUSE_WHISPERER_NA_MANAGED_PACKAGE',
    applicationName: 'WAREHOUSE_WHISPERER_NA_MANAGED',
    warehouseMode: 'managed',
  },
] as const;

describe('release collateral', () => {
  it('keeps both Native App variants pinned to the standalone SAR runtime', () => {
    for (const variant of variants) {
      const manifest = read(`${variant.directory}/manifest.yml`);
      const setup = read(`${variant.directory}/setup.sql`);
      const project = read(`${variant.directory}/snowflake.yml`);

      expect(manifest).toContain('application_service: app_public.warehouse_whisperer');
      expect(manifest).toContain('package: WAREHOUSE_WHISPERER');
      expect(manifest).toContain('version: VERSION$1');
      expect(setup).toContain('CREATE APPLICATION SERVICE IF NOT EXISTS app_public.warehouse_whisperer');
      expect(setup).toContain('FROM PACKAGE warehouse_whisperer');
      expect(project).toContain(`identifier: ${variant.packageName}`);
      expect(project).toContain(`identifier: ${variant.applicationName}`);
    }
  });

  it('keeps the warehouse architectures mutually exclusive', () => {
    const referenceManifest = read('na-warehouse-reference/manifest.yml');
    const referenceSetup = read('na-warehouse-reference/setup.sql');
    const managedManifest = read('na-warehouse-in-app/manifest.yml');
    const managedSetup = read('na-warehouse-in-app/setup.sql');

    expect(referenceManifest).toContain('query_warehouse:');
    expect(referenceSetup).toContain("REFERENCE('QUERY_WAREHOUSE')");
    expect(referenceManifest).not.toContain('CREATE WAREHOUSE:');

    expect(managedManifest).toContain('CREATE WAREHOUSE:');
    expect(managedManifest).not.toContain('query_warehouse:');
    expect(managedSetup).toContain('CREATE WAREHOUSE IF NOT EXISTS WAREHOUSE_WHISPERER_APP_WH');
    expect(managedSetup).toContain('WAREHOUSE_SIZE = XSMALL');
    expect(managedSetup).toContain('AUTO_SUSPEND = 60');
    expect(managedSetup).toContain('AUTO_RESUME = TRUE');
    expect(managedSetup).toContain('QUERY_WAREHOUSE = WAREHOUSE_WHISPERER_APP_WH');
    expect(managedSetup).not.toContain("REFERENCE('QUERY_WAREHOUSE')");
  });

  it('documents both product variants in the root architecture guide', () => {
    const readme = read('README.md');

    expect(readme).toContain('SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY');
    expect(readme).toContain('SNOWFLAKE.CORTEX_USER');
    expect(readme).toContain('WAREHOUSE_WHISPERER_NA_REFERENCE');
    expect(readme).toContain('WAREHOUSE_WHISPERER_NA_MANAGED');
    expect(readme).toContain("SYSTEM$REFERENCE('WAREHOUSE', '<consumer_warehouse>', 'PERSISTENT', 'USAGE')");
    expect(readme).toContain('WAREHOUSE_WHISPERER_APP_WH');
  });

  it('removes the obsolete single Native App layout', () => {
    expect(existsSync(resolve(root, 'native-app'))).toBe(false);
  });
});
