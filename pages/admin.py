"""
Admin Page

Handles system administration including edge types, parameter management, and data operations.
"""

import streamlit as st
import pandas as pd
import json
import zipfile
import io
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.data.manager import DataManager
from src.utils.edges import EdgeManager

def render_admin_page():
    """Render the admin page"""
    st.title("⚙️ Admin")
    st.markdown("Manage system settings, edge types, and data parameters.")
    
    # Initialize managers
    data_manager = DataManager()
    edge_manager = EdgeManager(data_manager)
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 Edge Types", "📝 Parameters", "💾 Data Management", "📊 System Stats"])
    
    with tab1:
        render_edge_types_management(data_manager)
    
    with tab2:
        render_parameters_management(data_manager)
    
    with tab3:
        render_data_management(data_manager)
    
    with tab4:
        render_system_stats(data_manager, edge_manager)

def render_edge_types_management(data_manager):
    """Render edge types management interface"""
    st.subheader("Manage Relationship Types")
    st.markdown("Define how people and companies can be related to each other.")
    
    edge_types = data_manager.load_edge_types()
    
    # Display current edge types
    st.markdown("#### Current Edge Types")
    if edge_types:
        for i, et in enumerate(edge_types):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
            
            with col1:
                st.text(et["name"])
            with col2:
                st.text(et["from_type"])
            with col3:
                st.text(et["to_type"])
            with col4:
                if st.button("✏️", key=f"edit_edge_{i}", help="Edit"):
                    st.session_state[f"editing_edge_{i}"] = True
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"delete_edge_{i}", help="Delete"):
                    edge_types.pop(i)
                    data_manager.save_edge_types(edge_types)
                    st.success("Edge type deleted!")
                    st.rerun()
            
            # Edit form if in edit mode
            if st.session_state.get(f"editing_edge_{i}", False):
                with st.form(f"edit_edge_form_{i}"):
                    st.markdown(f"**Editing: {et['name']}**")
                    new_name = st.text_input("Edge Name", value=et["name"])
                    new_from = st.selectbox("From Type", ["Person", "Company"], 
                                          index=0 if et["from_type"] == "Person" else 1)
                    new_to = st.selectbox("To Type", ["Person", "Company"], 
                                        index=0 if et["to_type"] == "Person" else 1)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save"):
                            edge_types[i] = {"name": new_name, "from_type": new_from, "to_type": new_to}
                            data_manager.save_edge_types(edge_types)
                            st.session_state[f"editing_edge_{i}"] = False
                            st.success("Edge type updated!")
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state[f"editing_edge_{i}"] = False
                            st.rerun()
            
            st.markdown("---")
    else:
        st.info("No edge types defined yet.")
    
    # Add new edge type
    st.markdown("#### Add New Edge Type")
    with st.form("add_edge_type_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_edge_name = st.text_input("Edge Name", placeholder="e.g., 'manages', 'works_for'")
        with col2:
            new_from_type = st.selectbox("From Type", ["Person", "Company"])
        with col3:
            new_to_type = st.selectbox("To Type", ["Person", "Company"])
        
        if st.form_submit_button("➕ Add Edge Type"):
            if new_edge_name:
                # Check if edge type already exists
                existing_names = [et["name"] for et in edge_types]
                if new_edge_name in existing_names:
                    st.error("Edge type with this name already exists!")
                else:
                    edge_types.append({
                        "name": new_edge_name,
                        "from_type": new_from_type,
                        "to_type": new_to_type
                    })
                    data_manager.save_edge_types(edge_types)
                    st.success(f"Added edge type: {new_edge_name}")
                    st.rerun()
            else:
                st.error("Please enter an edge name")

def render_parameters_management(data_manager):
    """Render parameters management interface"""
    st.subheader("Manage Data Parameters")
    st.markdown("Add custom fields to people and companies.")
    
    parameters = data_manager.load_parameters()
    
    # People parameters
    st.markdown("#### People Parameters")
    people_params = parameters.get("people", [])
    
    if people_params:
        for i, param in enumerate(people_params):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.text(param["name"])
            with col2:
                st.text(param["type"])
            with col3:
                st.text("✓" if param.get("required", False) else "✗")
            with col4:
                # Only allow deletion of non-required core fields
                if param["name"] not in ["first_name", "last_name"] or not param.get("required", False):
                    if st.button("🗑️", key=f"del_people_param_{i}", help="Delete parameter"):
                        people_params.pop(i)
                        parameters["people"] = people_params
                        data_manager.save_parameters(parameters)
                        st.success("Parameter removed!")
                        st.rerun()
    
    # Add new people parameter
    with st.expander("➕ Add People Parameter"):
        with st.form("add_people_param"):
            col1, col2, col3 = st.columns(3)
            with col1:
                param_name = st.text_input("Parameter Name", placeholder="e.g., 'department'")
            with col2:
                param_type = st.selectbox("Type", ["text"])  # Can be extended later
            with col3:
                is_required = st.checkbox("Required")
            
            if st.form_submit_button("Add Parameter"):
                if param_name:
                    # Check if parameter already exists
                    existing_names = [p["name"] for p in people_params]
                    if param_name in existing_names:
                        st.error("Parameter with this name already exists!")
                    else:
                        success = data_manager.add_parameter("people", param_name, param_type, is_required)
                        if success:
                            st.success(f"Added parameter: {param_name}")
                            st.rerun()
                        else:
                            st.error("Failed to add parameter")
                else:
                    st.error("Please enter a parameter name")
    
    st.markdown("---")
    
    # Companies parameters
    st.markdown("#### Company Parameters")
    company_params = parameters.get("companies", [])
    
    if company_params:
        for i, param in enumerate(company_params):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.text(param["name"])
            with col2:
                st.text(param["type"])
            with col3:
                st.text("✓" if param.get("required", False) else "✗")
            with col4:
                # Only allow deletion of non-required core fields
                if param["name"] != "name" or not param.get("required", False):
                    if st.button("🗑️", key=f"del_company_param_{i}", help="Delete parameter"):
                        company_params.pop(i)
                        parameters["companies"] = company_params
                        data_manager.save_parameters(parameters)
                        st.success("Parameter removed!")
                        st.rerun()
    
    # Add new company parameter
    with st.expander("➕ Add Company Parameter"):
        with st.form("add_company_param"):
            col1, col2, col3 = st.columns(3)
            with col1:
                param_name = st.text_input("Parameter Name", placeholder="e.g., 'revenue'")
            with col2:
                param_type = st.selectbox("Type", ["text"], key="company_param_type")
            with col3:
                is_required = st.checkbox("Required", key="company_param_required")
            
            if st.form_submit_button("Add Parameter"):
                if param_name:
                    # Check if parameter already exists
                    existing_names = [p["name"] for p in company_params]
                    if param_name in existing_names:
                        st.error("Parameter with this name already exists!")
                    else:
                        success = data_manager.add_parameter("companies", param_name, param_type, is_required)
                        if success:
                            st.success(f"Added parameter: {param_name}")
                            st.rerun()
                        else:
                            st.error("Failed to add parameter")
                else:
                    st.error("Please enter a parameter name")

def render_data_management(data_manager):
    """Render data management interface"""
    st.subheader("Data Management")
    
    # Export data
    st.markdown("#### Export Data")
    st.markdown("Download all system data as a ZIP file.")
    
    if st.button("📦 Export All Data"):
        zip_data = create_export_zip(data_manager)
        if zip_data:
            st.download_button(
                label="📥 Download ZIP",
                data=zip_data,
                file_name="people_directory_export.zip",
                mime="application/zip"
            )
    
    st.markdown("---")
    
    # Reset data
    st.markdown("#### Reset Data")
    st.warning("⚠️ **Danger Zone**: These operations cannot be undone!")
    
    with st.expander("🗑️ Reset Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear All People", type="secondary"):
                if st.session_state.get("confirm_clear_people", False):
                    empty_people = pd.DataFrame(columns=["id"] + [p["name"] for p in data_manager.load_parameters()["people"]])
                    data_manager.save_people(empty_people)
                    st.session_state.confirm_clear_people = False
                    st.success("All people data cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_people = True
                    st.error("Click again to confirm")
        
        with col2:
            if st.button("Clear All Companies", type="secondary"):
                if st.session_state.get("confirm_clear_companies", False):
                    empty_companies = pd.DataFrame(columns=["id"] + [p["name"] for p in data_manager.load_parameters()["companies"]])
                    data_manager.save_companies(empty_companies)
                    st.session_state.confirm_clear_companies = False
                    st.success("All company data cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_companies = True
                    st.error("Click again to confirm")
        
        if st.button("🗑️ Reset Everything", type="secondary"):
            if st.session_state.get("confirm_reset_all", False):
                # Clear all data
                empty_people = pd.DataFrame(columns=["id", "first_name", "last_name"])
                empty_companies = pd.DataFrame(columns=["id", "name"])
                empty_edges = pd.DataFrame(columns=["id", "source_id", "target_id", "type"])
                
                data_manager.save_people(empty_people)
                data_manager.save_companies(empty_companies)
                data_manager.save_edges(empty_edges)
                
                st.session_state.confirm_reset_all = False
                st.success("All data has been reset!")
                st.rerun()
            else:
                st.session_state.confirm_reset_all = True
                st.error("Click again to confirm complete reset")

def render_system_stats(data_manager, edge_manager):
    """Render system statistics"""
    st.subheader("System Statistics")
    
    # Load data
    people = data_manager.load_people()
    companies = data_manager.load_companies()
    edges = data_manager.load_edges()
    edge_types = data_manager.load_edge_types()
    parameters = data_manager.load_parameters()
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total People", len(people))
    with col2:
        st.metric("Total Companies", len(companies))
    with col3:
        st.metric("Total Relationships", len(edges))
    with col4:
        st.metric("Edge Types", len(edge_types))
    
    st.markdown("---")
    
    # Detailed statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Parameters")
        st.markdown(f"**People Parameters:** {len(parameters.get('people', []))}")
        for param in parameters.get('people', []):
            required_text = " (Required)" if param.get('required', False) else ""
            st.markdown(f"• {param['name']}{required_text}")
        
        st.markdown(f"**Company Parameters:** {len(parameters.get('companies', []))}")
        for param in parameters.get('companies', []):
            required_text = " (Required)" if param.get('required', False) else ""
            st.markdown(f"• {param['name']}{required_text}")
    
    with col2:
        st.markdown("#### Edge Types")
        for et in edge_types:
            st.markdown(f"• **{et['name']}**: {et['from_type']} → {et['to_type']}")
    
    # Relationship statistics
    if not edges.empty:
        st.markdown("---")
        st.markdown("#### Relationship Statistics")
        
        relationship_stats = edge_manager.get_relationship_stats()
        
        if relationship_stats.get("by_type"):
            st.markdown("**Relationships by Type:**")
            chart_data = pd.DataFrame.from_dict(
                relationship_stats["by_type"], 
                orient='index', 
                columns=['Count']
            )
            st.bar_chart(chart_data)

def create_export_zip(data_manager):
    """Create a ZIP file with all data for export"""
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add CSV files
            if os.path.exists(data_manager.people_file):
                zip_file.write(data_manager.people_file, "people.csv")
            if os.path.exists(data_manager.companies_file):
                zip_file.write(data_manager.companies_file, "companies.csv")
            if os.path.exists(data_manager.edges_file):
                zip_file.write(data_manager.edges_file, "edges.csv")
            if os.path.exists(data_manager.edge_types_file):
                zip_file.write(data_manager.edge_types_file, "edge_types.json")
            if os.path.exists(data_manager.parameters_file):
                zip_file.write(data_manager.parameters_file, "parameters.json")
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    except Exception as e:
        st.error(f"Error creating export: {str(e)}")
        return None

if __name__ == "__main__":
    render_admin_page()