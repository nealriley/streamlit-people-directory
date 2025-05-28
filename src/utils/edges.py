"""
Edge Management Utilities

Handles relationship display and management between people and companies.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
import streamlit as st

class EdgeManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_entity_edges(self, entity_id: int, entity_type: str) -> List[Dict[str, Any]]:
        """Get all edges for a specific entity with resolved names"""
        edges = self.data_manager.load_edges()
        edge_types = self.data_manager.load_edge_types()
        
        # Create edge type lookup
        edge_type_map = {et["name"]: et for et in edge_types}
        
        # Find edges where this entity is involved
        related_edges = edges[(edges["source_id"] == entity_id) | (edges["target_id"] == entity_id)]
        
        resolved_edges = []
        for _, edge in related_edges.iterrows():
            edge_def = edge_type_map.get(edge["type"])
            if not edge_def:
                continue
            
            # Determine if this entity is source or target
            if edge["source_id"] == entity_id:
                # Current entity is source
                target_id = edge["target_id"]
                target_type = edge_def["to_type"]
                target_name = self.data_manager.get_entity_display_name(target_id, target_type)
                direction = "outgoing"
                
                resolved_edges.append({
                    "edge_id": edge["id"],
                    "type": edge["type"],
                    "direction": direction,
                    "other_entity_id": target_id,
                    "other_entity_type": target_type,
                    "other_entity_name": target_name,
                    "relationship_text": f"{edge['type']} → {target_name}"
                })
            else:
                # Current entity is target
                source_id = edge["source_id"]
                source_type = edge_def["from_type"]
                source_name = self.data_manager.get_entity_display_name(source_id, source_type)
                direction = "incoming"
                
                resolved_edges.append({
                    "edge_id": edge["id"],
                    "type": edge["type"],
                    "direction": direction,
                    "other_entity_id": source_id,
                    "other_entity_type": source_type,
                    "other_entity_name": source_name,
                    "relationship_text": f"{source_name} → {edge['type']}"
                })
        
        return resolved_edges
    
    def display_entity_relationships(self, entity_id: int, entity_type: str):
        """Display relationships for an entity in Streamlit"""
        edges = self.get_entity_edges(entity_id, entity_type)
        
        if not edges:
            st.info("No relationships found")
            return
        
        st.subheader("Relationships")
        
        # Group by direction
        outgoing = [e for e in edges if e["direction"] == "outgoing"]
        incoming = [e for e in edges if e["direction"] == "incoming"]
        
        if outgoing:
            st.markdown("**Outgoing Relationships:**")
            for edge in outgoing:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"• {edge['relationship_text']}")
                with col2:
                    if st.button("🗑️", key=f"delete_edge_{edge['edge_id']}", help="Delete relationship"):
                        self._delete_edge(edge['edge_id'])
                        st.rerun()
        
        if incoming:
            st.markdown("**Incoming Relationships:**")
            for edge in incoming:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"• {edge['relationship_text']}")
                with col2:
                    if st.button("🗑️", key=f"delete_edge_incoming_{edge['edge_id']}", help="Delete relationship"):
                        self._delete_edge(edge['edge_id'])
                        st.rerun()
    
    def _delete_edge(self, edge_id: int):
        """Delete an edge by ID"""
        edges = self.data_manager.load_edges()
        edges = edges[edges["id"] != edge_id]
        self.data_manager.save_edges(edges)
    
    def get_available_targets(self, source_id: int, source_type: str, target_type: str) -> List[Tuple[int, str]]:
        """Get available targets for creating relationships"""
        if target_type == "Person":
            people = self.data_manager.load_people()
            if source_type == "Person":
                # Exclude self
                people = people[people["id"] != source_id]
            
            if people.empty:
                return []
            
            return [(row["id"], self.data_manager.get_entity_display_name(row["id"], "Person")) 
                   for _, row in people.iterrows()]
        
        elif target_type == "Company":
            companies = self.data_manager.load_companies()
            if source_type == "Company":
                # Exclude self
                companies = companies[companies["id"] != source_id]
            
            if companies.empty:
                return []
            
            return [(row["id"], self.data_manager.get_entity_display_name(row["id"], "Company")) 
                   for _, row in companies.iterrows()]
        
        return []
    
    def create_relationship_form(self, source_id: int, source_type: str):
        """Create a form to add new relationships"""
        st.subheader("Add New Relationship")
        
        # Get available edge types for this source type
        edge_types = self.data_manager.load_edge_types()
        available_edge_types = [et for et in edge_types if et["from_type"] == source_type]
        
        if not available_edge_types:
            st.warning(f"No edge types available for {source_type}")
            return
        
        # Select edge type
        edge_type_names = [et["name"] for et in available_edge_types]
        selected_edge_type = st.selectbox("Relationship Type", edge_type_names)
        
        if selected_edge_type:
            # Find the selected edge type definition
            edge_def = next(et for et in available_edge_types if et["name"] == selected_edge_type)
            target_type = edge_def["to_type"]
            
            # Get available targets
            targets = self.get_available_targets(source_id, source_type, target_type)
            
            if not targets:
                st.warning(f"No {target_type.lower()}s available to connect to")
                return
            
            # Select target
            target_options = {f"{name} (ID: {tid})": tid for tid, name in targets}
            selected_target_display = st.selectbox("Connect to", list(target_options.keys()))
            
            if selected_target_display:
                target_id = target_options[selected_target_display]
                
                if st.button("Create Relationship"):
                    try:
                        self.data_manager.add_edge(source_id, target_id, selected_edge_type)
                        st.success(f"Created relationship: {selected_edge_type}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating relationship: {str(e)}")
    
    def get_relationship_stats(self) -> Dict[str, int]:
        """Get statistics about relationships"""
        edges = self.data_manager.load_edges()
        edge_types = self.data_manager.load_edge_types()
        
        stats = {
            "total_relationships": len(edges),
            "relationship_types": len(edge_types)
        }
        
        # Count by edge type
        if not edges.empty:
            type_counts = edges["type"].value_counts().to_dict()
            stats["by_type"] = type_counts
        else:
            stats["by_type"] = {}
        
        return stats