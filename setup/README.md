# Graph Database Setup for HubSpot CRM

This folder contains SQL scripts to set up a graph-like data structure in Snowflake for representing relationships between companies and contacts from your HubSpot CRM data.

## Architecture Overview

### Nodes
- **Companies**: `PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES` (existing)
- **Contacts**: `PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS` (existing)

### Edges
- **WORKED_FOR**: Employment relationships between contacts and companies
- *(Future edges can be added as needed)*

## Setup Instructions

### 1. Create Schema
Run the schema creation script first:
```sql
-- Copy and paste content from: 01_create_schema.sql
```

### 2. Create Edge Tables
Create each edge table by running the scripts in the `edges/` folder:

#### WORKED_FOR Edge
```sql
-- Copy and paste content from: edges/worked_for.sql
```

#### REPORTED_TO Edge
```sql
-- Copy and paste content from: edges/reported_to.sql
```

## Edge Table Structure

### WORKED_FOR Table
Represents employment relationships: `CONTACT --[WORKED_FOR]--> COMPANY`

**Key Fields:**
- `FROM_NODE_ID`: Contact ID (references `CONTACTS.ID`)
- `TO_NODE_ID`: Company ID (references `COMPANIES.ID`)
- `START_DATE`: Employment start date
- `END_DATE`: Employment end date (NULL = current)
- `IS_CURRENT`: Auto-computed field (TRUE when END_DATE is NULL)
- `JOB_TITLE`: Optional job title
- `DEPARTMENT`: Optional department

**Example Usage:**
```sql
-- Insert a current employment relationship
INSERT INTO SANDBOX_NRILEY.GRAPH_EDGES.WORKED_FOR (
    FROM_NODE_ID, TO_NODE_ID, START_DATE, JOB_TITLE, SOURCE_SYSTEM
) VALUES (
    'contact_123', 'company_456', '2023-01-15', 'Software Engineer', 'HUBSPOT'
);

-- Find all current employees of a company
SELECT * FROM WORKED_FOR 
WHERE TO_NODE_ID = 'company_456' AND IS_CURRENT = TRUE;

-- Find employment history for a contact
SELECT * FROM WORKED_FOR 
WHERE FROM_NODE_ID = 'contact_123' 
ORDER BY START_DATE DESC;
```

### REPORTED_TO Table
Represents reporting relationships: `CONTACT --[REPORTED_TO]--> CONTACT`

**Key Fields:**
- `FROM_NODE_ID`: Employee Contact ID (references `CONTACTS.ID`)
- `TO_NODE_ID`: Manager Contact ID (references `CONTACTS.ID`)
- `START_DATE`: Reporting relationship start date
- `END_DATE`: Reporting relationship end date (NULL = current)
- `IS_CURRENT`: Whether this is a current reporting relationship
- `RELATIONSHIP_TYPE`: Type of reporting (e.g., 'DIRECT_REPORT', 'DOTTED_LINE', 'MATRIX')

**Example Usage:**
```sql
-- Insert a current reporting relationship
INSERT INTO SANDBOX_NRILEY.GRAPH_EDGES.REPORTED_TO (
    FROM_NODE_ID, TO_NODE_ID, START_DATE, RELATIONSHIP_TYPE, IS_CURRENT, SOURCE_SYSTEM
) VALUES (
    'employee_123', 'manager_456', '2023-01-15', 'DIRECT_REPORT', TRUE, 'MANUAL'
);

-- Find all direct reports for a manager
SELECT * FROM REPORTED_TO 
WHERE TO_NODE_ID = 'manager_456' AND IS_CURRENT = TRUE;

-- Find reporting history for an employee
SELECT * FROM REPORTED_TO 
WHERE FROM_NODE_ID = 'employee_123' 
ORDER BY START_DATE DESC;
```

## Future Edge Types

You can extend this structure by creating additional edge tables for other relationships:
- `FOUNDED_BY`: Contact founded Company
- `INVESTED_IN`: Company invested in Company
- `PARTNERED_WITH`: Company partnered with Company
- `REFERRED_BY`: Contact referred by Contact

Each edge table should follow the same pattern:
- `EDGE_ID`: Unique identifier
- `FROM_NODE_TYPE` & `FROM_NODE_ID`: Source node
- `TO_NODE_TYPE` & `TO_NODE_ID`: Target node
- Relationship-specific properties
- Metadata fields (created_at, source_system, etc.)

## Data Quality

The edge tables include several data quality features:
- **Constraints**: Validate date ranges and confidence scores
- **Indexes**: Optimize query performance
- **Computed Columns**: Auto-calculate derived fields
- **Source Tracking**: Track where data originated
- **Confidence Scoring**: Rate relationship reliability (0.0-1.0)