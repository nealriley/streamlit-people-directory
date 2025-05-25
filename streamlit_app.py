import os
import pandas as pd
import streamlit as st

DATA_DIR = "data"
PEOPLE_FILE = os.path.join(DATA_DIR, "people.csv")
COMPANIES_FILE = os.path.join(DATA_DIR, "companies.csv")
EDGES_FILE = os.path.join(DATA_DIR, "edges.csv")

st.set_page_config(page_title="People Directory", page_icon="👥")

@st.cache_data
def load_people():
    return pd.read_csv(PEOPLE_FILE)

@st.cache_data
def load_companies():
    return pd.read_csv(COMPANIES_FILE)

@st.cache_data
def load_edges():
    return pd.read_csv(EDGES_FILE)


def save_people(df: pd.DataFrame):
    df.to_csv(PEOPLE_FILE, index=False)
    load_people.clear()


def save_companies(df: pd.DataFrame):
    df.to_csv(COMPANIES_FILE, index=False)
    load_companies.clear()


def save_edges(df: pd.DataFrame):
    df.to_csv(EDGES_FILE, index=False)
    load_edges.clear()


def next_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


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
    related = edges[(edges.source_id == node_id) | (edges.target_id == node_id)]
    for _, edge in related.iterrows():
        if edge.source_id == node_id:
            target_type = "Person" if edge.target_id in people.id.values else "Company"
            if target_type == "Person":
                target = people[people.id == edge.target_id].iloc[0]
                name = f"{target.first_name} {target.last_name}"
            else:
                target = companies[companies.id == edge.target_id].iloc[0]
                name = target.name
            st.markdown(f"➡ **{edge.type}** → {name} (id {edge.target_id})")
        else:
            source_type = "Person" if edge.source_id in people.id.values else "Company"
            if source_type == "Person":
                src = people[people.id == edge.source_id].iloc[0]
                name = f"{src.first_name} {src.last_name}"
            else:
                src = companies[companies.id == edge.source_id].iloc[0]
                name = src.name
            st.markdown(f"⬅ **{edge.type}** ← {name} (id {edge.source_id})")


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
    display_edges(pid, "person")

    with st.expander("Add relationship"):
        edge_type = st.selectbox("Type", ["reports_to", "works_for"])
        target_category = st.selectbox("Target type", ["Person", "Company"])
        if target_category == "Person":
            target_options = people[people.id != pid]
            target = st.selectbox("Target person", target_options.id.tolist(), format_func=lambda x: f"{target_options[target_options.id==x].iloc[0].first_name} {target_options[target_options.id==x].iloc[0].last_name}")
        else:
            companies = load_companies()
            target_options = companies
            target = st.selectbox("Target company", target_options.id.tolist(), format_func=lambda x: target_options[target_options.id==x].iloc[0].name)
        if st.button("Add edge"):
            edges = load_edges()
            new_id = next_id(edges)
            edges.loc[len(edges)] = [new_id, pid, target, edge_type]
            save_edges(edges)
            st.success("Edge added")


def company_view():
    companies = load_companies()
    if companies.empty:
        st.info("No companies available")
        return
    cid = st.selectbox("Select company", companies.id.tolist(), format_func=lambda x: companies[companies.id==x].iloc[0].name)
    company = companies[companies.id == cid].iloc[0]
    st.subheader(company.name)

    if st.button("Save metadata"):
        companies.loc[companies.id == cid, "name"] = st.session_state.company_name
        save_companies(companies)
        st.success("Updated")

    st.text_input("Company name", key="company_name", value=company.name)

    st.markdown("### Relationships")
    display_edges(cid, "company")

    with st.expander("Add relationship"):
        edge_type = st.selectbox("Type", ["works_for"])
        people = load_people()
        target = st.selectbox("Person", people.id.tolist(), format_func=lambda x: f"{people[people.id==x].iloc[0].first_name} {people[people.id==x].iloc[0].last_name}")
        if st.button("Add edge", key="add_company_edge"):
            edges = load_edges()
            new_id = next_id(edges)
            edges.loc[len(edges)] = [new_id, target, cid, edge_type]
            save_edges(edges)
            st.success("Edge added")


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


def main():
    view = st.sidebar.selectbox("View", ["Search", "Person", "Company", "Create"])
    if view == "Search":
        search_view()
    elif view == "Person":
        person_view()
    elif view == "Company":
        company_view()
    else:
        create_view()


if __name__ == "__main__":
    main()
