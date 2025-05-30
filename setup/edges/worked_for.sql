-- Create WORKED_FOR edge table
-- Represents employment relationships between contacts (employees) and companies (employers)
-- Edge direction: CONTACT --[WORKED_FOR]--> COMPANY

USE DATABASE SANDBOX_NRILEY;
USE SCHEMA GRAPH_EDGES;

CREATE OR REPLACE TABLE WORKED_FOR (
    -- Primary key for the edge
    EDGE_ID STRING DEFAULT CONCAT('WORKED_FOR_', REPLACE(UUID_STRING(), '-', '')) PRIMARY KEY,
    
    -- Edge metadata
    EDGE_TYPE STRING DEFAULT 'WORKED_FOR' NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Source node: Contact (FROM)
    FROM_NODE_TYPE STRING DEFAULT 'CONTACT' NOT NULL,
    FROM_NODE_ID STRING NOT NULL,  -- References PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS.ID
    
    -- Target node: Company (TO)
    TO_NODE_TYPE STRING DEFAULT 'COMPANY' NOT NULL,
    TO_NODE_ID STRING NOT NULL,    -- References PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES.ID
    
    -- Relationship properties
    START_DATE DATE,               -- When employment started
    END_DATE DATE,                 -- When employment ended (NULL = current employment)
    JOB_TITLE STRING,             -- Optional: Job title/position
    DEPARTMENT STRING,            -- Optional: Department/division
    IS_CURRENT BOOLEAN,           -- Will be computed via trigger or application logic
    
    -- Data quality fields
    CONFIDENCE_SCORE FLOAT,       -- Optional: Confidence in this relationship (0.0-1.0)
    SOURCE_SYSTEM STRING          -- Where this data came from (e.g., 'HUBSPOT', 'LINKEDIN', 'MANUAL')
)
COMMENT = 'Edge table representing employment relationships between contacts and companies. Direction: CONTACT --[WORKED_FOR]--> COMPANY';

-- Note: Snowflake doesn't support CHECK constraints
-- Data validation should be handled at the application level:
-- - Ensure START_DATE <= END_DATE when both are provided
-- - Ensure CONFIDENCE_SCORE is between 0.0 and 1.0
-- - Ensure FROM_NODE_TYPE = 'CONTACT' and TO_NODE_TYPE = 'COMPANY'

-- Note: Snowflake doesn't support indexes on regular tables (only on hybrid tables)
-- Query performance is handled automatically by Snowflake's optimizer
-- Consider clustering keys for large tables if needed:
-- ALTER TABLE WORKED_FOR CLUSTER BY (FROM_NODE_ID, TO_NODE_ID);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE WORKED_FOR TO ROLE SYSADMIN;

-- Create a view that automatically computes IS_CURRENT for queries
CREATE OR REPLACE VIEW WORKED_FOR_CURRENT AS
SELECT 
    *,
    (END_DATE IS NULL) AS IS_CURRENT_COMPUTED
FROM WORKED_FOR;

-- Show table structure
DESCRIBE TABLE WORKED_FOR;