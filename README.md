# People Directory - Relationship Management System

A comprehensive Streamlit application for managing people, companies, and their relationships. Built from the ground up with a modular architecture that supports dynamic parameters and custom relationship types.

## Features

### 🏠 Home Page
- System overview with quick statistics
- Global search functionality
- Quick actions for adding people and companies
- Recent activity display
- Navigation hub

### 👥 People Page
- **Search & Browse**: Advanced search across all people fields
- **View Details**: Individual person profiles with editable information
- **Manage Relationships**: Create and view connections between people and companies
- **Add New People**: Form-based person creation with custom parameters

### 🏢 Companies Page
- **Search & Browse**: Search companies by name, industry, and other fields
- **View Details**: Company profiles with editable information
- **Manage Relationships**: Create and view company connections
- **Add New Companies**: Form-based company creation with custom parameters

### ⚙️ Admin Page
- **Edge Types**: Create and manage custom relationship types
- **Parameters**: Add custom fields to people and companies
- **Data Management**: Export data, reset system data
- **System Statistics**: View comprehensive system analytics

## Architecture

### Modular Structure
```
src/
├── data/
│   └── manager.py          # DataManager class for all CSV operations
├── utils/
│   ├── search.py           # SearchEngine for finding people and companies
│   └── edges.py            # EdgeManager for relationship management
└── pages/
    ├── home.py             # Home page implementation
    ├── people.py           # People management page
    ├── companies.py        # Companies management page
    └── admin.py            # Admin interface
```

### Data Storage
- **CSV Files**: All data stored in human-readable CSV format
- **JSON Configuration**: Edge types and parameters stored in JSON
- **Dynamic Schema**: Support for custom fields added via admin interface

## Getting Started

### Prerequisites
- Python 3.12+
- UV package manager (or pip)

### Installation
1. Clone or navigate to the project directory
2. Install dependencies:
   ```bash
   uv sync
   ```

### Running the Application
```bash
uv run streamlit run app.py
```

### Adding Sample Data
To populate the system with example data:
```bash
uv run python add_sample_data.py
```

## Usage Guide

### Managing People
1. Navigate to the **People** page
2. Use the search bar to find existing people
3. Click "View" to see details and relationships
4. Use the "Add Person" tab to create new people
5. Add relationships using the relationship form

### Managing Companies
1. Navigate to the **Companies** page
2. Search for companies using the search functionality
3. View company details and relationships
4. Add new companies with custom parameters
5. Create company-to-company or company-to-person relationships

### Customizing the System
1. Go to the **Admin** page
2. **Edge Types**: Define new relationship types (e.g., "mentors", "suppliers")
3. **Parameters**: Add custom fields to people (e.g., "department") or companies (e.g., "revenue")
4. Changes are immediately available throughout the system

### Data Management
- **Export**: Download all data as a ZIP file from the Admin page
- **Reset**: Clear specific data types or reset the entire system
- **Backup**: Regular exports recommended for data safety

## Default Configuration

### Default Edge Types
- `reports_to`: Person → Person
- `works_for`: Person → Company
- `manages`: Person → Person
- `partners_with`: Company → Company

### Default Person Parameters
- `first_name` (required)
- `last_name` (required)
- `email`
- `phone`

### Default Company Parameters
- `name` (required)
- `industry`
- `website`
- `description`

## Data Files

All data is stored in the `data/` directory:
- `people.csv`: People information
- `companies.csv`: Company information
- `edges.csv`: Relationships between entities
- `edge_types.json`: Relationship type definitions
- `parameters.json`: Custom field definitions

## Development

### Adding New Features
The modular architecture makes it easy to extend:
1. **New Pages**: Add to `pages/` and register in `app.py`
2. **New Utilities**: Add to `src/utils/` for shared functionality
3. **Data Extensions**: Modify `DataManager` for new data operations

### Testing
Run the sample data script to test all functionality:
```bash
uv run python add_sample_data.py
```

## Migration from Original App

This version completely replaces the original `streamlit_app.py` with:
- ✅ Modular, maintainable code structure
- ✅ Enhanced search capabilities
- ✅ Dynamic parameter system
- ✅ Improved user interface
- ✅ Better error handling
- ✅ Comprehensive admin tools

The data format is compatible, but the new parameter system provides much more flexibility.

## Support

For issues or questions:
1. Check the Admin page for system statistics
2. Verify data files in the `data/` directory
3. Review error messages in the Streamlit interface
4. Ensure all dependencies are properly installed