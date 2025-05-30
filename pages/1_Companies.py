"""
Companies page - Search and explore company relationships
"""
import streamlit as st
from utils import (
    get_companies_data, 
    display_table_info, 
    show_relationship_management_for_company,
    search_companies_by_domain
)

st.set_page_config(
    page_title="Companies - People Card",
    page_icon="🏢",
    layout="wide"
)

def show_companies_page():
    """Display the Companies page."""
    st.header("🏢 Companies")
    st.write("Search for companies to explore their employee relationships and organizational structure")
    
    # Check for query parameter
    query_params = st.query_params
    object_id = query_params.get("id")
    
    if object_id:
        st.info(f"🔍 Filtering by ID: {object_id}")
        # Auto-execute query for specific ID
        with st.spinner("Loading company data..."):
            df = get_companies_data(object_id=object_id)
            if df is not None:
                st.session_state.companies_df = df
    else:
        # Search functionality
        st.subheader("🔍 Search Companies")
        st.write("Enter a company domain to find and explore their professional network")
        
        domain_search = st.text_input("Search by Domain", placeholder="example.com", help="Enter all or part of a company's domain name")
        
        if domain_search:
            search_results = search_companies_by_domain(domain_search)
            if search_results is not None and len(search_results) > 0:
                st.write("**Search Results:**")
                for _, row in search_results.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{row.get('NAME', 'Unknown')}** - {row.get('DOMAIN', 'No domain')}")
                    with col2:
                        if st.button(f"View", key=f"view_company_{row['ID']}"):
                            st.query_params["id"] = row['ID']
                            st.rerun()
            else:
                st.info("No companies found matching your search. Try a different domain or partial domain name.")
    
    # Display data if available
    if 'companies_df' in st.session_state:
        df = st.session_state.companies_df
        display_table_info(df, "Companies")
        
        st.subheader("Companies Data")
        st.dataframe(df, use_container_width=True)
        
        # Show relationship management if ID parameter is present
        if object_id:
            st.divider()
            show_relationship_management_for_company(object_id)

# Run the page
show_companies_page()