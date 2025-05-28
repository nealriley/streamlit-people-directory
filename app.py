"""
People Directory - Main Application

A comprehensive relationship management system for people and companies.
Built with a modular architecture supporting dynamic parameters and custom relationship types.
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from pages.home import render_home_page
    from pages.people import render_people_page
    from pages.companies import render_companies_page
    from pages.admin import render_admin_page
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="People Directory",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .nav-button {
        width: 100%;
        margin: 0.2rem 0;
    }
    .sidebar .block-container {
        padding-top: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏠 Navigation")
        
        # Navigation buttons
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("👥 People", key="nav_people", use_container_width=True):
            st.session_state.current_page = "people"
            st.rerun()
        
        if st.button("🏢 Companies", key="nav_companies", use_container_width=True):
            st.session_state.current_page = "companies"
            st.rerun()
        
        if st.button("⚙️ Admin", key="nav_admin", use_container_width=True):
            st.session_state.current_page = "admin"
            st.rerun()
        
        st.markdown("---")
        
        # Quick stats in sidebar
        try:
            from src.data.manager import DataManager
            data_manager = DataManager()
            
            people_count = len(data_manager.load_people())
            companies_count = len(data_manager.load_companies())
            relationships_count = len(data_manager.load_edges())
            
            st.markdown("### 📊 Quick Stats")
            st.metric("People", people_count)
            st.metric("Companies", companies_count)
            st.metric("Relationships", relationships_count)
            
        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")
        
        st.markdown("---")
        st.markdown("""
        ### 📋 About
        **People Directory** is a comprehensive relationship management system 
        that helps you track connections between people and companies.
        
        **Features:**
        - 🔍 Advanced search
        - 🔗 Custom relationships
        - 📝 Dynamic parameters
        - 📊 Data insights
        """)
    
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    
    # Route to appropriate page
    try:
        if st.session_state.current_page == "home":
            render_home_page()
        elif st.session_state.current_page == "people":
            render_people_page()
        elif st.session_state.current_page == "companies":
            render_companies_page()
        elif st.session_state.current_page == "admin":
            render_admin_page()
        else:
            st.error("Page not found")
            st.session_state.current_page = "home"
            st.rerun()
    
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.markdown("**Debug info:**")
        st.code(str(e))
        
        # Provide a way to recover
        if st.button("🏠 Return to Home"):
            st.session_state.current_page = "home"
            st.rerun()

if __name__ == "__main__":
    main()