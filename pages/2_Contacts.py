"""
Contacts page - Search and explore people's professional relationships
"""
import streamlit as st
from utils import (
    get_contacts_data, 
    display_table_info, 
    show_relationship_management_for_contact,
    search_contacts_by_email
)

st.set_page_config(
    page_title="Contacts - People Card",
    page_icon="👥",
    layout="wide"
)

def show_contacts_page():
    """Display the Contacts page."""
    st.header("👥 Contacts")
    st.write("Search for people to explore their employment history and professional relationships")
    
    # Check for query parameter
    query_params = st.query_params
    object_id = query_params.get("id")
    
    if object_id:
        st.info(f"🔍 Filtering by ID: {object_id}")
        # Auto-execute query for specific ID
        with st.spinner("Loading contact data..."):
            df = get_contacts_data(object_id=object_id)
            if df is not None:
                st.session_state.contacts_df = df
    else:
        # Search functionality
        st.subheader("🔍 Search Contacts")
        st.write("Enter an email address to find someone and explore their professional network")
        
        email_search = st.text_input("Search by Email", placeholder="john@example.com", help="Enter all or part of someone's email address")
        
        if email_search:
            search_results = search_contacts_by_email(email_search)
            if search_results is not None and len(search_results) > 0:
                st.write("**Search Results:**")
                for _, row in search_results.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        first_name = row.get('PROPERTIES_FIRSTNAME_VALUE', '')
                        last_name = row.get('PROPERTIES_LASTNAME_VALUE', '')
                        name = f"{first_name} {last_name}".strip()
                        if not name:
                            name = f"ID: {row['ID']}"
                        st.write(f"**{name}** - {row.get('EMAIL', 'No email')}")
                    with col2:
                        if st.button(f"View", key=f"view_contact_{row['ID']}"):
                            st.query_params["id"] = row['ID']
                            st.rerun()
            else:
                st.info("No contacts found matching your search. Try a different email or partial email address.")
    
    # Display data if available
    if 'contacts_df' in st.session_state:
        df = st.session_state.contacts_df
        display_table_info(df, "Contacts")
        
        st.subheader("Contacts Data")
        st.dataframe(df, use_container_width=True)
        
        # Show relationship management if ID parameter is present
        if object_id:
            st.divider()
            show_relationship_management_for_contact(object_id)

# Run the page
show_contacts_page()