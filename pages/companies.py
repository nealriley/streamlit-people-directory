"""
Companies Page

Handles all company-related functionality including search, view, and management.
"""

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.data.manager import DataManager
from src.utils.search import SearchEngine
from src.utils.edges import EdgeManager

def render_companies_page():
    """Render the companies management page"""
    st.title("🏢 Companies")
    
    # Initialize managers
    data_manager = DataManager()
    search_engine = SearchEngine(data_manager)
    edge_manager = EdgeManager(data_manager)
    
    # Load data
    companies = data_manager.load_companies()
    parameters = data_manager.load_parameters()["companies"]
    
    # Check for company ID in query parameters
    company_id = st.query_params.get("id")
    
    if company_id:
        # Show company detail view
        try:
            company_id = int(company_id)
            render_company_detail_view(data_manager, edge_manager, parameters, company_id)
        except (ValueError, TypeError):
            st.error("Invalid company ID")
            render_companies_search(data_manager, search_engine)
    else:
        # Show search interface
        render_companies_search(data_manager, search_engine)

def render_companies_search(data_manager, search_engine):
    """Render the companies search interface"""
    st.subheader("🔍 Search Companies")
    
    # Initialize session state for form visibility
    if "show_create_company_form" not in st.session_state:
        st.session_state.show_create_company_form = False
    
    # Check if we should show the form from quick actions
    if st.session_state.get("show_create_company_form", False):
        st.session_state.show_create_company_form = True
    
    companies = data_manager.load_companies()
    
    if companies.empty:
        st.info("No companies in the system. Add some companies to get started!")
        if st.button("➕ Create First Company", type="primary"):
            st.session_state.show_create_company_form = True
            st.rerun()
        
        if st.session_state.show_create_company_form:
            render_create_company_form(data_manager)
        return
    
    # Show create form if requested from quick actions
    if st.session_state.show_create_company_form:
        render_create_company_form(data_manager)
        return
    
    # Search functionality
    search_query = st.text_input("Search companies", placeholder="Enter company name, industry, or other details...")
    
    # Display results
    if search_query:
        matches = search_engine.search_companies(search_query)
        if not matches.empty:
            st.success(f"Found {len(matches)} companies")
            display_companies_results(matches, data_manager)
        else:
            st.info("No companies found matching your search")
            if st.button("➕ Create New Company", type="primary"):
                st.session_state.show_create_company_form = True
                st.rerun()
            
            if st.session_state.show_create_company_form:
                render_create_company_form(data_manager)
    else:
        st.info("Enter a search term to find companies, or browse all companies below.")
        display_companies_results(companies, data_manager)

def display_companies_results(companies_df, data_manager):
    """Display companies search results with navigation to detail view"""
    if companies_df.empty:
        return
    
    # Display each company
    for idx, row in companies_df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                name = data_manager.get_entity_display_name(row["id"], "Company")
                # Show additional info if available
                details = []
                if "industry" in row and pd.notna(row["industry"]) and row["industry"]:
                    details.append(f"🏭 {row['industry']}")
                if "website" in row and pd.notna(row["website"]) and row["website"]:
                    details.append(f"🌐 {row['website']}")
                
                st.markdown(f"**{name}** (ID: {row['id']})")
                if details:
                    st.markdown(f"*{' | '.join(details)}*")
            
            with col2:
                if st.button("👁️ View", key=f"view_company_{row['id']}", help="View details"):
                    # Navigate to company detail view using query parameters
                    st.query_params["id"] = str(row["id"])
                    st.rerun()
            
            st.markdown("---")

def render_company_detail_view(data_manager, edge_manager, parameters, company_id):
    """Render individual company detail view with back navigation"""
    
    # Back button
    if st.button("← Back to Companies", type="secondary"):
        # Clear query parameters to go back to search
        st.query_params.clear()
        st.rerun()
    
    company = data_manager.get_company_by_id(company_id)
    if company is None:
        st.error("Company not found")
        if st.button("← Back to Companies"):
            st.query_params.clear()
            st.rerun()
        return
    
    # Company header
    company_name = data_manager.get_entity_display_name(company_id, "Company")
    st.subheader(f"🏢 {company_name}")
    
    # Display and edit company details
    st.markdown("### Company Information")
    
    # Create form for editing
    with st.form("edit_company_form"):
        updated_data = {}
        
        col1, col2 = st.columns(2)
        
        for i, param in enumerate(parameters):
            field_name = param["name"]
            field_type = param["type"]
            is_required = param.get("required", False)
            current_value = company.get(field_name, "")
            
            # Determine which column to use
            col = col1 if i % 2 == 0 else col2
            
            with col:
                if field_type == "text":
                    label = f"{field_name.replace('_', ' ').title()}"
                    if is_required:
                        label += " *"
                    
                    # Special handling for certain fields
                    if field_name == "description":
                        updated_data[field_name] = st.text_area(
                            label,
                            value=str(current_value) if pd.notna(current_value) else "",
                            key=f"edit_{field_name}_{company_id}",
                            height=100
                        )
                    else:
                        updated_data[field_name] = st.text_input(
                            label,
                            value=str(current_value) if pd.notna(current_value) else "",
                            key=f"edit_{field_name}_{company_id}"
                        )
        
        if st.form_submit_button("💾 Save Changes"):
            try:
                # Validate required fields
                for param in parameters:
                    if param.get("required", False) and not updated_data.get(param["name"]):
                        st.error(f"{param['name'].replace('_', ' ').title()} is required")
                        return
                
                data_manager.update_company(company_id, updated_data)
                st.success("Company updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating company: {str(e)}")
    
    # Display relationships
    st.markdown("---")
    edge_manager.display_entity_relationships(company_id, "Company")
    
    # Add relationship form
    st.markdown("---")
    with st.expander("➕ Add New Relationship"):
        edge_manager.create_relationship_form(company_id, "Company")


def render_create_company_form(data_manager):
    """Render form to create a new company"""
    st.markdown("### ➕ Create New Company")
    
    parameters = data_manager.load_parameters()["companies"]
    
    with st.form("create_company_form"):
        company_data = {}
        
        col1, col2 = st.columns(2)
        
        for i, param in enumerate(parameters):
            field_name = param["name"]
            field_type = param["type"]
            is_required = param.get("required", False)
            
            # Determine which column to use
            col = col1 if i % 2 == 0 else col2
            
            with col:
                if field_type == "text":
                    label = f"{field_name.replace('_', ' ').title()}"
                    if is_required:
                        label += " *"
                    company_data[field_name] = st.text_input(
                        label,
                        key=f"create_{field_name}"
                    )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Create Company", type="primary"):
                try:
                    # Validate required fields
                    for param in parameters:
                        if param.get("required", False) and not company_data.get(param["name"]):
                            st.error(f"{param['name'].replace('_', ' ').title()} is required")
                            return
                    
                    company_id = data_manager.add_company(company_data)
                    st.success(f"Company created successfully with ID {company_id}!")
                    st.session_state.show_create_company_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating company: {str(e)}")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_create_company_form = False
                st.rerun()


if __name__ == "__main__":
    render_companies_page()