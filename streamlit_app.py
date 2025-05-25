import os
import pandas as pd
import streamlit as st
import zipfile
import io
import json

DATA_DIR = "data"
PEOPLE_FILE = os.path.join(DATA_DIR, "people.csv")
COMPANIES_FILE = os.path.join(DATA_DIR, "companies.csv")
EDGES_FILE = os.path.join(DATA_DIR, "edges.csv")
EDGE_TYPES_FILE = os.path.join(DATA_DIR, "edge_types.json")

st.set_page_config(page_title="People Directory", page_icon="👥")

@st.cache_data
def load_people():
    if not os.path.exists(PEOPLE_FILE):
        return pd.DataFrame(columns=["id", "first_name", "last_name"])
    df = pd.read_csv(PEOPLE_FILE)
    if not df.empty:
        df["id"] = df["id"].astype(int)
    return df

@st.cache_data
def load_companies():
    if not os.path.exists(COMPANIES_FILE):
        return pd.DataFrame(columns=["id", "name"])
    df = pd.read_csv(COMPANIES_FILE)
    if not df.empty:
        df["id"] = df["id"].astype(int)
    return df

@st.cache_data
def load_edges():
    if not os.path.exists(EDGES_FILE):
        return pd.DataFrame(columns=["id", "source_id", "target_id", "type"])
    df = pd.read_csv(EDGES_FILE)
    if not df.empty:
        df["id"] = df["id"].astype(int)
        df["source_id"] = df["source_id"].astype(int)
        df["target_id"] = df["target_id"].astype(int)
    return df

@st.cache_data
def load_edge_types():
    if os.path.exists(EDGE_TYPES_FILE):
        with open(EDGE_TYPES_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default edge types
        default_types = [
            {"name": "reports_to", "from_type": "Person", "to_type": "Person"},
            {"name": "works_for", "from_type": "Person", "to_type": "Company"}
        ]
        save_edge_types(default_types)
        return default_types

def save_people(df: pd.DataFrame):
    df.to_csv(PEOPLE_FILE, index=False)
    load_people.clear()


def save_companies(df: pd.DataFrame):
    df.to_csv(COMPANIES_FILE, index=False)
    load_companies.clear()


def save_edges(df: pd.DataFrame):
    df.to_csv(EDGES_FILE, index=False)
    load_edges.clear()


def save_edge_types(edge_types: list):
    with open(EDGE_TYPES_FILE, 'w') as f:
        json.dump(edge_types, f, indent=2)
    load_edge_types.clear()


def next_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


def get_valid_edge_types(from_type: str, to_type: str):
    edge_types = load_edge_types()
    return [et["name"] for et in edge_types if et["from_type"] == from_type and et["to_type"] == to_type]


def search_view():
    st.header("🔎 Search")
    query = st.text_input("Search for people or companies")
    if query:
        people = load_people()
        companies = load_companies()
        ppl_matches = people[
            people.apply(lambda r: query.lower() in f"{r.first_name} {r.last_name}".lower(), axis=1)
        ]
        comp_matches = companies[companies["name"].str.contains(query, case=False)]
        if not ppl_matches.empty:
            st.subheader("People")
            for _, row in ppl_matches.iterrows():
                st.markdown(f"**{row.first_name} {row.last_name}** (id {row.id})")
        if not comp_matches.empty:
            st.subheader("Companies")
            for _, row in comp_matches.iterrows():
                st.markdown(f"**{row.name}** (id {row.id})")
        if ppl_matches.empty and comp_matches.empty:
            st.info("No results found")


def display_edges(node_id: int, node_type: str):
    edges = load_edges()
    people = load_people()
    companies = load_companies()
    edge_types = load_edge_types()
    
    # Create a mapping of edge names to their type definitions
    edge_type_map = {et["name"]: et for et in edge_types}
    
    related = edges[(edges.source_id == node_id) | (edges.target_id == node_id)]
    
    for _, edge in related.iterrows():
        edge_def = edge_type_map.get(edge.type)
        if not edge_def:
            continue  # Skip if edge type not found
            
        # Determine the actual from and to entities based on edge definition
        if edge.source_id == node_id:
            # Current node is the source
            target_id = edge.target_id
            if edge_def["to_type"] == "Person":
                target = people[people.id == target_id].iloc[0]
                target_name = f"{target.first_name} {target.last_name}"
            else:
                target = companies[companies.id == target_id].iloc[0]
                target_name = target.name
            
            # Show: Current Node --edge_type--> Target
            current_name = f"{people[people.id == node_id].iloc[0].first_name} {people[people.id == node_id].iloc[0].last_name}" if node_type == "Person" else companies[companies.id == node_id].iloc[0].name
            st.markdown(f"**{current_name}** ➡ **{edge.type}** ➡ **{target_name}** (id {target_id})")
        else:
            # Current node is the target
            source_id = edge.source_id
            if edge_def["from_type"] == "Person":
                source = people[people.id == source_id].iloc[0]
                source_name = f"{source.first_name} {source.last_name}"
            else:
                source = companies[companies.id == source_id].iloc[0]
                source_name = source.name
            
            # Show: Source --edge_type--> Current Node
            current_name = f"{people[people.id == node_id].iloc[0].first_name} {people[people.id == node_id].iloc[0].last_name}" if node_type == "Person" else companies[companies.id == node_id].iloc[0].name
            st.markdown(f"**{source_name}** (id {source_id}) ➡ **{edge.type}** ➡ **{current_name}**")


def person_view():
    people = load_people()
    person_ids = people.id.tolist()
    if not person_ids:
        st.info("No people available")
        return
    pid = st.selectbox("Select person", person_ids, format_func=lambda x: f"{people[people.id==x].iloc[0].first_name} {people[people.id==x].iloc[0].last_name}")
    person = people[people.id == pid].iloc[0]
    st.subheader(f"{person.first_name} {person.last_name}")

    if st.button("Save metadata"):
        people.loc[people.id == pid, "first_name"] = st.session_state.first_name
        people.loc[people.id == pid, "last_name"] = st.session_state.last_name
        save_people(people)
        st.success("Updated")

    st.text_input("First name", key="first_name", value=person.first_name)
    st.text_input("Last name", key="last_name", value=person.last_name)

    st.markdown("### Relationships")
    display_edges(pid, "Person")

    with st.expander("Add relationship"):
        target_category = st.selectbox("Target type", ["Person", "Company"])
        target = None
        
        if target_category == "Person":
            # Only show edge types where from_type is "Person" and to_type is "Person"
            valid_types = get_valid_edge_types("Person", "Person")
            target_options = people[people.id != pid]
            if target_options.empty:
                st.warning("No other people available to connect to")
            else:
                target = st.selectbox("Target person", target_options.id.tolist(), format_func=lambda x: f"{target_options[target_options.id==x].iloc[0].first_name} {target_options[target_options.id==x].iloc[0].last_name}")
        else:
            # Only show edge types where from_type is "Person" and to_type is "Company"
            valid_types = get_valid_edge_types("Person", "Company")
            companies = load_companies()
            if companies.empty:
                st.warning("No companies available to connect to")
            else:
                target = st.selectbox("Target company", companies.id.tolist(), format_func=lambda x: companies[companies.id==x].iloc[0].name)
        
        if valid_types and target is not None:
            edge_type = st.selectbox("Type", valid_types)
            if st.button("Add edge"):
                edges = load_edges()
                new_id = next_id(edges)
                new_row = pd.DataFrame([[new_id, pid, target, edge_type]], columns=["id", "source_id", "target_id", "type"])
                edges = pd.concat([edges, new_row], ignore_index=True)
                save_edges(edges)
                st.success("Edge added")
                st.experimental_rerun()
        elif not valid_types:
            st.warning(f"No edge types available for Person → {target_category}")


def company_view():
    companies = load_companies()
    if companies.empty:
        st.info("No companies available")
        return
    cid = st.selectbox(
        "Select company",
        companies.id.tolist(),
        format_func=lambda x: companies.loc[companies.id == x, "name"].values[0] if x in companies.id.values else str(x)
    )
    company = companies[companies.id == cid].iloc[0]
    st.subheader(company.name)

    if st.button("Save metadata"):
        companies.loc[companies.id == cid, "name"] = st.session_state.company_name
        save_companies(companies)
        st.success("Updated")

    st.text_input("Company name", key="company_name", value=company.name)

    st.markdown("### Relationships")
    display_edges(cid, "Company")

    with st.expander("Add relationship"):
        # Only show edge types where from_type is "Company"
        valid_person_types = get_valid_edge_types("Company", "Person")
        valid_company_types = get_valid_edge_types("Company", "Company")
        
        if valid_person_types or valid_company_types:
            target_category = st.selectbox("Target type", ["Person", "Company"])
            
            if target_category == "Person":
                valid_types = valid_person_types
                people = load_people()
                if people.empty:
                    st.warning("No people available to connect to")
                    target = None
                else:
                    target = st.selectbox("Target person", people.id.tolist(), format_func=lambda x: f"{people[people.id==x].iloc[0].first_name} {people[people.id==x].iloc[0].last_name}")
            else:
                valid_types = valid_company_types
                target_options = companies[companies.id != cid]
                if target_options.empty:
                    st.warning("No other companies available to connect to")
                    target = None
                else:
                    target = st.selectbox("Target company", target_options.id.tolist(), format_func=lambda x: target_options[target_options.id==x].iloc[0].name)
            
            if valid_types and target is not None:
                edge_type = st.selectbox("Type", valid_types)
                if st.button("Add edge", key="add_company_edge"):
                    edges = load_edges()
                    new_id = next_id(edges)
                    new_row = pd.DataFrame([[new_id, cid, target, edge_type]], columns=["id", "source_id", "target_id", "type"])
                    edges = pd.concat([edges, new_row], ignore_index=True)
                    save_edges(edges)
                    st.success("Edge added")
                    st.experimental_rerun()
            elif not valid_types:
                st.warning(f"No edge types available for Company → {target_category}")
        else:
            st.warning("No edge types available where Company is the from_type")


def create_view():
    st.header("➕ Create")
    item_type = st.selectbox("What do you want to create?", ["Person", "Company"])
    if item_type == "Person":
        first = st.text_input("First name")
        last = st.text_input("Last name")
        if st.button("Create person"):
            people = load_people()
            new_id = next_id(people)
            people.loc[len(people)] = [new_id, first, last]
            save_people(people)
            st.success(f"Created person {first} {last} with id {new_id}")
    else:
        name = st.text_input("Company name")
        if st.button("Create company"):
            companies = load_companies()
            new_id = next_id(companies)
            companies.loc[len(companies)] = [new_id, name]
            save_companies(companies)
            st.success(f"Created company {name} with id {new_id}")


def admin_view():
    st.header("⚙️ Admin")
    
    tab1, tab2, tab3 = st.tabs(["Edge Types", "Reset Data", "Export Data"])
    
    with tab1:
        st.subheader("Manage Edge Types")
        edge_types = load_edge_types()
        
        # Display current edge types
        st.markdown("#### Current Edge Types")
        for i, et in enumerate(edge_types):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.text(et["name"])
            with col2:
                st.text(et["from_type"])
            with col3:
                st.text(et["to_type"])
            with col4:
                if st.button("🗑️", key=f"delete_{i}"):
                    edge_types.pop(i)
                    save_edge_types(edge_types)
                    st.experimental_rerun()
        
        # Add new edge type
        st.markdown("#### Add New Edge Type")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input("Edge Name", key="new_edge_name")
        with col2:
            new_from = st.selectbox("From Type", ["Person", "Company"], key="new_from_type")
        with col3:
            new_to = st.selectbox("To Type", ["Person", "Company"], key="new_to_type")
        
        if st.button("Add Edge Type"):
            if new_name:
                edge_types.append({"name": new_name, "from_type": new_from, "to_type": new_to})
                save_edge_types(edge_types)
                st.success(f"Added edge type: {new_name}")
                st.experimental_rerun()
            else:
                st.error("Please enter an edge name")
    
    with tab2:
        st.subheader("Reset All Data")
        st.warning("⚠️ This will permanently delete all people, companies, and relationships!")
        
        if st.button("🗑️ Reset All Data", type="secondary"):
            # Create empty dataframes
            empty_people = pd.DataFrame(columns=["id", "first_name", "last_name"])
            empty_companies = pd.DataFrame(columns=["id", "name"])
            empty_edges = pd.DataFrame(columns=["id", "source_id", "target_id", "type"])
            
            # Save empty files
            save_people(empty_people)
            save_companies(empty_companies)
            save_edges(empty_edges)
            
            st.success("All data has been reset!")
    
    with tab3:
        st.subheader("Export Data")
        st.info("Download all data as a ZIP file containing CSV files and edge types configuration.")
        
        if st.button("📦 Export All Data"):
            # Create a ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add CSV files
                if os.path.exists(PEOPLE_FILE):
                    zip_file.write(PEOPLE_FILE, "people.csv")
                if os.path.exists(COMPANIES_FILE):
                    zip_file.write(COMPANIES_FILE, "companies.csv")
                if os.path.exists(EDGES_FILE):
                    zip_file.write(EDGES_FILE, "edges.csv")
                if os.path.exists(EDGE_TYPES_FILE):
                    zip_file.write(EDGE_TYPES_FILE, "edge_types.json")
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 Download ZIP",
                data=zip_buffer.getvalue(),
                file_name="people_directory_export.zip",
                mime="application/zip"
            )

def main():
    view = st.sidebar.selectbox("View", ["Search", "Person", "Company", "Create", "Admin"])
    if view == "Search":
        search_view()
    elif view == "Person":
        person_view()
    elif view == "Company":
        company_view()
    elif view == "Create":
        create_view()
    else:
        admin_view()

if __name__ == "__main__":
    main()
