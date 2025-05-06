import streamlit as st
import pandas as pd

def display_column_mapper(user_columns, required_columns):
    """
    Display the column mapping interface for the user to match their 
    CSV columns to the required columns for the application.
    
    Args:
        user_columns (list): List of column names from the user's CSV file
        required_columns (dict): Dictionary of required columns with descriptions
        
    Returns:
        tuple: (column_mapping, mapping_complete)
            - column_mapping: Dict mapping required columns to user columns
            - mapping_complete: Boolean indicating if mapping is complete
    """
    st.write("Match your CSV columns to the required fields below:")
    
    # Initialize or use existing column mapping
    column_mapping = {}
    
    # Create three columns
    col1, col2, col3 = st.columns(3)
    
    # Create a row for the preview
    preview_row = st.container()
    
    # Main mapping columns
    with st.container():
        st.subheader("Column Mapping")
        
        # Organize required columns into groups for 3 columns
        column_groups = {
            "1": {
                "Product Identification": ["sku_id", "product_name"],
                "Pricing Data": ["catalog_price", "cost"]
            },
            "2": {
                "Inventory Data": ["at site", "at transit", "at wh"],
                "Sales Data": ["sales_30_days", "sales_60_days", "sales_90_days"]
            },
            "3": {
                "Product Information": ["brands", "category", "seasons", "styles", "size"],
                "Location Data": ["location_name"]
            }
        }
        
        # Process the mapping groups in a single pass
        for col_idx, (col_num, groups) in enumerate(column_groups.items()):
            current_col = [col1, col2, col3][col_idx]
            
            with current_col:
                for group_name, group_columns in groups.items():
                    with st.expander(f"{group_name}", expanded=True):
                        for col_name in group_columns:
                            description = required_columns.get(col_name, {}).get('description', '')
                            is_required = required_columns.get(col_name, {}).get('required', False)
                            
                            # Add label with required indicator if needed
                            label = f"{col_name} {'*' if is_required else ''}"
                            
                            # Default selection logic
                            default_value = None
                            default_index = 0
                            
                            # First check for direct match
                            for user_col in user_columns:
                                if user_col.lower() == col_name.lower():
                                    default_value = user_col
                                    break
                            
                            # If no direct match, check for aliases
                            if default_value is None and 'aliases' in required_columns.get(col_name, {}):
                                aliases = required_columns[col_name]['aliases']
                                for alias in aliases:
                                    for user_col in user_columns:
                                        if user_col.lower() == alias.lower():
                                            default_value = user_col
                                            break
                                    if default_value is not None:
                                        break
                            
                            # Prepare options (including all columns for simplicity to avoid disappearing fields)
                            if is_required:
                                options = user_columns
                            else:
                                options = [""] + user_columns
                            
                            # Set the default index
                            if default_value and default_value in options:
                                default_index = options.index(default_value)
                            
                            # Create the dropdown
                            selected_column = st.selectbox(
                                label,
                                options=options,
                                index=default_index,
                                help=description
                            )
                            
                            # Store the mapping
                            column_mapping[col_name] = selected_column if selected_column != "" else None
    
    # Data preview section (in a separate container below mapping)
    with preview_row:
        with st.expander("📋 Data Preview", expanded=False):
            # Show a preview of the user's data
            if st.session_state.data is not None:
                # First show a sample of the raw data
                st.subheader("Sample Data")
                st.dataframe(st.session_state.data.head(5), use_container_width=True)
                
                # Then show column details to help with mapping
                st.subheader("Column Details")
                dtypes_df = pd.DataFrame({
                    'Column': st.session_state.data.columns,
                    'Data Type': st.session_state.data.dtypes.astype(str),
                    'Sample Values': [
                        str(st.session_state.data[col].dropna().iloc[:3].tolist())[:50] + '...' 
                        if not st.session_state.data[col].dropna().empty else "No non-null values"
                        for col in st.session_state.data.columns
                    ]
                })
                st.dataframe(dtypes_df, use_container_width=True)
    
    # Check if all required fields are mapped
    required_fields = [k for k, v in required_columns.items() if v.get('required', False)]
    all_required_mapped = all(column_mapping.get(field) is not None for field in required_fields)
    
    # Show mapping status
    if all_required_mapped:
        st.success("All required fields are mapped.")
    else:
        missing_fields = [field for field in required_fields if column_mapping.get(field) is None]
        st.warning(f"Please map all required fields: {', '.join(missing_fields)}")
    
    # Button to complete mapping
    mapping_complete = st.button("Continue with this mapping", disabled=not all_required_mapped)
    
    return column_mapping, mapping_complete
