"""
Core functionality for generating application manifests from Snowflake data shares.
"""

from typing import Dict, List, Any, Optional
import logging
import re
from .connection import SnowflakeConnection
from .yaml_formatter import EmptyValue, FlowStyleList

logger = logging.getLogger(__name__)


def _validate_identifier(identifier: str, context: str = "identifier") -> str:
    """
    Validate and sanitize Snowflake identifiers to prevent SQL injection.
    
    Args:
        identifier: The identifier to validate
        context: Context for error messages
        
    Returns:
        Validated identifier
        
    Raises:
        ValueError: If identifier is invalid
    """
    if not identifier or not isinstance(identifier, str):
        raise ValueError(f"Invalid {context}: must be a non-empty string")
    
    # Remove whitespace
    identifier = identifier.strip()
    
    # Check for SQL injection patterns
    dangerous_patterns = [
        r'[;\'"\\]',  # Semicolon, quotes, backslash
        r'\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|TRUNCATE)\b',  # SQL keywords
        r'--',  # SQL comments
        r'/\*',  # SQL block comments
        r'\bOR\b.*\b1\s*=\s*1\b',  # Common injection pattern
        r'\bUNION\b',  # Union attacks
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, identifier, re.IGNORECASE):
            raise ValueError(f"Invalid {context}: contains dangerous characters or keywords")
    
    # Validate against Snowflake identifier rules (simplified)
    # Allow alphanumeric, underscore, dot (for qualified names), and dollar sign
    if not re.match(r'^[A-Za-z0-9_.$-]+$', identifier):
        raise ValueError(f"Invalid {context}: contains invalid characters")
    
    # Length check (Snowflake max identifier length is 255)
    if len(identifier) > 255:
        raise ValueError(f"Invalid {context}: too long (max 255 characters)")
    
    return identifier


class ShareManifestGenerator:
    """Generates declarative application manifests from Snowflake data shares."""
    
    def __init__(self, connection: 'SnowflakeConnection'):
        """
        Initialize the manifest generator.
        
        Args:
            connection: SnowflakeConnection instance
        """
        self.connection = connection
    
    def analyze_share(self, share_name: str) -> Dict[str, Any]:
        """
        Generate application manifest from a data share.
        
        Args:
            share_name: Name of the data share to generate manifest from
            
        Returns:
            Dictionary containing application manifest data
        """
        logger.info(f"Starting manifest generation from data share: {share_name}")
        
        # Get all grants to the share
        grants = self._get_share_grants(share_name)
        
        # Get additional grants from database roles with role tracking
        role_grants, role_info = self._get_database_role_grants(grants)
        
        # Combine all grants (add role info to direct grants)
        direct_grants = [{'grant': g, 'role': None} for g in grants]
        all_grants = direct_grants + role_grants
        
        # Build the hierarchical structure with role mappings
        shared_content, role_mappings = self._build_shared_content_structure(all_grants)
        roles_section = self._build_roles_section(role_info)
        
        manifest_result = {
            'manifest_version': 2,
            'roles': roles_section,
            'shared_content': shared_content
        }
        
        logger.info(f"Completed manifest generation from data share: {share_name}")
        return manifest_result
    
    def _get_share_grants(self, share_name: str) -> List[Dict[str, Any]]:
        """Get all grants to the data share."""
        # Validate share name to prevent SQL injection
        validated_share_name = _validate_identifier(share_name, "share name")
        
        query = f"""
        SHOW GRANTS TO SHARE {validated_share_name}
        """
        
        try:
            results = self.connection.execute_query_dict(query)
            grants = []
            
            for result in results:
                grants.append({
                    'privilege': result.get('privilege'),
                    'granted_on': result.get('granted_on'),
                    'name': result.get('name')
                })
            
            return grants
        except Exception as e:
            logger.error(f"Error getting share grants: {e}")
            return []
    
    def _get_database_role_grants(self, grants: List[Dict[str, Any]]) -> tuple:
        """Get grants from database roles that are granted to the share."""
        role_grants = []
        role_info = {}
        
        # Find all database roles granted to the share
        database_roles = []
        for grant in grants:
            if (grant.get('granted_on') == 'DATABASE_ROLE' and 
                grant.get('privilege') == 'USAGE' and 
                grant.get('name')):
                database_roles.append(grant.get('name'))
        
        # For each database role, get its grants and info
        for role_name in database_roles:
            # Extract role name without database prefix
            if '.' in role_name:
                _, role_short_name = role_name.split('.', 1)
            else:
                role_short_name = role_name
            
            # Get role information
            role_info[role_short_name] = self._get_role_info(role_name)
            
            # Get role grants
            # Validate role name to prevent SQL injection
            validated_role_name = _validate_identifier(role_name, "database role name")
            
            query = f"""
            SHOW GRANTS TO DATABASE ROLE {validated_role_name}
            """
            
            try:
                logger.info(f"Getting grants for database role: {role_name}")
                results = self.connection.execute_query_dict(query)
                
                for result in results:
                    role_grants.append({
                        'grant': {
                            'privilege': result.get('privilege'),
                            'granted_on': result.get('granted_on'),
                            'name': result.get('name')
                        },
                        'role': role_short_name
                    })
            except Exception as e:
                logger.error(f"Error getting grants for database role {role_name}: {e}")
                continue
        
        return role_grants, role_info
    
    def _get_role_info(self, role_name: str) -> Dict[str, Any]:
        """Get information about a database role."""
        # Extract database name from role_name (e.g., DEMO_DB.DR1 -> DEMO_DB)
        if '.' in role_name:
            db_name, role_short_name = role_name.split('.', 1)
        else:
            return {}
        
        # Validate database name to prevent SQL injection
        validated_db_name = _validate_identifier(db_name, "database name")
        
        query = f"""
        SHOW DATABASE ROLES IN DATABASE {validated_db_name}
        """
        
        try:
            results = self.connection.execute_query_dict(query)
            for result in results:
                if result.get('name') == role_short_name:
                    comment = result.get('comment', '').strip()
                    if comment:
                        return {'comment': comment}
                    else:
                        return {}
            return {}
        except Exception as e:
            logger.error(f"Error getting role info for {role_name}: {e}")
            return {}
    
    def _build_roles_section(self, role_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build the roles section for the manifest."""
        roles = []
        for role_name, info in role_info.items():
            if info:  # Only add info if there's actual content
                roles.append({role_name: info})
            else:  # Empty info, just add the role name with empty value
                roles.append({role_name: EmptyValue()})
        return roles
    
    def _build_shared_content_structure(self, grants: List[Dict[str, Any]]) -> tuple:
        """Build the hierarchical shared content structure with role mappings."""
        databases = {}
        role_mappings = {
            'databases': {},
            'schemas': {},
            'tables': {},
            'views': {}
        }
        
        # First pass: collect databases with USAGE privilege
        for grant_data in grants:
            grant = grant_data['grant']
            role = grant_data['role']
            
            if (grant.get('granted_on') == 'DATABASE' and 
                grant.get('privilege') == 'USAGE' and 
                grant.get('name')):
                db_name = grant.get('name')
                if db_name not in databases:
                    databases[db_name] = {'schemas': {}}
                    role_mappings['databases'][db_name] = set()
                
                if role:
                    role_mappings['databases'][db_name].add(role)
            
            elif (grant.get('granted_on') == 'DATABASE_ROLE' and 
                  grant.get('privilege') == 'USAGE' and 
                  grant.get('name')):
                full_name = grant.get('name')
                if '.' in full_name:
                    db_name = full_name.split('.')[0]
                    if db_name not in databases:
                        databases[db_name] = {'schemas': {}}
                        role_mappings['databases'][db_name] = set()
                    # The role being granted to the share provides access to this database
                    if role is None:  # This is a direct grant to the share
                        role_name = full_name.split('.', 1)[1]
                        role_mappings['databases'][db_name].add(role_name)
        
        # Second pass: collect schemas with USAGE privilege
        for grant_data in grants:
            grant = grant_data['grant']
            role = grant_data['role']
            
            if (grant.get('granted_on') == 'SCHEMA' and 
                grant.get('privilege') == 'USAGE' and 
                grant.get('name')):
                full_name = grant.get('name')
                if '.' in full_name:
                    db_name, schema_name = full_name.split('.', 1)
                    if db_name in databases:
                        schema_key = f"{db_name}.{schema_name}"
                        if schema_name not in databases[db_name]['schemas']:
                            databases[db_name]['schemas'][schema_name] = {
                                'tables': {},
                                'views': {}
                            }
                            role_mappings['schemas'][schema_key] = set()
                        
                        if role:
                            role_mappings['schemas'][schema_key].add(role)
        
        # Third pass: collect tables and views with SELECT privilege
        for grant_data in grants:
            grant = grant_data['grant']
            role = grant_data['role']
            
            if (grant.get('privilege') == 'SELECT' and grant.get('name')):
                granted_on = grant.get('granted_on')
                full_name = grant.get('name')
                
                if granted_on in ['TABLE', 'VIEW'] and full_name.count('.') >= 2:
                    parts = full_name.split('.')
                    db_name = parts[0]
                    schema_name = parts[1]
                    object_name = '.'.join(parts[2:])  # Handle names with dots
                    object_key = f"{db_name}.{schema_name}.{object_name}"
                    
                    if (db_name in databases and 
                        schema_name in databases[db_name]['schemas']):
                        if granted_on == 'TABLE':
                            if object_name not in databases[db_name]['schemas'][schema_name]['tables']:
                                databases[db_name]['schemas'][schema_name]['tables'][object_name] = set()
                                role_mappings['tables'][object_key] = set()
                            
                            if role:
                                databases[db_name]['schemas'][schema_name]['tables'][object_name].add(role)
                                role_mappings['tables'][object_key].add(role)
                                
                        elif granted_on == 'VIEW':
                            if object_name not in databases[db_name]['schemas'][schema_name]['views']:
                                databases[db_name]['schemas'][schema_name]['views'][object_name] = set()
                                role_mappings['views'][object_key] = set()
                            
                            if role:
                                databases[db_name]['schemas'][schema_name]['views'][object_name].add(role)
                                role_mappings['views'][object_key].add(role)
        
        # Convert to the required list format with roles
        database_list = []
        for db_name, db_content in databases.items():
            schema_list = []
            db_roles = list(role_mappings['databases'].get(db_name, set()))
            
            for schema_name, schema_content in db_content['schemas'].items():
                schema_key = f"{db_name}.{schema_name}"
                schema_roles = list(role_mappings['schemas'].get(schema_key, set()))
                
                schema_dict = {schema_name: {}}
                
                # Add roles only if there are any
                if schema_roles:
                    schema_dict[schema_name]['roles'] = FlowStyleList(schema_roles)
                
                # Add tables with roles
                if schema_content['tables']:
                    table_list = []
                    for table_name, table_roles in schema_content['tables'].items():
                        table_role_list = list(table_roles)
                        if table_role_list:
                            table_item = {table_name: {'roles': FlowStyleList(table_role_list)}}
                        else:
                            table_item = {table_name: EmptyValue()}
                        table_list.append(table_item)
                    schema_dict[schema_name]['tables'] = table_list
                
                # Add views with roles
                if schema_content['views']:
                    view_list = []
                    for view_name, view_roles in schema_content['views'].items():
                        view_role_list = list(view_roles)
                        if view_role_list:
                            view_item = {view_name: {'roles': FlowStyleList(view_role_list)}}
                        else:
                            view_item = {view_name: EmptyValue()}
                        view_list.append(view_item)
                    schema_dict[schema_name]['views'] = view_list
                
                schema_list.append(schema_dict)
            
            db_dict = {db_name: {}}
            
            # Add database roles if there are any
            if db_roles:
                db_dict[db_name]['roles'] = FlowStyleList(db_roles)
                
            db_dict[db_name]['schemas'] = schema_list
            database_list.append(db_dict)
        
        return {'databases': database_list}, role_mappings
