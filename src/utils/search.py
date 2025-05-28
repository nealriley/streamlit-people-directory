"""
Search and Filter Utilities

Provides search functionality for people and companies.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
import streamlit as st

class SearchEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def search_people(self, query: str) -> pd.DataFrame:
        """Search people by name, email, or other fields"""
        if not query:
            return pd.DataFrame()
        
        people = self.data_manager.load_people()
        if people.empty:
            return pd.DataFrame()
        
        query_lower = query.lower()
        matches = pd.DataFrame()
        
        # Search in text fields
        text_columns = ["first_name", "last_name", "email", "phone"]
        for col in text_columns:
            if col in people.columns:
                col_matches = people[people[col].astype(str).str.lower().str.contains(query_lower, na=False)]
                matches = pd.concat([matches, col_matches]).drop_duplicates()
        
        # Special case for full name search
        if "first_name" in people.columns and "last_name" in people.columns:
            people["full_name"] = people["first_name"].astype(str) + " " + people["last_name"].astype(str)
            full_name_matches = people[people["full_name"].str.lower().str.contains(query_lower, na=False)]
            matches = pd.concat([matches, full_name_matches]).drop_duplicates()
        
        return matches.reset_index(drop=True)
    
    def search_companies(self, query: str) -> pd.DataFrame:
        """Search companies by name, industry, or other fields"""
        if not query:
            return pd.DataFrame()
        
        companies = self.data_manager.load_companies()
        if companies.empty:
            return pd.DataFrame()
        
        query_lower = query.lower()
        matches = pd.DataFrame()
        
        # Search in text fields
        text_columns = ["name", "industry", "website", "description"]
        for col in text_columns:
            if col in companies.columns:
                col_matches = companies[companies[col].astype(str).str.lower().str.contains(query_lower, na=False)]
                matches = pd.concat([matches, col_matches]).drop_duplicates()
        
        return matches.reset_index(drop=True)
    
    def search_all(self, query: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Search both people and companies"""
        people_matches = self.search_people(query)
        company_matches = self.search_companies(query)
        return people_matches, company_matches
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> Dict[str, List[str]]:
        """Get search suggestions based on partial query"""
        suggestions = {"people": [], "companies": []}
        
        if len(query) < 2:
            return suggestions
        
        people = self.data_manager.load_people()
        companies = self.data_manager.load_companies()
        
        # People suggestions
        if not people.empty and "first_name" in people.columns and "last_name" in people.columns:
            people["full_name"] = people["first_name"].astype(str) + " " + people["last_name"].astype(str)
            query_lower = query.lower()
            matching_people = people[people["full_name"].str.lower().str.startswith(query_lower)]
            suggestions["people"] = matching_people["full_name"].head(limit).tolist()
        
        # Company suggestions
        if not companies.empty and "name" in companies.columns:
            query_lower = query.lower()
            matching_companies = companies[companies["name"].astype(str).str.lower().str.startswith(query_lower)]
            suggestions["companies"] = matching_companies["name"].head(limit).tolist()
        
        return suggestions