-- Create REPORTED_TO edge table
-- Represents reporting relationships between contacts (employees)
-- Edge direction: CONTACT --[REPORTED_TO]--> CONTACT

USE DATABASE SANDBOX_NRILEY;
USE SCHEMA GRAPH_EDGES;

CREATE OR REPLACE TABLE REPORTED_TO (
    -- Primary key for the edge
    EDGE_ID STRING DEFAULT CONCAT('REPORTED_TO_', REPLACE(UUID_STRING(), '-', '')) PRIMARY KEY,
    
    -- Edge metadata
    EDGE_TYPE STRING DEFAULT 'REPORTED_TO' NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Source node: Contact (FROM) - the person reporting
    FROM_NODE_TYPE STRING DEFAULT 'CONTACT' NOT NULL,
    FROM_NODE_ID STRING NOT NULL,  -- References PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS.ID
    
    -- Target node: Contact (TO) - the manager/supervisor
    TO_NODE_TYPE STRING DEFAULT 'CONTACT' NOT NULL,
    TO_NODE_ID STRING NOT NULL,    -- References PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS.ID
    
    -- Relationship properties
    START_DATE DATE,               -- When reporting relationship started
    END_DATE DATE,                 -- When reporting relationship ended (NULL = current)
    RELATIONSHIP_TYPE STRING,      -- e.g., 'DIRECT_REPORT', 'DOTTED_LINE', 'MATRIX'
    IS_CURRENT BOOLEAN,           -- Whether this is a current reporting relationship
    
    -- Data quality fields
    CONFIDENCE_SCORE FLOAT,       -- Optional: Confidence in this relationship (0.0-1.0)
    SOURCE_SYSTEM STRING          -- Where this data came from (e.g., 'HUBSPOT', 'HRIS', 'MANUAL')
)
COMMENT = 'Edge table representing reporting relationships between contacts. Direction: CONTACT --[REPORTED_TO]--> CONTACT (employee reports to manager)';

-- Note: Snowflake doesn't support CHECK constraints
-- Data validation should be handled at the application level:
-- - Ensure START_DATE <= END_DATE when both are provided
-- - Ensure CONFIDENCE_SCORE is between 0.0 and 1.0
-- - Ensure FROM_NODE_TYPE = 'CONTACT' and TO_NODE_TYPE = 'CONTACT'
-- - Prevent self-reporting (FROM_NODE_ID != TO_NODE_ID)

-- Note: Snowflake doesn't support indexes on regular tables (only on hybrid tables)
-- Query performance is handled automatically by Snowflake's optimizer
-- Consider clustering keys for large tables if needed:
-- ALTER TABLE REPORTED_TO CLUSTER BY (FROM_NODE_ID, TO_NODE_ID);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE REPORTED_TO TO ROLE SYSADMIN;

-- Create a view that automatically computes IS_CURRENT for queries
CREATE OR REPLACE VIEW REPORTED_TO_CURRENT AS
SELECT 
    *,
    (END_DATE IS NULL) AS IS_CURRENT_COMPUTED
FROM REPORTED_TO;

-- Show table structure
DESCRIBE TABLE REPORTED_TO;