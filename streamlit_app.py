"""
People Card

Explore and visualize professional relationships between people and companies.
Navigate to different pages using the sidebar.
"""
import streamlit as st

st.set_page_config(
    page_title="People Card",
    page_icon="👤",
    layout="wide"
)

# Main page content
st.title("👤 People Card")
st.subheader("Explore Professional Networks and Relationships")

st.markdown("""
## Welcome to People Card

People Card helps you discover and explore professional relationships within your network. Search for people and companies to visualize their connections and career journeys.

### How to Use People Card

🔍 **Search for People or Companies**
- Use the **Companies** page to search by company domain
- Use the **Contacts** page to search by email address
- Click "View" on any result to see detailed relationship information

👥 **Explore Professional Networks**
- See who worked for which companies
- Understand reporting relationships between colleagues
- Visualize career paths and company connections

### Relationship Types

People Card tracks two main types of professional relationships:

#### 🏢 **WORKED_FOR** (Employment Relationships)
- **Direction**: Person → Company
- **What it means**: Shows employment history and current positions
- **Details**: Job titles, departments, start/end dates
- **Examples**: 
  - "Alice worked for TechCorp as a Software Engineer from 2020-2023"
  - "Bob currently works at StartupInc as VP of Sales"

#### 👥 **REPORTED_TO** (Reporting Relationships)  
- **Direction**: Employee → Manager
- **What it means**: Shows organizational hierarchy and management structure
- **Details**: Relationship type (direct report, dotted line, matrix), start/end dates
- **Examples**:
  - "Sarah reports directly to John as Engineering Manager"
  - "Mike has a dotted-line relationship with Lisa for cross-functional projects"

### Getting Started

1. **Find Someone**: Use the sidebar to navigate to Companies or Contacts
2. **Search**: Enter a company domain or person's email to search
3. **Explore**: Click "View" to see their professional relationships
4. **Add Relationships**: Use the relationship buttons to add new connections
5. **Discover Networks**: Follow the connections to explore the broader network

### Example Workflows

- **Research a Company**: Search by domain → see all employees → explore their backgrounds
- **Map Team Structure**: Find a manager → see their direct reports → understand org chart
- **Track Career Paths**: Find a person → see their employment history → discover career progression
- **Network Analysis**: Explore connections between people across different companies

---

*Ready to explore? Use the sidebar to search for companies or contacts and start discovering professional networks!*
""")

# Quick navigation
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 🏢 Companies
    Search companies by domain name to find:
    - Current and former employees
    - Company relationships
    - Organizational insights
    """)

with col2:
    st.markdown("""
    #### 👥 Contacts  
    Search people by email to discover:
    - Employment history
    - Reporting relationships
    - Professional connections
    """)

with col3:
    st.markdown("""
    #### 🔍 Custom Queries
    Advanced users can:
    - Write custom SQL queries
    - Explore raw data
    - Generate custom reports
    """)