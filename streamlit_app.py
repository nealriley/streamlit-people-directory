import os
import hashlib

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="HubSpot CRM Data Explorer",
    page_icon="❄️",
    layout="wide"
)



################################################################
# Authentication Functions

def check_password():
    """Returns True if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        app_password = "hello"
        if not app_password:
            st.error("No password configured. Set STREAMLIT_PASSWORD environment variable.")
            return
            
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == hashlib.sha256(app_password.encode()).hexdigest():
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password
    st.markdown("### 🔐 Login Required")
    st.text_input(
        "Password", 
        type="password", 
        on_change=password_entered, 
        key="password",
        help="Enter the application password to continue"
    )
    
    if "password_correct" in st.session_state:
        if not st.session_state["password_correct"]:
            st.error("😕 Password incorrect")
    
    return False


################################################################
# Functions


@st.cache_data
def execute_snowflake_query(query):
    """Execute a query against Snowflake and return results."""
    try:
        conn = st.connection("snowflake", type="snowflake")
        df = conn.query(query, ttl=300)  # Cache for 5 minutes
        return df
    except Exception as e:
        st.error(f"Failed to execute query: {str(e)}")
        st.info("Please check your connection configuration in .streamlit/secrets.toml")
        return None


@st.cache_data
def get_companies_data(limit=100, object_id=None):
    """Get companies data from HubSpot CRM."""
    if object_id:
        query = f"""
        SELECT *
        FROM PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES
        WHERE ID = '{object_id}'
        """
    else:
        query = f"""
        SELECT *
        FROM PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES
        LIMIT {limit}
        """
    return execute_snowflake_query(query)


@st.cache_data
def get_contacts_data(limit=100, object_id=None):
    """Get contacts data from HubSpot CRM."""
    if object_id:
        query = f"""
        SELECT *
        FROM PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS
        WHERE ID = '{object_id}'
        """
    else:
        query = f"""
        SELECT *
        FROM PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS
        LIMIT {limit}
        """
    return execute_snowflake_query(query)


def display_table_info(df, table_name):
    """Display basic information about a table."""
    if df is not None and len(df) > 0:
        st.success(f"Loaded {len(df)} rows from {table_name}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", len(df))
            st.metric("Columns", len(df.columns))
        with col2:
            st.write("**Column Names:**")
            st.write(list(df.columns))
            
        with st.expander("Column Data Types"):
            st.write(df.dtypes.to_frame("Data Type"))
    else:
        st.error(f"No data found for {table_name}")


################################################################
# Page Functions

def show_companies_page():
    """Display the Companies page."""
    st.header("🏢 Companies")
    st.write("Data from PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES")
    
    # Check for query parameter
    query_params = st.query_params
    object_id = query_params.get("id")
    
    if object_id:
        st.info(f"🔍 Filtering by HS_OBJECT_ID: {object_id}")
        # Auto-execute query for specific ID
        with st.spinner("Loading company data..."):
            df = get_companies_data(object_id=object_id)
            if df is not None:
                st.session_state.companies_df = df
    else:
        # Controls for general browsing
        col1, col2 = st.columns([1, 3])
        with col1:
            limit = st.number_input("Rows to load", min_value=10, max_value=1000, value=100, step=10)
        with col2:
            if st.button("Load Companies Data", type="primary"):
                with st.spinner("Loading companies data..."):
                    df = get_companies_data(limit)
                    if df is not None:
                        st.session_state.companies_df = df
    
    # Display data if available
    if 'companies_df' in st.session_state:
        df = st.session_state.companies_df
        display_table_info(df, "Companies")
        
        st.subheader("Companies Data")
        st.dataframe(df, use_container_width=True)


def show_contacts_page():
    """Display the Contacts page."""
    st.header("👥 Contacts")
    st.write("Data from PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS")
    
    # Check for query parameter
    query_params = st.query_params
    object_id = query_params.get("id")
    
    if object_id:
        st.info(f"🔍 Filtering by HS_OBJECT_ID: {object_id}")
        # Auto-execute query for specific ID
        with st.spinner("Loading contact data..."):
            df = get_contacts_data(object_id=object_id)
            if df is not None:
                st.session_state.contacts_df = df
    else:
        # Controls for general browsing
        col1, col2 = st.columns([1, 3])
        with col1:
            limit = st.number_input("Rows to load", min_value=10, max_value=1000, value=100, step=10)
        with col2:
            if st.button("Load Contacts Data", type="primary"):
                with st.spinner("Loading contacts data..."):
                    df = get_contacts_data(limit)
                    if df is not None:
                        st.session_state.contacts_df = df
    
    # Display data if available
    if 'contacts_df' in st.session_state:
        df = st.session_state.contacts_df
        display_table_info(df, "Contacts")
        
        st.subheader("Contacts Data")
        st.dataframe(df, use_container_width=True)


def show_query_page():
    """Display the custom query page."""
    st.header("🔍 Custom Query")
    st.write("Execute custom SQL queries against your Snowflake database")
    
    # Query input
    query = st.text_area(
        "Enter your SQL query:",
        height=150,
        placeholder="SELECT * FROM PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES LIMIT 10;",
        help="Enter any valid SQL query to execute against your Snowflake database"
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


################################################################
# Application logic

"""
# ❄️ HubSpot CRM Data Explorer

Explore your HubSpot CRM data with dedicated pages for Companies and Contacts.
"""

# Check authentication first
if not check_password():
    st.stop()

st.info("💡 **Setup Required**: Create `.streamlit/secrets.toml` with your Snowflake connection details")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Companies", "Contacts", "Custom Query"],
    help="Select which data to explore"
)

# Display selected page
if page == "Companies":
    show_companies_page()
elif page == "Contacts":
    show_contacts_page()
elif page == "Custom Query":
    show_query_page()
