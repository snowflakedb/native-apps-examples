"""
Snowflake connection handler.
"""

import snowflake.connector
from typing import Optional, Dict, Any
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SnowflakeConnection:
    """Handles Snowflake database connections and query execution."""
    
    @staticmethod
    def _parse_account_from_url(account_or_url: str) -> str:
        """
        Parse account identifier from URL or return as-is if already an account identifier.
        
        Args:
            account_or_url: Either a full Snowflake URL or account identifier
            
        Returns:
            Account identifier suitable for snowflake-connector-python
            
        Examples:
            https://myaccount.snowflakecomputing.com -> myaccount
            https://myaccount.region.cloud.snowflakecomputing.com -> myaccount.region.cloud
            myaccount.region.cloud -> myaccount.region.cloud (unchanged)
        """
        if account_or_url.startswith(('http://', 'https://')):
            parsed = urlparse(account_or_url)
            hostname = parsed.hostname
            if hostname and hostname.endswith('.snowflakecomputing.com'):
                # Remove .snowflakecomputing.com suffix
                return hostname[:-len('.snowflakecomputing.com')]
            else:
                return hostname or account_or_url
        else:
            # Already an account identifier
            return account_or_url
    
    def __init__(self, 
                 account: str,
                 user: str,
                 password: Optional[str] = None,
                 private_key: Optional[str] = None,
                 private_key_passphrase: Optional[str] = None,
                 authenticator: str = 'snowflake',
                 warehouse: Optional[str] = None,
                 database: Optional[str] = None,
                 schema: Optional[str] = None,
                 role: Optional[str] = None):
        """
        Initialize Snowflake connection parameters.
        
        Args:
            account: Snowflake account identifier or full URL
            user: Username for authentication
            password: Password (if using password auth)
            private_key: Private key for key-pair authentication
            private_key_passphrase: Passphrase for private key
            authenticator: Authentication method
            warehouse: Default warehouse
            database: Default database
            schema: Default schema
            role: Default role
        """
        # Parse account from URL if needed
        parsed_account = self._parse_account_from_url(account)
        
        self.connection_params = {
            'account': parsed_account,
            'user': user,
            'authenticator': authenticator
        }
        
        if password:
            self.connection_params['password'] = password
        
        if private_key:
            self.connection_params['private_key'] = private_key
        
        if private_key_passphrase:
            self.connection_params['private_key_passphrase'] = private_key_passphrase
            
        if warehouse:
            self.connection_params['warehouse'] = warehouse
            
        if database:
            self.connection_params['database'] = database
            
        if schema:
            self.connection_params['schema'] = schema
            
        if role:
            self.connection_params['role'] = role
            
        self._connection = None
    
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Establish connection to Snowflake."""
        try:
            self._connection = snowflake.connector.connect(**self.connection_params)
            logger.info("Successfully connected to Snowflake")
            return self._connection
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise
    
    def execute_query(self, query: str) -> list:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of query results
        """
        if not self._connection:
            self.connect()
            
        try:
            cursor = self._connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_query_dict(self, query: str) -> list:
        """
        Execute a query and return results as dictionaries.
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of dictionaries with column names as keys
        """
        if not self._connection:
            self.connect()
            
        try:
            cursor = self._connection.cursor(snowflake.connector.DictCursor)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def close(self):
        """Close the Snowflake connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Snowflake connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()