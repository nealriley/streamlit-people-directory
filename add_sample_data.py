"""
Sample Data Script

Adds sample data to the People Directory for testing and demonstration.
"""

import sys
import os
import pandas as pd

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.manager import DataManager

def add_sample_data():
    """Add sample data to the system"""
    print("Adding sample data to People Directory...")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Sample people data
    sample_people = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@techcorp.com",
            "phone": "+1-555-0101"
        },
        {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.johnson@innovate.com",
            "phone": "+1-555-0102"
        },
        {
            "first_name": "Michael",
            "last_name": "Chen",
            "email": "m.chen@techcorp.com",
            "phone": "+1-555-0103"
        },
        {
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "email": "emily@startupxyz.com",
            "phone": "+1-555-0104"
        },
        {
            "first_name": "David",
            "last_name": "Wilson",
            "email": "d.wilson@consulting.com",
            "phone": "+1-555-0105"
        }
    ]
    
    # Sample companies data
    sample_companies = [
        {
            "name": "TechCorp Solutions",
            "industry": "Technology",
            "website": "https://techcorp.com",
            "description": "Leading technology solutions provider"
        },
        {
            "name": "Innovate Industries",
            "industry": "Manufacturing",
            "website": "https://innovate.com",
            "description": "Innovative manufacturing company"
        },
        {
            "name": "StartupXYZ",
            "industry": "Fintech",
            "website": "https://startupxyz.com",
            "description": "Emerging fintech startup"
        },
        {
            "name": "Wilson Consulting",
            "industry": "Consulting",
            "website": "https://wilsonconsulting.com",
            "description": "Strategic business consulting firm"
        }
    ]
    
    # Add people
    print("Adding people...")
    people_ids = []
    for person in sample_people:
        person_id = data_manager.add_person(person)
        people_ids.append(person_id)
        print(f"  Added: {person['first_name']} {person['last_name']} (ID: {person_id})")
    
    # Add companies
    print("\nAdding companies...")
    company_ids = []
    for company in sample_companies:
        company_id = data_manager.add_company(company)
        company_ids.append(company_id)
        print(f"  Added: {company['name']} (ID: {company_id})")
    
    # Add some relationships
    print("\nAdding relationships...")
    
    # John works for TechCorp
    data_manager.add_edge(people_ids[0], company_ids[0], "works_for")
    print(f"  John Doe works for TechCorp Solutions")
    
    # Michael works for TechCorp
    data_manager.add_edge(people_ids[2], company_ids[0], "works_for")
    print(f"  Michael Chen works for TechCorp Solutions")
    
    # Sarah works for Innovate
    data_manager.add_edge(people_ids[1], company_ids[1], "works_for")
    print(f"  Sarah Johnson works for Innovate Industries")
    
    # Emily works for StartupXYZ
    data_manager.add_edge(people_ids[3], company_ids[2], "works_for")
    print(f"  Emily Rodriguez works for StartupXYZ")
    
    # David works for Wilson Consulting
    data_manager.add_edge(people_ids[4], company_ids[3], "works_for")
    print(f"  David Wilson works for Wilson Consulting")
    
    # John reports to Sarah (assuming Sarah is a manager)
    data_manager.add_edge(people_ids[0], people_ids[1], "reports_to")
    print(f"  John Doe reports to Sarah Johnson")
    
    # Michael reports to John
    data_manager.add_edge(people_ids[2], people_ids[0], "reports_to")
    print(f"  Michael Chen reports to John Doe")
    
    print("\n✅ Sample data added successfully!")
    print(f"Added {len(people_ids)} people, {len(company_ids)} companies, and 7 relationships.")
    
    # Display summary
    print("\n📊 Data Summary:")
    people = data_manager.load_people()
    companies = data_manager.load_companies()
    edges = data_manager.load_edges()
    
    print(f"  Total People: {len(people)}")
    print(f"  Total Companies: {len(companies)}")
    print(f"  Total Relationships: {len(edges)}")

if __name__ == "__main__":
    add_sample_data()