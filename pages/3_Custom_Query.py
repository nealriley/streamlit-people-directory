"""
Custom Query page - Execute custom SQL queries for advanced analysis
"""
import streamlit as st
from utils import execute_snowflake_query, display_table_info

st.set_page_config(
    page_title="Custom Query - People Card",
    page_icon="🔍",
    layout="wide"
)

def show_query_page():
    """Display the custom query page."""
    st.header("🔍 Custom Query")
    st.write("Execute custom SQL queries for advanced analysis and reporting")
    
    # Example queries
    with st.expander("📖 Example Queries"):
        st.markdown("""
        **Find all current employees at a company:**
        ```sql
        SELECT c.EMAIL, c.PROPERTIES_FIRSTNAME_VALUE, c.PROPERTIES_LASTNAME_VALUE, w.JOB_TITLE
        FROM PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS c
        JOIN SANDBOX_NRILEY.GRAPH_EDGES.WORKED_FOR w ON c.ID = w.FROM_NODE_ID
        WHERE w.TO_NODE_ID = 'company_id' AND w.IS_CURRENT = TRUE;
        ```
        
        **Find employment history for a person:**
        ```sql
        SELECT co.NAME, co.DOMAIN, w.START_DATE, w.END_DATE, w.JOB_TITLE
        FROM PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES co
        JOIN SANDBOX_NRILEY.GRAPH_EDGES.WORKED_FOR w ON co.ID = w.TO_NODE_ID
        WHERE w.FROM_NODE_ID = 'contact_id'
        ORDER BY w.START_DATE DESC;
        ```
        
        **Find reporting relationships:**
        ```sql
        SELECT 
            e.EMAIL as employee_email,
            m.EMAIL as manager_email,
            r.RELATIONSHIP_TYPE,
            r.START_DATE,
            r.END_DATE
        FROM SANDBOX_NRILEY.GRAPH_EDGES.REPORTED_TO r
        JOIN PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS e ON r.FROM_NODE_ID = e.ID
        JOIN PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS m ON r.TO_NODE_ID = m.ID
        WHERE r.IS_CURRENT = TRUE;
        ```
        """)

    # Query input
    query = st.text_area(
        "Enter your SQL query:",
        height=150,
        placeholder="SELECT * FROM PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES LIMIT 10;",
        help="Enter any valid SQL query to analyze the People Card data"
    )
    
    # Execute button
    if st.button("Execute Query", type="primary"):
        if not query.strip():
            st.error("Please enter a SQL query")
        else:
            with st.spinner("Executing query..."):
                df = execute_snowflake_query(query)
                
                if df is not None:
                    st.success(f"Query executed successfully! Returned {len(df)} rows.")
                    
                    # Display results
                    st.subheader("Query Results")
                    st.dataframe(df, use_container_width=True)
                    
                    # Show basic info about the results
                    if len(df) > 0:
                        display_table_info(df, "Query Results")

# Run the page
show_query_page()