#!/usr/bin/env python3
"""
Command-line interface for Snowflake Manifest from Share.
"""

import argparse
import logging
import sys
import os
from typing import Optional
from .connection import SnowflakeConnection, _secure_read_private_key
from .share_manifest_generator import ShareManifestGenerator
from .yaml_formatter import YAMLFormatter


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_connection_from_args(args) -> SnowflakeConnection:
    """Create SnowflakeConnection from command line arguments."""
    # Validate that either account or host is provided
    if not args.account and not args.host:
        logging.error("Either --account or --host must be provided")
        sys.exit(1)
    
    # Determine account parameter - prefer host if provided
    if args.host:
        # If host is provided, prepend https:// to make it a valid URL for parsing
        if not args.host.startswith(('http://', 'https://')):
            account_param = f"https://{args.host}"
        else:
            account_param = args.host
    else:
        account_param = args.account
    
    connection_params = {
        'account': account_param,
        'user': args.user,
        'authenticator': args.authenticator
    }
    
    if args.password:
        connection_params['password'] = args.password
    elif args.private_key_path:
        try:
            # Use secure private key reading function
            connection_params['private_key'] = _secure_read_private_key(args.private_key_path)
        except Exception as e:
            logging.error(f"Failed to read private key file: {e}")
            sys.exit(1)
        
        if args.private_key_passphrase:
            connection_params['private_key_passphrase'] = args.private_key_passphrase
    
    if args.warehouse:
        connection_params['warehouse'] = args.warehouse
    if args.database:
        connection_params['database'] = args.database
    if args.schema:
        connection_params['schema'] = args.schema
    if args.role:
        connection_params['role'] = args.role
    
    return SnowflakeConnection(**connection_params)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Create declarative application manifest from secure data share',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using account identifier
  snowflake-manifest-from-share --account myaccount.region.cloud --user myuser --password mypass --share MYSHARE

  # Using host (copy-paste from Snowflake account details)
  snowflake-manifest-from-share --host myaccount.region.cloud.snowflakecomputing.com --user myuser --password mypass --share MYSHARE

  # Using full Snowflake URL
  snowflake-manifest-from-share --account https://myaccount.snowflakecomputing.com --user myuser --password mypass --share MYSHARE

  # Using private key authentication
  snowflake-manifest-from-share --host myaccount.region.cloud.snowflakecomputing.com --user myuser --private-key-path /path/to/key.pem --share MYSHARE

  # With custom output file and warehouse
  snowflake-manifest-from-share --host myaccount.region.cloud.snowflakecomputing.com --user myuser --password mypass --share MYSHARE --output manifest.yml --warehouse COMPUTE_WH
        """
    )
    
    # Connection parameters
    parser.add_argument('--account',
                       help='Snowflake account identifier or full URL (e.g., https://myaccount.snowflakecomputing.com)')
    parser.add_argument('--host',
                       help='Snowflake host (e.g., myaccount.region.cloud.snowflakecomputing.com)')
    parser.add_argument('--user', required=True,
                       help='Snowflake username')
    parser.add_argument('--password',
                       help='Snowflake password (if using password auth)')
    parser.add_argument('--private-key-path',
                       help='Path to private key file (if using key-pair auth)')
    parser.add_argument('--private-key-passphrase',
                       help='Passphrase for private key')
    parser.add_argument('--authenticator', default='snowflake',
                       help='Authentication method (default: snowflake)')
    parser.add_argument('--warehouse',
                       help='Snowflake warehouse to use')
    parser.add_argument('--database',
                       help='Default database')
    parser.add_argument('--schema',
                       help='Default schema')
    parser.add_argument('--role',
                       help='Snowflake role to use')
    
    # Manifest generation parameters
    parser.add_argument('--share', required=True,
                       help='Name of the data share to generate manifest from')
    parser.add_argument('--output', '-o',
                       help='Output YAML file (default: print to stdout)')
    
    # Formatting options
    parser.add_argument('--indent', type=int, default=2,
                       help='YAML indentation (default: 2)')
    parser.add_argument('--no-sort-keys', action='store_true',
                       help='Do not sort dictionary keys in output')
    
    # Other options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate authentication parameters
    if not args.password and not args.private_key_path:
        logger.error("Must provide either --password or --private-key-path")
        sys.exit(1)
    
    try:
        # Create connection
        logger.info("Establishing connection to Snowflake...")
        connection = get_connection_from_args(args)
        
        # Create manifest generator
        generator = ShareManifestGenerator(connection)
        
        # Generate manifest
        logger.info(f"Generating manifest for share: {args.share}")
        manifest_result = generator.analyze_share(args.share)
        
        # Format results
        formatter = YAMLFormatter(
            indent=args.indent,
            sort_keys=not args.no_sort_keys
        )
        
        if args.output:
            # Save to file
            formatter.save_to_file(manifest_result, args.output)
            logger.info(f"Manifest generation complete. Results saved to: {args.output}")
        else:
            # Print to stdout
            yaml_output = formatter.format_manifest(manifest_result)
            print(yaml_output)
        
        # Close connection
        connection.close()
        
    except KeyboardInterrupt:
        logger.info("Manifest generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Manifest generation failed: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == '__main__':
    main()