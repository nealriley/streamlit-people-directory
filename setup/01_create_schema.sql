-- Create schema for graph edges in SANDBOX_NRILEY database
-- This schema will hold all relationship tables between companies and contacts

USE DATABASE SANDBOX_NRILEY;

-- Drop schema if it exists (for clean recreation)
DROP SCHEMA IF EXISTS GRAPH_EDGES;

-- Create the edges schema
CREATE SCHEMA GRAPH_EDGES
    COMMENT = 'Schema containing edge tables that represent relationships between companies and contacts in a graph structure';

-- Grant necessary permissions (adjust as needed for your environment)
GRANT USAGE ON SCHEMA GRAPH_EDGES TO ROLE SYSADMIN;
GRANT ALL ON SCHEMA GRAPH_EDGES TO ROLE SYSADMIN;

-- Confirm schema creation
SHOW SCHEMAS IN DATABASE SANDBOX_NRILEY;