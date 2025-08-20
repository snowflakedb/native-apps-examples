"""
Snowflake connection handler.
"""

import snowflake.connector
from typing import Optional, Dict, Any, Union
import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def _secure_read_private_key(private_key_path: str) -> bytes:
    """
    Securely read private key file as bytes.
    
    Args:
        private_key_path: Path to private key file
        
    Returns:
        Private key content as bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If insufficient permissions
        ValueError: If file is empty or invalid
    """
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Private key file not found: {private_key_path}")
    
    # Check file permissions (should not be world-readable)
    file_stat = os.stat(private_key_path)
    if file_stat.st_mode & 0o077:  # Check if group/other have any permissions
        logger.warning(f"Private key file {private_key_path} has overly permissive permissions")
    
    try:
        with open(private_key_path, 'rb') as f:
            key_content = f.read()
        
        if not key_content:
            raise ValueError(f"Private key file is empty: {private_key_path}")
        
        return key_content
    except Exception as e:
        logger.error(f"Failed to read private key file {private_key_path}: {e}")
        raise


def _validate_credential_security(password: Optional[str], private_key: Optional[Union[str, bytes]]) -> None:
    """
    Validate credential security parameters.
    
    Args:
        password: Password string
        private_key: Private key content
        
    Raises:
        ValueError: If credentials are insecure
    """
    if password and private_key:
        raise ValueError("Cannot specify both password and private key authentication")
    
    if not password and not private_key:
        raise ValueError("Must specify either password or private key authentication")
    
    if password and len(password) < 8:
        logger.warning("Password is shorter than 8 characters, consider using a stronger password")


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
                 private_key: Optional[Union[str, bytes]] = None,
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
            private_key: Private key content as string or bytes (if using key-pair auth)
            private_key_passphrase: Passphrase for private key
            authenticator: Authentication method
            warehouse: Default warehouse
            database: Default database
            schema: Default schema
            role: Default role
        """
        # Validate credential security
        _validate_credential_security(password, private_key)
        
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
            # Ensure private key is in bytes format for security
            if isinstance(private_key, str):
                self.connection_params['private_key'] = private_key.encode('utf-8')
            else:
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