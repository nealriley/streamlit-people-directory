"""
People Page

Handles all people-related functionality including search, view, and management.
"""

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.data.manager import DataManager
from src.utils.search import SearchEngine
from src.utils.edges import EdgeManager

def render_people_page():
    """Render the people management page"""
    st.title("👥 People")
    
    # Initialize managers
    data_manager = DataManager()
    search_engine = SearchEngine(data_manager)
    edge_manager = EdgeManager(data_manager)
    
    # Load data
    people = data_manager.load_people()
    parameters = data_manager.load_parameters()["people"]
    
    # Check for person ID in query parameters
    person_id = st.query_params.get("id")
    
    if person_id:
        # Show person detail view
        try:
            person_id = int(person_id)
            render_person_detail_view(data_manager, edge_manager, parameters, person_id)
        except (ValueError, TypeError):
            st.error("Invalid person ID")
            render_people_search(data_manager, search_engine)
    else:
        # Show search interface
        render_people_search(data_manager, search_engine)

def render_people_search(data_manager, search_engine):
    """Render the people search interface"""
    st.subheader("🔍 Search People")
    
    # Initialize session state for form visibility
    if "show_create_person_form" not in st.session_state:
        st.session_state.show_create_person_form = False
    
    # Check if we should show the form from quick actions
    if st.session_state.get("show_create_person_form", False):
        st.session_state.show_create_person_form = True
    
    people = data_manager.load_people()
    
    if people.empty:
        st.info("No people in the system. Add some people to get started!")
        if st.button("➕ Create First Person", type="primary"):
            st.session_state.show_create_person_form = True
            st.rerun()
        
        if st.session_state.show_create_person_form:
            render_create_person_form(data_manager)
        return
    
    # Show create form if requested from quick actions
    if st.session_state.show_create_person_form:
        render_create_person_form(data_manager)
        return
    
    # Search functionality
    search_query = st.text_input("Search people", placeholder="Enter name, email, or other details...")
    
    # Display results
    if search_query:
        matches = search_engine.search_people(search_query)
        if not matches.empty:
            st.success(f"Found {len(matches)} people")
            display_people_results(matches, data_manager)
        else:
            st.info("No people found matching your search")
            if st.button("➕ Create New Person", type="primary"):
                st.session_state.show_create_person_form = True
                st.rerun()
            
            if st.session_state.show_create_person_form:
                render_create_person_form(data_manager)
    else:
        st.info("Enter a search term to find people, or browse all people below.")
        display_people_results(people, data_manager)

def display_people_results(people_df, data_manager):
    """Display people search results with navigation to detail view"""
    if people_df.empty:
        return
    
    # Display each person
    for idx, row in people_df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                name = data_manager.get_entity_display_name(row["id"], "Person")
                # Show additional info if available
                details = []
                if "email" in row and pd.notna(row["email"]) and row["email"]:
                    details.append(f"📧 {row['email']}")
                if "phone" in row and pd.notna(row["phone"]) and row["phone"]:
                    details.append(f"📞 {row['phone']}")
                
                st.markdown(f"**{name}** (ID: {row['id']})")
                if details:
                    st.markdown(f"*{' | '.join(details)}*")
            
            with col2:
                if st.button("👁️ View", key=f"view_person_{row['id']}", help="View details"):
                    # Navigate to person detail view using query parameters
                    st.query_params["id"] = str(row["id"])
                    st.rerun()
            
            st.markdown("---")

def render_person_detail_view(data_manager, edge_manager, parameters, person_id):
    """Render individual person detail view with back navigation"""
    
    # Back button
    if st.button("← Back to People", type="secondary"):
        # Clear query parameters to go back to search
        st.query_params.clear()
        st.rerun()
    
    person = data_manager.get_person_by_id(person_id)
    if person is None:
        st.error("Person not found")
        if st.button("← Back to People"):
            st.query_params.clear()
            st.rerun()
        return
    
    # Person header
    person_name = data_manager.get_entity_display_name(person_id, "Person")
    st.subheader(f"👤 {person_name}")
    
    # Display and edit person details
    st.markdown("### Personal Information")
    
    # Create form for editing
    with st.form("edit_person_form"):
        updated_data = {}
        
        col1, col2 = st.columns(2)
        
        for i, param in enumerate(parameters):
            field_name = param["name"]
            field_type = param["type"]
            is_required = param.get("required", False)
            current_value = person.get(field_name, "")
            
            # Determine which column to use
            col = col1 if i % 2 == 0 else col2
            
            with col:
                if field_type == "text":
                    label = f"{field_name.replace('_', ' ').title()}"
                    if is_required:
                        label += " *"
                    updated_data[field_name] = st.text_input(
                        label,
                        value=str(current_value) if pd.notna(current_value) else "",
                        key=f"edit_{field_name}_{person_id}"
                    )
        
        if st.form_submit_button("💾 Save Changes"):
            try:
                # Validate required fields
                for param in parameters:
                    if param.get("required", False) and not updated_data.get(param["name"]):
                        st.error(f"{param['name'].replace('_', ' ').title()} is required")
                        return
                
                data_manager.update_person(person_id, updated_data)
                st.success("Person updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating person: {str(e)}")
    
    # Display relationships
    st.markdown("---")
    edge_manager.display_entity_relationships(person_id, "Person")
    
    # Add relationship form
    st.markdown("---")
    with st.expander("➕ Add New Relationship"):
        edge_manager.create_relationship_form(person_id, "Person")


def render_create_person_form(data_manager):
    """Render form to create a new person"""
    st.markdown("### ➕ Create New Person")
    
    parameters = data_manager.load_parameters()["people"]
    
    with st.form("create_person_form"):
        person_data = {}
        
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
                    person_data[field_name] = st.text_input(
                        label,
                        key=f"create_{field_name}"
                    )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Create Person", type="primary"):
                try:
                    # Validate required fields
                    for param in parameters:
                        if param.get("required", False) and not person_data.get(param["name"]):
                            st.error(f"{param['name'].replace('_', ' ').title()} is required")
                            return
                    
                    person_id = data_manager.add_person(person_data)
                    st.success(f"Person created successfully with ID {person_id}!")
                    st.session_state.show_create_person_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating person: {str(e)}")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_create_person_form = False
                st.rerun()


if __name__ == "__main__":
    render_people_page()