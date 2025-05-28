"""
Home Page

Provides overview and quick navigation for the People Directory app.
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.data.manager import DataManager
from src.utils.search import SearchEngine
from src.utils.edges import EdgeManager

def render_home_page():
    """Render the home page"""
    st.title("🏠 People Directory")
    st.markdown("Welcome to your comprehensive people and company relationship management system.")
    
    # Initialize managers
    data_manager = DataManager()
    search_engine = SearchEngine(data_manager)
    edge_manager = EdgeManager(data_manager)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    people = data_manager.load_people()
    companies = data_manager.load_companies()
    edges = data_manager.load_edges()
    edge_types = data_manager.load_edge_types()
    
    with col1:
        st.metric("People", len(people))
    
    with col2:
        st.metric("Companies", len(companies))
    
    with col3:
        st.metric("Relationships", len(edges))
    
    with col4:
        st.metric("Relationship Types", len(edge_types))
    
    st.markdown("---")
    
    # Quick search
    st.subheader("🔍 Quick Search")
    search_query = st.text_input("Search people or companies...", placeholder="Enter name, email, or company")
    
    if search_query:
        people_matches, company_matches = search_engine.search_all(search_query)
        
        if not people_matches.empty or not company_matches.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                if not people_matches.empty:
                    st.markdown("**People:**")
                    for _, person in people_matches.iterrows():
                        name = data_manager.get_entity_display_name(person["id"], "Person")
                        if st.button(f"👤 {name}", key=f"person_{person['id']}", use_container_width=True):
                            st.session_state.selected_person_id = person["id"]
                            st.switch_page("pages/people.py")
            
            with col2:
                if not company_matches.empty:
                    st.markdown("**Companies:**")
                    for _, company in company_matches.iterrows():
                        name = data_manager.get_entity_display_name(company["id"], "Company")
                        if st.button(f"🏢 {name}", key=f"company_{company['id']}", use_container_width=True):
                            st.session_state.selected_company_id = company["id"]
                            st.switch_page("pages/companies.py")
        else:
            st.info("No results found")
    
    st.markdown("---")
    
    # Recent activity / highlights
    st.subheader("📊 System Overview")
    
    # Show recent relationships
    if not edges.empty:
        st.markdown("**Recent Relationships:**")
        recent_edges = edges.tail(5)
        for _, edge in recent_edges.iterrows():
            source_name = data_manager.get_entity_display_name(edge["source_id"], "Person")  # Assuming most are people
            target_name = data_manager.get_entity_display_name(edge["target_id"], "Company")  # Assuming most are companies
            st.markdown(f"• {source_name} → **{edge['type']}** → {target_name}")
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Person", use_container_width=True):
            st.session_state.show_create_person_form = True
            st.switch_page("pages/people.py")
    
    with col2:
        if st.button("🏢 Add Company", use_container_width=True):
            st.session_state.show_create_company_form = True
            st.switch_page("pages/companies.py")
    
    with col3:
        if st.button("⚙️ Admin Settings", use_container_width=True):
            st.switch_page("pages/admin.py")
    
    # Show relationship type breakdown if there are edges
    if not edges.empty:
        st.markdown("---")
        st.subheader("📈 Relationship Breakdown")
        
        # Get relationship stats
        relationship_stats = edge_manager.get_relationship_stats()
        
        if relationship_stats.get("by_type"):
            # Create a simple chart
            import pandas as pd
            chart_data = pd.DataFrame.from_dict(
                relationship_stats["by_type"], 
                orient='index', 
                columns=['Count']
            )
            st.bar_chart(chart_data)
    
    # Navigation help
    st.markdown("---")
    st.subheader("🧭 Navigation")
    st.markdown("""
    - **People**: Manage individuals, view their relationships, and add new people
    - **Companies**: Manage organizations, view their relationships, and add new companies  
    - **Admin**: Configure relationship types, add new parameters, and manage system settings
    """)

if __name__ == "__main__":
    render_home_page()