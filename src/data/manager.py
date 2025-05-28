"""
Data Manager Module

Handles all CSV file operations and data management for the People Directory app.
Supports dynamic parameters for both people and companies.
"""

import os
import pandas as pd
import json
from typing import Dict, List, Any, Optional
import streamlit as st

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.people_file = os.path.join(data_dir, "people.csv")
        self.companies_file = os.path.join(data_dir, "companies.csv")
        self.edges_file = os.path.join(data_dir, "edges.csv")
        self.edge_types_file = os.path.join(data_dir, "edge_types.json")
        self.parameters_file = os.path.join(data_dir, "parameters.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize default parameters if not exists
        self._initialize_default_parameters()
    
    def _initialize_default_parameters(self):
        """Initialize default parameters for people and companies"""
        if not os.path.exists(self.parameters_file):
            default_params = {
                "people": [
                    {"name": "first_name", "type": "text", "required": True},
                    {"name": "last_name", "type": "text", "required": True},
                    {"name": "email", "type": "text", "required": False},
                    {"name": "phone", "type": "text", "required": False}
                ],
                "companies": [
                    {"name": "name", "type": "text", "required": True},
                    {"name": "industry", "type": "text", "required": False},
                    {"name": "website", "type": "text", "required": False},
                    {"name": "description", "type": "text", "required": False}
                ]
            }
            self.save_parameters(default_params)
    
    @st.cache_data
    def load_people(_self) -> pd.DataFrame:
        """Load people data from CSV"""
        if not os.path.exists(_self.people_file):
            params = _self.load_parameters()["people"]
            columns = ["id"] + [p["name"] for p in params]
            return pd.DataFrame(columns=columns)
        
        df = pd.read_csv(_self.people_file)
        if not df.empty and "id" in df.columns:
            df["id"] = df["id"].astype(int)
        return df
    
    @st.cache_data
    def load_companies(_self) -> pd.DataFrame:
        """Load companies data from CSV"""
        if not os.path.exists(_self.companies_file):
            params = _self.load_parameters()["companies"]
            columns = ["id"] + [p["name"] for p in params]
            return pd.DataFrame(columns=columns)
        
        df = pd.read_csv(_self.companies_file)
        if not df.empty and "id" in df.columns:
            df["id"] = df["id"].astype(int)
        return df
    
    @st.cache_data
    def load_edges(_self) -> pd.DataFrame:
        """Load edges data from CSV"""
        if not os.path.exists(_self.edges_file):
            return pd.DataFrame(columns=["id", "source_id", "target_id", "type"])
        
        df = pd.read_csv(_self.edges_file)
        if not df.empty:
            df["id"] = df["id"].astype(int)
            df["source_id"] = df["source_id"].astype(int)
            df["target_id"] = df["target_id"].astype(int)
        return df
    
    @st.cache_data
    def load_edge_types(_self) -> List[Dict[str, str]]:
        """Load edge types from JSON"""
        if os.path.exists(_self.edge_types_file):
            with open(_self.edge_types_file, 'r') as f:
                return json.load(f)
        else:
            # Default edge types
            default_types = [
                {"name": "reports_to", "from_type": "Person", "to_type": "Person"},
                {"name": "works_for", "from_type": "Person", "to_type": "Company"},
                {"name": "manages", "from_type": "Person", "to_type": "Person"},
                {"name": "partners_with", "from_type": "Company", "to_type": "Company"}
            ]
            _self.save_edge_types(default_types)
            return default_types
    
    @st.cache_data
    def load_parameters(_self) -> Dict[str, List[Dict[str, Any]]]:
        """Load parameter definitions for people and companies"""
        if os.path.exists(_self.parameters_file):
            with open(_self.parameters_file, 'r') as f:
                return json.load(f)
        else:
            _self._initialize_default_parameters()
            with open(_self.parameters_file, 'r') as f:
                return json.load(f)
    
    def save_people(self, df: pd.DataFrame):
        """Save people data to CSV and clear cache"""
        df.to_csv(self.people_file, index=False)
        self.load_people.clear()
    
    def save_companies(self, df: pd.DataFrame):
        """Save companies data to CSV and clear cache"""
        df.to_csv(self.companies_file, index=False)
        self.load_companies.clear()
    
    def save_edges(self, df: pd.DataFrame):
        """Save edges data to CSV and clear cache"""
        df.to_csv(self.edges_file, index=False)
        self.load_edges.clear()
    
    def save_edge_types(self, edge_types: List[Dict[str, str]]):
        """Save edge types to JSON and clear cache"""
        with open(self.edge_types_file, 'w') as f:
            json.dump(edge_types, f, indent=2)
        self.load_edge_types.clear()
    
    def save_parameters(self, parameters: Dict[str, List[Dict[str, Any]]]):
        """Save parameter definitions to JSON and clear cache"""
        with open(self.parameters_file, 'w') as f:
            json.dump(parameters, f, indent=2)
        self.load_parameters.clear()
    
    def get_next_id(self, df: pd.DataFrame) -> int:
        """Get the next available ID for a dataframe"""
        if df.empty or "id" not in df.columns:
            return 1
        return int(df["id"].max()) + 1
    
    def get_valid_edge_types(self, from_type: str, to_type: str) -> List[str]:
        """Get valid edge types for given from and to types"""
        edge_types = self.load_edge_types()
        return [et["name"] for et in edge_types 
                if et["from_type"] == from_type and et["to_type"] == to_type]
    
    def get_person_by_id(self, person_id: int) -> Optional[pd.Series]:
        """Get a person by ID"""
        people = self.load_people()
        matches = people[people["id"] == person_id]
        return matches.iloc[0] if not matches.empty else None
    
    def get_company_by_id(self, company_id: int) -> Optional[pd.Series]:
        """Get a company by ID"""
        companies = self.load_companies()
        matches = companies[companies["id"] == company_id]
        return matches.iloc[0] if not matches.empty else None
    
    def add_person(self, person_data: Dict[str, Any]) -> int:
        """Add a new person and return their ID"""
        people = self.load_people()
        new_id = self.get_next_id(people)
        person_data["id"] = new_id
        
        # Ensure all required columns exist
        params = self.load_parameters()["people"]
        for param in params:
            if param["name"] not in person_data:
                person_data[param["name"]] = ""
        
        new_row = pd.DataFrame([person_data])
        people = pd.concat([people, new_row], ignore_index=True)
        self.save_people(people)
        return new_id
    
    def add_company(self, company_data: Dict[str, Any]) -> int:
        """Add a new company and return their ID"""
        companies = self.load_companies()
        new_id = self.get_next_id(companies)
        company_data["id"] = new_id
        
        # Ensure all required columns exist
        params = self.load_parameters()["companies"]
        for param in params:
            if param["name"] not in company_data:
                company_data[param["name"]] = ""
        
        new_row = pd.DataFrame([company_data])
        companies = pd.concat([companies, new_row], ignore_index=True)
        self.save_companies(companies)
        return new_id
    
    def add_edge(self, source_id: int, target_id: int, edge_type: str) -> int:
        """Add a new edge and return its ID"""
        edges = self.load_edges()
        new_id = self.get_next_id(edges)
        new_row = pd.DataFrame([{
            "id": new_id,
            "source_id": source_id,
            "target_id": target_id,
            "type": edge_type
        }])
        edges = pd.concat([edges, new_row], ignore_index=True)
        self.save_edges(edges)
        return new_id
    
    def update_person(self, person_id: int, updates: Dict[str, Any]):
        """Update a person's data"""
        people = self.load_people()
        for field, value in updates.items():
            if field in people.columns:
                people.loc[people["id"] == person_id, field] = value
        self.save_people(people)
    
    def update_company(self, company_id: int, updates: Dict[str, Any]):
        """Update a company's data"""
        companies = self.load_companies()
        for field, value in updates.items():
            if field in companies.columns:
                companies.loc[companies["id"] == company_id, field] = value
        self.save_companies(companies)
    
    def add_parameter(self, entity_type: str, param_name: str, param_type: str, required: bool = False):
        """Add a new parameter to people or companies"""
        parameters = self.load_parameters()
        
        if entity_type not in parameters:
            parameters[entity_type] = []
        
        # Check if parameter already exists
        existing = [p for p in parameters[entity_type] if p["name"] == param_name]
        if existing:
            return False  # Parameter already exists
        
        parameters[entity_type].append({
            "name": param_name,
            "type": param_type,
            "required": required
        })
        
        self.save_parameters(parameters)
        
        # Add column to existing data if it doesn't exist
        if entity_type == "people":
            people = self.load_people()
            if param_name not in people.columns:
                people[param_name] = ""
                self.save_people(people)
        elif entity_type == "companies":
            companies = self.load_companies()
            if param_name not in companies.columns:
                companies[param_name] = ""
                self.save_companies(companies)
        
        return True
    
    def get_entity_display_name(self, entity_id: int, entity_type: str) -> str:
        """Get display name for an entity"""
        if entity_type == "Person":
            person = self.get_person_by_id(entity_id)
            if person is not None:
                return f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
        elif entity_type == "Company":
            company = self.get_company_by_id(entity_id)
            if company is not None:
                return company.get('name', '')
        return f"Unknown {entity_type} (ID: {entity_id})"