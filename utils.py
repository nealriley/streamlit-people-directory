"""
Shared utility functions for the HubSpot CRM Data Explorer
"""
import streamlit as st
import pandas as pd


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


@st.cache_data
def get_worked_for_relationships(from_node_id=None, to_node_id=None):
    """Get WORKED_FOR relationships."""
    where_clause = []
    if from_node_id:
        where_clause.append(f"FROM_NODE_ID = '{from_node_id}'")
    if to_node_id:
        where_clause.append(f"TO_NODE_ID = '{to_node_id}'")
    
    where_sql = " WHERE " + " AND ".join(where_clause) if where_clause else ""
    
    query = f"""
    SELECT *
    FROM SANDBOX_NRILEY.GRAPH_EDGES.WORKED_FOR
    {where_sql}
    ORDER BY START_DATE DESC
    """
    return execute_snowflake_query(query)


@st.cache_data
def get_reported_to_relationships(from_node_id=None, to_node_id=None):
    """Get REPORTED_TO relationships."""
    where_clause = []
    if from_node_id:
        where_clause.append(f"FROM_NODE_ID = '{from_node_id}'")
    if to_node_id:
        where_clause.append(f"TO_NODE_ID = '{to_node_id}'")
    
    where_sql = " WHERE " + " AND ".join(where_clause) if where_clause else ""
    
    query = f"""
    SELECT *
    FROM SANDBOX_NRILEY.GRAPH_EDGES.REPORTED_TO
    {where_sql}
    ORDER BY START_DATE DESC
    """
    return execute_snowflake_query(query)


@st.cache_data
def search_companies_by_domain(domain_search):
    """Search companies by domain."""
    query = f"""
    SELECT ID, DOMAIN, NAME
    FROM PROD_HUBSPOT.HUBSPOT_CRM.COMPANIES
    WHERE DOMAIN ILIKE '%{domain_search}%'
    LIMIT 20
    """
    return execute_snowflake_query(query)


@st.cache_data
def search_contacts_by_email(email_search):
    """Search contacts by email."""
    query = f"""
    SELECT ID, EMAIL, PROPERTIES_FIRSTNAME_VALUE, PROPERTIES_LASTNAME_VALUE
    FROM PROD_HUBSPOT.HUBSPOT_CRM.CONTACTS
    WHERE EMAIL ILIKE '%{email_search}%'
    LIMIT 20
    """
    return execute_snowflake_query(query)


def insert_worked_for_relationship(from_node_id, to_node_id, start_date, end_date=None, job_title=None, department=None):
    """Insert a new WORKED_FOR relationship."""
    # Construct values for optional fields
    end_date_val = f"'{end_date}'" if end_date else "NULL"
    job_title_val = f"'{job_title}'" if job_title else "NULL"
    department_val = f"'{department}'" if department else "NULL"
    is_current = "TRUE" if end_date is None else "FALSE"
    
    query = f"""
    INSERT INTO SANDBOX_NRILEY.GRAPH_EDGES.WORKED_FOR (
        FROM_NODE_ID, TO_NODE_ID, START_DATE, END_DATE, JOB_TITLE, DEPARTMENT, IS_CURRENT, SOURCE_SYSTEM
    ) VALUES (
        '{from_node_id}', '{to_node_id}', '{start_date}', {end_date_val}, {job_title_val}, {department_val}, {is_current}, 'MANUAL'
    )
    """
    return execute_snowflake_query(query)


def insert_reported_to_relationship(from_node_id, to_node_id, start_date, end_date=None, relationship_type=None):
    """Insert a new REPORTED_TO relationship."""
    # Construct values for optional fields
    end_date_val = f"'{end_date}'" if end_date else "NULL"
    relationship_type_val = f"'{relationship_type}'" if relationship_type else "NULL"
    is_current = "TRUE" if end_date is None else "FALSE"
    
    query = f"""
    INSERT INTO SANDBOX_NRILEY.GRAPH_EDGES.REPORTED_TO (
        FROM_NODE_ID, TO_NODE_ID, START_DATE, END_DATE, RELATIONSHIP_TYPE, IS_CURRENT, SOURCE_SYSTEM
    ) VALUES (
        '{from_node_id}', '{to_node_id}', '{start_date}', {end_date_val}, {relationship_type_val}, {is_current}, 'MANUAL'
    )
    """
    return execute_snowflake_query(query)


def delete_worked_for_relationship(edge_id):
    """Delete a WORKED_FOR relationship."""
    query = f"""
    DELETE FROM SANDBOX_NRILEY.GRAPH_EDGES.WORKED_FOR
    WHERE EDGE_ID = '{edge_id}'
    """
    return execute_snowflake_query(query)


def delete_reported_to_relationship(edge_id):
    """Delete a REPORTED_TO relationship."""
    query = f"""
    DELETE FROM SANDBOX_NRILEY.GRAPH_EDGES.REPORTED_TO
    WHERE EDGE_ID = '{edge_id}'
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


def show_worked_for_form(from_node_id, form_key="worked_for_form"):
    """Show form to add WORKED_FOR relationship (Contact -> Company)."""
    with st.form(form_key):
        st.write("**Add Employment Relationship (Contact -> Company):**")
        
        # Search for company
        company_search = st.text_input("Search Company by Domain", placeholder="example.com")
        
        target_id = None
        if company_search:
            companies_df = search_companies_by_domain(company_search)
            if companies_df is not None and len(companies_df) > 0:
                company_options = {f"{row['NAME']} ({row['DOMAIN']})": row['ID'] for _, row in companies_df.iterrows()}
                selected_company = st.selectbox("Select Company", options=list(company_options.keys()))
                target_id = company_options.get(selected_company)
            else:
                st.warning("No companies found")
        
        # Employment details
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date (leave empty if current)", value=None)
        
        job_title = st.text_input("Job Title (optional)")
        department = st.text_input("Department (optional)")
        
        submitted = st.form_submit_button("Add Employment Relationship")
        
        if submitted and target_id:
            insert_worked_for_relationship(
                from_node_id=from_node_id,
                to_node_id=target_id,
                start_date=start_date,
                end_date=end_date,
                job_title=job_title if job_title else None,
                department=department if department else None
            )
            st.success("Employment relationship added!")
            st.rerun()
        elif submitted:
            st.error("Please select a company")


def show_reported_to_form(from_node_id, form_key="reported_to_form"):
    """Show form to add REPORTED_TO relationship (Contact -> Contact)."""
    with st.form(form_key):
        st.write("**Add Reporting Relationship (Employee -> Manager):**")
        
        # Search for contact (manager)
        contact_search = st.text_input("Search Manager by Email", placeholder="manager@example.com")
        
        target_id = None
        if contact_search:
            contacts_df = search_contacts_by_email(contact_search)
            if contacts_df is not None and len(contacts_df) > 0:
                contact_options = {}
                for _, row in contacts_df.iterrows():
                    first_name = row.get('PROPERTIES_FIRSTNAME_VALUE', '')
                    last_name = row.get('PROPERTIES_LASTNAME_VALUE', '')
                    name = f"{first_name} {last_name}".strip()
                    if not name:
                        name = f"ID: {row['ID']}"
                    display_text = f"{name} ({row['EMAIL']})"
                    contact_options[display_text] = row['ID']
                
                selected_contact = st.selectbox("Select Manager", options=list(contact_options.keys()))
                target_id = contact_options.get(selected_contact)
            else:
                st.warning("No contacts found")
        
        # Reporting details
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date (leave empty if current)", value=None)
        
        reporting_type = st.selectbox(
            "Reporting Type",
            options=["DIRECT_REPORT", "DOTTED_LINE", "MATRIX"],
            help="Type of reporting relationship"
        )
        
        submitted = st.form_submit_button("Add Reporting Relationship")
        
        if submitted and target_id:
            if target_id == from_node_id:
                st.error("A contact cannot report to themselves!")
            else:
                insert_reported_to_relationship(
                    from_node_id=from_node_id,
                    to_node_id=target_id,
                    start_date=start_date,
                    end_date=end_date,
                    relationship_type=reporting_type
                )
                st.success("Reporting relationship added!")
                st.rerun()
        elif submitted:
            st.error("Please select a manager")


def show_employee_form(company_id, form_key="employee_form"):
    """Show form to add employee relationship (Contact -> Company)."""
    with st.form(form_key):
        st.write("**Add Employee (Contact -> Company):**")
        
        # Search for contact
        contact_search = st.text_input("Search Contact by Email", placeholder="john@example.com")
        
        from_node_id = None
        if contact_search:
            contacts_df = search_contacts_by_email(contact_search)
            if contacts_df is not None and len(contacts_df) > 0:
                contact_options = {}
                for _, row in contacts_df.iterrows():
                    first_name = row.get('PROPERTIES_FIRSTNAME_VALUE', '')
                    last_name = row.get('PROPERTIES_LASTNAME_VALUE', '')
                    name = f"{first_name} {last_name}".strip()
                    if not name:
                        name = f"ID: {row['ID']}"
                    display_text = f"{name} ({row['EMAIL']})"
                    contact_options[display_text] = row['ID']
                
                selected_contact = st.selectbox("Select Contact", options=list(contact_options.keys()))
                from_node_id = contact_options.get(selected_contact)
            else:
                st.warning("No contacts found")
        
        # Employment details
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date (leave empty if current)", value=None)
        
        job_title = st.text_input("Job Title (optional)")
        department = st.text_input("Department (optional)")
        
        submitted = st.form_submit_button("Add Employee")
        
        if submitted and from_node_id:
            insert_worked_for_relationship(
                from_node_id=from_node_id,
                to_node_id=company_id,
                start_date=start_date,
                end_date=end_date,
                job_title=job_title if job_title else None,
                department=department if department else None
            )
            st.success("Employee relationship added!")
            st.rerun()
        elif submitted:
            st.error("Please select a contact")


def show_relationship_management_for_contact(contact_id):
    """Show relationship management UI for a contact (FROM node)."""
    st.subheader("🔗 Relationships")
    st.write("Manage relationships for this contact")
    
    # Load existing relationships
    worked_for_df = get_worked_for_relationships(from_node_id=contact_id)
    reported_to_df = get_reported_to_relationships(from_node_id=contact_id)
    
    # Display WORKED_FOR relationships
    st.write("**🏢 Employment History (Companies worked for):**")
    if worked_for_df is not None and len(worked_for_df) > 0:
        for _, rel in worked_for_df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                current_text = " (Current)" if rel.get('IS_CURRENT') else ""
                date_range = f"{rel.get('START_DATE', 'Unknown')} - {rel.get('END_DATE', 'Present')}"
                job_info = f" as {rel.get('JOB_TITLE', 'Unknown Role')}" if rel.get('JOB_TITLE') else ""
                st.write(f"**Company ID:** {rel.get('TO_NODE_ID')} | {date_range}{job_info}{current_text}")
            with col2:
                if st.button("Edit", key=f"edit_worked_{rel.get('EDGE_ID')}"):
                    st.info("Edit functionality - coming soon")
            with col3:
                if st.button("Delete", key=f"delete_worked_{rel.get('EDGE_ID')}", type="secondary"):
                    delete_worked_for_relationship(rel.get('EDGE_ID'))
                    st.success("Relationship deleted!")
                    st.rerun()
    else:
        st.info("No employment relationships found")
    
    # Display REPORTED_TO relationships
    st.write("**👥 Reporting Relationships (Managers reported to):**")
    if reported_to_df is not None and len(reported_to_df) > 0:
        for _, rel in reported_to_df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                current_text = " (Current)" if rel.get('IS_CURRENT') else ""
                date_range = f"{rel.get('START_DATE', 'Unknown')} - {rel.get('END_DATE', 'Present')}"
                rel_type = f" ({rel.get('RELATIONSHIP_TYPE', 'Unknown Type')})" if rel.get('RELATIONSHIP_TYPE') else ""
                st.write(f"**Manager ID:** {rel.get('TO_NODE_ID')} | {date_range}{rel_type}{current_text}")
            with col2:
                if st.button("Edit", key=f"edit_report_{rel.get('EDGE_ID')}"):
                    st.info("Edit functionality - coming soon")
            with col3:
                if st.button("Delete", key=f"delete_report_{rel.get('EDGE_ID')}", type="secondary"):
                    delete_reported_to_relationship(rel.get('EDGE_ID'))
                    st.success("Relationship deleted!")
                    st.rerun()
    else:
        st.info("No reporting relationships found")
    
    # Add new relationship buttons
    st.write("**Add New Relationships:**")
    
    # Initialize session state for form display
    if 'show_worked_for_form' not in st.session_state:
        st.session_state.show_worked_for_form = False
    if 'show_reported_to_form' not in st.session_state:
        st.session_state.show_reported_to_form = False
    
    # Buttons for each relationship type available to contacts
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏢 Add Employment (WORKED_FOR)", key="btn_worked_for", use_container_width=True):
            st.session_state.show_worked_for_form = not st.session_state.show_worked_for_form
            st.session_state.show_reported_to_form = False
            st.rerun()
    
    with col2:
        if st.button("👥 Add Reporting (REPORTED_TO)", key="btn_reported_to", use_container_width=True):
            st.session_state.show_reported_to_form = not st.session_state.show_reported_to_form
            st.session_state.show_worked_for_form = False
            st.rerun()
    
    # Show forms based on button clicks
    if st.session_state.show_worked_for_form:
        show_worked_for_form(contact_id, f"worked_for_form_{contact_id}")
    
    if st.session_state.show_reported_to_form:
        show_reported_to_form(contact_id, f"reported_to_form_{contact_id}")


def show_relationship_management_for_company(company_id):
    """Show relationship management UI for a company (TO node)."""
    st.subheader("🔗 Employee Relationships")
    st.write("Manage contacts who have worked for this company")
    
    # Load existing relationships
    relationships_df = get_worked_for_relationships(to_node_id=company_id)
    
    # Display existing relationships
    st.write("**🏢 Employees (Contacts who worked for this company):**")
    if relationships_df is not None and len(relationships_df) > 0:
        for _, rel in relationships_df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                current_text = " (Current)" if rel.get('IS_CURRENT') else ""
                date_range = f"{rel.get('START_DATE', 'Unknown')} - {rel.get('END_DATE', 'Present')}"
                job_info = f" as {rel.get('JOB_TITLE', 'Unknown Role')}" if rel.get('JOB_TITLE') else ""
                st.write(f"**Contact ID:** {rel.get('FROM_NODE_ID')} | {date_range}{job_info}{current_text}")
            with col2:
                if st.button("Edit", key=f"edit_{rel.get('EDGE_ID')}"):
                    st.info("Edit functionality - coming soon")
            with col3:
                if st.button("Delete", key=f"delete_{rel.get('EDGE_ID')}", type="secondary"):
                    delete_worked_for_relationship(rel.get('EDGE_ID'))
                    st.success("Relationship deleted!")
                    st.rerun()
    else:
        st.info("No employee relationships found")
    
    # Add new relationship buttons
    st.write("**Add New Relationships:**")
    
    # Initialize session state for form display
    if 'show_employee_form' not in st.session_state:
        st.session_state.show_employee_form = False
    
    # Only show WORKED_FOR for companies (contact -> company relationships)
    if st.button("👤 Add Employee (WORKED_FOR)", key="btn_add_employee", use_container_width=True):
        st.session_state.show_employee_form = not st.session_state.show_employee_form
        st.rerun()
    
    # Show form based on button click
    if st.session_state.show_employee_form:
        show_employee_form(company_id, f"employee_form_{company_id}")