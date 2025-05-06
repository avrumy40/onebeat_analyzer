import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import os
import base64
from datetime import datetime

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Inventory Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Force sidebar to be collapsed initially
)

# Import language utils before any UI rendering
from modules.language_utils import get_text, language_selector, initialize_language, get_language

# Initialize language settings
initialize_language()

# Apply custom styling from CSS file
def load_css():
    try:
        with open('.streamlit/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Create directory if it doesn't exist
        os.makedirs('.streamlit', exist_ok=True)
        # Create a basic CSS file
        with open('.streamlit/style.css', 'w') as f:
            f.write("""
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size: 18px;
            }
            .main-header {
                color: #1A314B;
            }
            .metric-card {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
                background-color: #fbfbfb;
            }
            .metric-label {
                font-size: 16px;
                color: #666;
            }
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                color: #1F6C6D;
            }
            .negative-value {
                color: #FD604A;
            }
            .positive-value {
                color: #1F6C6D;
            }
            """)
        load_css()

# Load the custom CSS
load_css()

from modules.data_processor import process_data, validate_data, aggregate_inventory_by_location, calculate_inventory_targets, calculate_redistribution_metrics
from modules.hbt_analyzer import perform_hbt_analysis, calculate_kpis
from modules.column_mapper import display_column_mapper
from modules.visualization import (
    plot_cumulative_graph, 
    plot_hbt_distribution, 
    create_inventory_location_chart,
    plot_sales_trends,
    create_inventory_distribution_chart,
    create_store_comparison_chart,
    create_store_hbt_comparison
)
from modules.utils import download_csv, format_currency
from config.app_config import REQUIRED_COLUMNS, APP_TITLE, APP_DESCRIPTION

# Initialize session state variables if they don't exist
if 'data' not in st.session_state:
    st.session_state.data = None
if 'mapping_complete' not in st.session_state:
    st.session_state.mapping_complete = False
if 'mapped_data' not in st.session_state:
    st.session_state.mapped_data = None
if 'hbt_results' not in st.session_state:
    st.session_state.hbt_results = None
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'categories': [],
        'locations': [],
        'brands': [],
        'seasons': [],
        'styles': [],
        'size': [],
        'department': [],
        'inventory_status': 'All Products',
        'sales_performance': 'All'
    }
if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = {}
if 'lead_time_days' not in st.session_state:
    st.session_state.lead_time_days = 7  # Default replenishment lead time
if 'filtering_stats' not in st.session_state:
    st.session_state.filtering_stats = None

# App title and description
st.title(get_text("app_title"))

# Only show the welcome description and file uploader if mapping is not complete
if not st.session_state.mapping_complete:
    st.markdown(f"""
    {get_text("welcome_text")}
    """)
    
    # Updated instruction text
    st.markdown(f"""
    ### {get_text("get_started")}
    """)
    
    # File uploader in the center at the top - but aligned left like the text
    uploaded_file = st.file_uploader(get_text("upload_csv"), type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the uploaded CSV file
            data = pd.read_csv(uploaded_file)
            st.session_state.data = data
            # Store data dimensions in session state but don't display
            st.session_state.data_dimensions = {
                'rows': data.shape[0],
                'columns': data.shape[1]
            }
            st.success(f"{get_text('data_loaded')} {data.shape[0]:,} rows and {data.shape[1]} columns.")
        except Exception as e:
            st.error(f"{get_text('invalid_file')} {e}")
else:
    # Autoscroll to top of page using HTML/JavaScript with a more robust implementation
    st.markdown("""
    <script>
        // Function to scroll to the top
        function scrollToTop() {
            window.scrollTo(0, 0);
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        }
        
        // Call immediately and with increasing delays to ensure it works in all browsers
        scrollToTop();
        setTimeout(scrollToTop, 100);
        setTimeout(scrollToTop, 300);
        setTimeout(scrollToTop, 600);
        setTimeout(scrollToTop, 1000);
    </script>
    """, unsafe_allow_html=True)

# Store in session state that we've already set page config
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "set"

# Sidebar for filters (collapsed by default)
with st.sidebar:
    # Language selector at the top of sidebar
    language_selector()
    # Display filters only after data is loaded and mapped
    if st.session_state.mapping_complete and st.session_state.mapped_data is not None:
        # Get unique values for each filter from the mapped data
        mapped_data = st.session_state.mapped_data
        
        # Handle the case where mapped_data is a tuple or other non-DataFrame object
        if not hasattr(mapped_data, 'columns'):
            if isinstance(mapped_data, tuple) and len(mapped_data) > 0 and hasattr(mapped_data[0], 'columns'):
                # If it's a tuple with a DataFrame as first element, use that
                mapped_data = mapped_data[0]
            else:
                # Skip filter section if we don't have a proper DataFrame
                st.warning("Data format issue detected. Filters may not be available.")
                mapped_data = pd.DataFrame()  # Empty DataFrame to avoid errors
        
        st.header(f"🔍 {get_text('sidebar_title')}")
        # Always use expander and set expanded=False to collapse by default
        with st.expander(get_text("filter_options"), expanded=False):
            # Category filter
            if hasattr(mapped_data, 'columns') and 'category' in mapped_data.columns:
                all_categories = sorted(mapped_data['category'].unique().tolist())
                selected_categories = st.multiselect(get_text("product_categories"), all_categories, default=[])
                if selected_categories:
                    st.session_state.filters['categories'] = selected_categories
                else:
                    st.session_state.filters['categories'] = []
            
            # Location filter
            if hasattr(mapped_data, 'columns') and 'location_name' in mapped_data.columns:
                all_locations = sorted(mapped_data['location_name'].unique().tolist())
                selected_locations = st.multiselect(get_text("locations"), all_locations, default=[])
                if selected_locations:
                    st.session_state.filters['locations'] = selected_locations
                else:
                    st.session_state.filters['locations'] = []
            
            # Brand filter (if available)
            if hasattr(mapped_data, 'columns') and 'brand' in mapped_data.columns:
                all_brands = sorted(mapped_data['brand'].unique().tolist())
                selected_brands = st.multiselect(get_text("brands"), all_brands, default=[])
                if selected_brands:
                    st.session_state.filters['brands'] = selected_brands
                else:
                    st.session_state.filters['brands'] = []
                    
            # Apply filters button
            if st.button(get_text("apply_filters")):
                # Filter the data based on selected filters
                if hasattr(mapped_data, 'copy'):
                    filtered_data = mapped_data.copy()
                else:
                    filtered_data = mapped_data
                
                if st.session_state.filters['categories']:
                    filtered_data = filtered_data[filtered_data['category'].isin(st.session_state.filters['categories'])]
                
                if st.session_state.filters['locations']:
                    filtered_data = filtered_data[filtered_data['location_name'].isin(st.session_state.filters['locations'])]
                
                if st.session_state.filters['brands'] and 'brand' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['brand'].isin(st.session_state.filters['brands'])]
                
                # Update the mapped_data with filtered data
                st.session_state.mapped_data = filtered_data
                
                # Calculate filtering stats
                total_rows = mapped_data.shape[0]
                filtered_rows = filtered_data.shape[0]
                percentage = (filtered_rows / total_rows) * 100 if total_rows > 0 else 0
                
                st.session_state.filtering_stats = {
                    'total_rows': total_rows,
                    'filtered_rows': filtered_rows,
                    'percentage': percentage
                }
                
                # Recalculate HBT analysis with filtered data
                st.session_state.hbt_results = perform_hbt_analysis(filtered_data)
                
                # Use the filters_applied translation with formatting
                formatted_message = get_text("filters_applied").format(f"{filtered_rows:,}", f"{total_rows:,}", f"{percentage:.1f}")
                st.success(formatted_message)
            
            # Reset filters button
            if st.button(get_text("reset_filters")):
                # Reset all filters
                st.session_state.filters = {
                    'categories': [],
                    'locations': [],
                    'brands': [],
                    'seasons': [],
                    'styles': [],
                    'size': [],
                    'department': [],
                    'inventory_status': 'All Products',
                    'sales_performance': 'All'
                }
                
                # Reset to original mapped data
                if 'original_mapped_data' in st.session_state:
                    original_data = st.session_state.original_mapped_data
                    if hasattr(original_data, 'copy'):
                        st.session_state.mapped_data = original_data.copy()
                    else:
                        st.session_state.mapped_data = original_data
                
                # Recalculate HBT analysis with original data
                st.session_state.hbt_results = perform_hbt_analysis(st.session_state.mapped_data)
                
                st.session_state.filtering_stats = None
                
                st.success(get_text("filters_reset"))

# Main content
if st.session_state.data is not None:
    if not st.session_state.mapping_complete:
        # Show column mapping interface
        st.header(get_text("mapping_title"))
        st.markdown(f"""
        {get_text("mapping_instructions")}
        {get_text("mapping_help")}
        """)
        
        column_mapping, mapping_complete = display_column_mapper(
            st.session_state.data.columns.tolist(),
            REQUIRED_COLUMNS
        )
        
        # Update session state with mapping results
        st.session_state.column_mapping = column_mapping
        st.session_state.mapping_complete = mapping_complete
        
        if mapping_complete:
            # Process the data using the column mapping
            mapped_data = process_data(st.session_state.data, column_mapping)
            
            # Store both the original and current mapped data
            st.session_state.mapped_data = mapped_data
            # Make sure mapped_data is a DataFrame before copying
            if hasattr(mapped_data, 'copy'):
                st.session_state.original_mapped_data = mapped_data.copy()
            else:
                st.session_state.original_mapped_data = mapped_data
            
            # Perform HBT analysis
            st.session_state.hbt_results = perform_hbt_analysis(mapped_data)
            
            # Add JavaScript to scroll to top of page with a more robust implementation
            st.markdown("""
            <script>
                // Function to scroll to the top
                function scrollToTop() {
                    window.scrollTo(0, 0);
                    document.body.scrollTop = 0;
                    document.documentElement.scrollTop = 0;
                }
                
                // Call immediately and with increasing delays to ensure it works in all browsers
                scrollToTop();
                setTimeout(scrollToTop, 100);
                setTimeout(scrollToTop, 300);
                setTimeout(scrollToTop, 600);
                setTimeout(scrollToTop, 1000);
            </script>
            """, unsafe_allow_html=True)
            
            st.success(get_text("mapping_complete"))
            st.rerun()
    else:
        # Display tabs for different analyses
        tab1, tab2, tab3 = st.tabs([get_text("hbt_analysis"), get_text("misdistribution"), get_text("store_analysis")])
        
        # Get the mapped data from session state
        mapped_data = st.session_state.mapped_data
        
        # Handle the case where mapped_data is a tuple or other non-DataFrame object
        if not hasattr(mapped_data, 'columns'):
            if isinstance(mapped_data, tuple) and len(mapped_data) > 0 and hasattr(mapped_data[0], 'columns'):
                # If it's a tuple with a DataFrame as first element, use that
                mapped_data = mapped_data[0]
            else:
                # Use an empty DataFrame as fallback if we can't determine what to do
                import pandas as pd
                st.warning("Data format issue detected. Please retry column mapping.")
                mapped_data = pd.DataFrame()
        
        # Tab 1: HBT Analysis
        with tab1:
            st.header(get_text("hbt_title"))
            
            # Attempt to scroll to top when switching to this tab
            st.markdown("""
            <script>
                // Function to scroll to the top
                function scrollToTop() {
                    window.scrollTo(0, 0);
                    document.body.scrollTop = 0;
                    document.documentElement.scrollTop = 0;
                }
                
                // Call immediately and with increasing delays to ensure it works in all browsers
                scrollToTop();
                setTimeout(scrollToTop, 100);
                setTimeout(scrollToTop, 300);
                setTimeout(scrollToTop, 600);
                setTimeout(scrollToTop, 1000);
            </script>
            """, unsafe_allow_html=True)
            
            if st.session_state.hbt_results is not None:
                # Create columns for KPIs
                col1, col2, col3 = st.columns(3)
                
                # Calculate KPIs
                kpis = calculate_kpis(st.session_state.hbt_results, mapped_data)
                
                with col1:
                    st.metric(
                        f"{get_text('head')} SKUs",
                        f"{kpis['head_product_percentage']:.1f}%",
                        help="Percentage of SKUs that generate 30% of total sales"
                    )
                
                with col2:
                    st.metric(
                        f"{get_text('tail')} {get_text('inventory')} {get_text('cost')}",
                        f"${kpis['tail_inventory_cost']:,.0f}",  # No decimal places
                        help="Total inventory cost tied up in tail SKUs"
                    )
                
                with col3:
                    st.metric(
                        f"{get_text('head')} {get_text('total_availability')}",
                        f"{kpis['head_availability']:.1f}%",
                        help="Percentage of head SKUs that are in stock"
                    )
                
                # Cumulative sales vs inventory graph
                st.subheader(get_text("cumulative_graph"))
                cumulative_graph = plot_cumulative_graph(st.session_state.hbt_results)
                st.plotly_chart(cumulative_graph, use_container_width=True, config={'displayModeBar': False})
                
                # HBT Distribution chart
                st.subheader(get_text("hbt_distribution"))
                hbt_chart = plot_hbt_distribution(st.session_state.hbt_results)
                st.plotly_chart(hbt_chart, use_container_width=True, config={'displayModeBar': False})
                
                # Display the HBT classification data
                st.subheader(get_text("product_list"))
                
                # Prepare the data for display
                classification_df = st.session_state.hbt_results['product_classification'].copy()
                
                # Make a copy of the classification dataframe with some aggregation
                if 'product_name' in classification_df.columns:
                    # Group by product name and calculate aggregates
                    product_summary = classification_df.groupby(['product_name', 'hbt_class']).agg({
                        'sales_value': 'sum',
                        'inventory_value': 'sum'
                        # Removed 'hbt_class': 'first' since it's already in the index
                    }).reset_index()
                    
                    # Sort by sales value descending
                    product_summary = product_summary.sort_values('sales_value', ascending=False)
                    
                    # Display the product summary in a DataFrame
                    display_cols = ['product_name', 'hbt_class', 'sales_value', 'inventory_value']
                    
                    # Check and filter columns that exist
                    display_cols = [col for col in display_cols if col in product_summary.columns]
                    
                    # Rename columns for better display
                    rename_dict = {
                        'product_name': 'Product',
                        'hbt_class': 'Classification',
                        'sales_value': 'Sales Value',
                        'inventory_value': 'Inventory Value'
                    }
                    
                    # Only include columns that exist in the display_cols
                    product_summary_display = product_summary[display_cols].rename(
                        columns={k: v for k, v in rename_dict.items() if k in display_cols}
                    )
                    
                    # Format currency values without decimal places
                    if 'Sales Value' in product_summary_display.columns:
                        product_summary_display['Sales Value'] = product_summary_display['Sales Value'].apply(
                            lambda x: f"${x:,.0f}"  # No decimal places
                        )
                    if 'Inventory Value' in product_summary_display.columns:
                        product_summary_display['Inventory Value'] = product_summary_display['Inventory Value'].apply(
                            lambda x: f"${x:,.0f}"  # No decimal places
                        )
                    
                    # Add color-coding to the HBT classification using Pandas styling
                    # Instead of using HTML, we'll use pandas styling directly
                    styled_summary = product_summary_display.style
                    
                    # Define a styling function
                    def highlight_hbt(val):
                        if val == 'Head':
                            return 'background-color: #1F6C6D; color: white; font-weight: bold; border-radius: 8px; padding: 4px 8px; text-align: center;'
                        elif val == 'Tail':
                            return 'background-color: #FD604A; color: white; font-weight: bold; border-radius: 8px; padding: 4px 8px; text-align: center;'
                        else:  # Belly
                            return 'background-color: #E8BFE6; color: #1A314B; font-weight: bold; border-radius: 8px; padding: 4px 8px; text-align: center;'
                    
                    # Apply the styling
                    styled_summary = styled_summary.applymap(
                        highlight_hbt, subset=['Classification']
                    )
                    
                    # Show the styled DataFrame with a class to help target CSS
                    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                    st.dataframe(styled_summary, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download button for the product classification data
                    st.download_button(
                        label=get_text("download_full_report"),
                        data=download_csv(product_summary_display),
                        file_name=f"hbt_classification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        # Tab 2: Misdistribution Analysis
        with tab2:
            st.header(get_text("misdistribution_title"))
            
            # Attempt to scroll to top when switching to this tab
            st.markdown("""
            <script>
                // Function to scroll to the top
                function scrollToTop() {
                    window.scrollTo(0, 0);
                    document.body.scrollTop = 0;
                    document.documentElement.scrollTop = 0;
                }
                
                // Call immediately and with increasing delays to ensure it works in all browsers
                scrollToTop();
                setTimeout(scrollToTop, 100);
                setTimeout(scrollToTop, 300);
                setTimeout(scrollToTop, 600);
                setTimeout(scrollToTop, 1000);
            </script>
            """, unsafe_allow_html=True)
            
            # Lead time input for inventory target calculation
            lead_time = st.number_input(
                get_text("lead_time_days"),
                min_value=1,
                max_value=180,
                value=st.session_state.lead_time_days,
                help="Enter the typical number of days it takes to restock inventory"
            )
            
            # Update session state if value changed
            if lead_time != st.session_state.lead_time_days:
                st.session_state.lead_time_days = lead_time
                st.info(get_text("lead_time_updated"))
                # Force a rerun to update all other tabs with the new lead time
                st.rerun()
            
            # Calculate inventory targets based on lead time
            with st.spinner("Calculating inventory targets..."):
                try:
                    target_data = calculate_inventory_targets(mapped_data, lead_time)
                    
                    # Create main metrics
                    st.subheader(get_text("misdistribution_metrics"))
                    
                    # Calculate standard metrics
                    total_units = target_data['at site'].sum()
                    total_target = target_data['inventory_target'].sum()
                    total_gap = target_data['inventory_gap'].sum()
                    
                    # Calculate advanced redistribution metrics
                    redistribution_metrics = calculate_redistribution_metrics(target_data)
                    
                    # First row of metrics - Basic inventory metrics
                    st.markdown("##### Basic Inventory Metrics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            get_text("current_inventory"),
                            f"{int(total_units):,} units",
                            help="Total units currently at all store locations"
                        )
                    with col2:
                        st.metric(
                            get_text("target_inventory"),
                            f"{int(total_target):,} units",
                            help="Total units needed based on sales patterns and lead time"
                        )
                    with col3:
                        # Calculate total surplus (Current Inventory - Target Inventory, when positive)
                        total_surplus = target_data['inventory_surplus'].sum()
                        st.metric(
                            get_text("inventory_surplus"),
                            f"{int(total_surplus):,} units",
                            help="Total excess inventory above target levels"
                        )
                    
                    # Second row of metrics - Availability metrics
                    st.markdown("##### Availability Metrics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Total Availability",
                            f"{redistribution_metrics['total_availability']:.1f}%",
                            help="Percentage of SKUs that are in stock (at site > 0)"
                        )
                    
                    # Only show WH metrics if warehouse data is available
                    if redistribution_metrics['depleted_wh_availability'] is not None:
                        with col2:
                            st.metric(
                                "Availability for Depleted WH",
                                f"{redistribution_metrics['depleted_wh_availability']:.1f}%",
                                help="Percentage of products with no WH stock that are available at stores"
                            )
                        with col3:
                            st.metric(
                                "WH Replenishment Potential",
                                f"{redistribution_metrics['wh_potential']:.1f}%",
                                help="Percentage of stockouts that could be fixed with WH inventory"
                            )
                    
                    # Third row of metrics - Redistribution potential
                    st.markdown("##### Redistribution Potential")
                    col1, col2, col3 = st.columns(3)
                    
                    # Store redistribution (only if multiple locations)
                    if redistribution_metrics['store_redistribution_potential'] is not None:
                        with col1:
                            st.metric(
                                "Store Redistribution Potential",
                                f"{redistribution_metrics['store_redistribution_potential']:.1f}%",
                                help="Percentage of depleted warehouse stockouts that could be fixed with surplus from other stores"
                            )
                    
                    # Sales increase potentials
                    if redistribution_metrics['potential_wh_sales_increase'] is not None:
                        with col2:
                            st.metric(
                                "Potential Sales from WH",
                                f"+{redistribution_metrics['potential_wh_sales_increase']:.1f}%",
                                help="Potential sales increase from WH replenishment"
                            )
                    
                    if redistribution_metrics['potential_store_sales_increase'] is not None:
                        with col3:
                            st.metric(
                                "Potential Sales from Stores",
                                f"+{redistribution_metrics['potential_store_sales_increase']:.1f}%",
                                help="Potential sales increase from store-to-store redistribution"
                            )
                    
                    # Inventory Distribution Chart
                    st.subheader("Inventory Distribution by SKU-Location")
                    st.markdown("""
                    This chart shows the distribution of SKU-Locations with different inventory levels
                    and their corresponding targets.
                    """)
                    
                    # Create the inventory distribution chart
                    max_count = st.slider("Maximum inventory count to show", 
                                         min_value=5, max_value=50, value=20, 
                                         help="Adjust to see different ranges of inventory levels")
                    
                    distribution_chart = create_inventory_distribution_chart(target_data, max_count)
                    st.plotly_chart(distribution_chart, use_container_width=True, config={'displayModeBar': False})
                    
                    # Table showing SKU-Location level data
                    st.subheader("SKU-Location Inventory Targets")
                    
                    # Search functionality
                    search_sku = st.text_input("Search for SKUs or locations", key="target_search")
                    
                    # Prepare display columns
                    display_cols = [
                        'sku_id', 'product_name', 'location_name',
                        'sales_30_days', 'sales_60_days', 'sales_90_days',
                        'at site', 'inventory_target', 'inventory_gap', 'inventory_surplus', 'target_percentage'
                    ]
                    
                    # Filter columns to only include existing ones
                    display_cols = [col for col in display_cols if col in target_data.columns]
                    table_data = target_data[display_cols].copy()
                    
                    # Better column names for display
                    column_rename = {
                        'sku_id': 'SKU',
                        'product_name': 'Product',
                        'location_name': 'Location',
                        'sales_30_days': 'Sales (30d)',
                        'sales_60_days': 'Sales (60d)',
                        'sales_90_days': 'Sales (90d)',
                        'at site': 'Current Stock',
                        'inventory_target': 'Target Stock',
                        'inventory_gap': 'Stock Gap',
                        'inventory_surplus': 'Surplus',
                        'target_percentage': '% of Target'
                    }
                    table_data = table_data.rename(columns={k: v for k, v in column_rename.items() if k in table_data.columns})
                    
                    # Apply search filter if provided
                    if search_sku:
                        # Build a combined filter across multiple columns
                        search_cols = ['SKU', 'Product', 'Location']
                        filter_mask = pd.Series(False, index=table_data.index)
                        
                        for col in search_cols:
                            if col in table_data.columns:
                                filter_mask = filter_mask | table_data[col].astype(str).str.contains(search_sku, case=False)
                        
                        table_data = table_data[filter_mask]
                    
                    # Determine sort order
                    sort_by = st.radio(
                        "Sort by:",
                        ["Stock Gap (largest first)", "Surplus (largest first)", "% of Target (smallest first)", "Sales (largest first)"],
                        horizontal=True
                    )
                    
                    if sort_by == "Stock Gap (largest first)":
                        table_data = table_data.sort_values("Stock Gap", ascending=False)
                    elif sort_by == "Surplus (largest first)":
                        table_data = table_data.sort_values("Surplus", ascending=False)
                    elif sort_by == "% of Target (smallest first)":
                        table_data = table_data.sort_values("% of Target", ascending=True)
                    else:  # Sort by sales
                        if "Sales (90d)" in table_data.columns:
                            table_data = table_data.sort_values("Sales (90d)", ascending=False)
                    
                    # Display the data with formatting
                    st.dataframe(
                        table_data.style.format({
                            'Sales (30d)': '{:.0f}',
                            'Sales (60d)': '{:.0f}',
                            'Sales (90d)': '{:.0f}',
                            'Current Stock': '{:.0f}',
                            'Target Stock': '{:.0f}',
                            'Stock Gap': '{:.0f}',
                            'Surplus': '{:.0f}',
                            '% of Target': '{:.1f}%'
                        }).background_gradient(
                            subset=['% of Target'],
                            cmap='RdYlGn',
                            vmin=0,
                            vmax=200
                        ),
                        height=400,
                        use_container_width=True
                    )
                    
                    # Download button for the table data
                    st.download_button(
                        label=get_text("download_full_report"),
                        data=download_csv(table_data),
                        file_name=f"misdistribution_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"Error calculating inventory targets: {e}")
                    st.code(str(e))
        
        # Tab 3: Store Analysis
        with tab3:
            st.header(get_text("store_title"))
            
            # Attempt to scroll to top when switching to this tab
            st.markdown("""
            <script>
                // Function to scroll to the top
                function scrollToTop() {
                    window.scrollTo(0, 0);
                    document.body.scrollTop = 0;
                    document.documentElement.scrollTop = 0;
                }
                
                // Call immediately and with increasing delays to ensure it works in all browsers
                scrollToTop();
                setTimeout(scrollToTop, 100);
                setTimeout(scrollToTop, 300);
                setTimeout(scrollToTop, 600);
                setTimeout(scrollToTop, 1000);
            </script>
            """, unsafe_allow_html=True)
            
            # Show the current lead time value from session state with timestamp to show updates
            current_time = datetime.now().strftime('%H:%M:%S')
            st.info(f"{get_text('lead_time_days')}: {st.session_state.lead_time_days} {get_text('days')} ({get_text('last_updated')} {current_time})")

            try:
                # Check if location_name column exists
                if 'location_name' not in mapped_data.columns:
                    st.warning("Location information is missing. Store analysis requires location data.")
                else:
                    # Get unique locations
                    locations = sorted(mapped_data['location_name'].unique())
                    
                    # Calculate targets by location
                    target_data = calculate_inventory_targets(mapped_data, st.session_state.lead_time_days)
                    
                    # Aggregation by location
                    location_data = target_data.groupby('location_name').agg({
                        'at site': 'sum',
                        'inventory_target': 'sum',
                        'inventory_gap': 'sum',
                        'inventory_surplus': 'sum',
                        'sales_30_days': 'sum',
                        'sales_60_days': 'sum',
                        'sales_90_days': 'sum'
                    }).reset_index()
                    
                    # Calculate target percentage by location
                    location_data['target_percentage'] = (location_data['at site'] / location_data['inventory_target']) * 100
                    
                    # Calculate inventory days (how many days the current inventory will last based on sales rate)
                    # Use weighted_daily_sales from target_data to calculate
                    # First calculate daily sales rate - use sales_30_days / 30 for simplicity
                    location_data['daily_sales_rate'] = location_data['sales_30_days'] / 30
                    
                    # Create a numeric inventory days column for sorting and calculations
                    location_data['inventory_days_numeric'] = location_data.apply(
                        lambda row: 999 if row['daily_sales_rate'] == 0 or pd.isna(row['daily_sales_rate']) 
                                    else min(999, row['at site'] / row['daily_sales_rate']), 
                        axis=1
                    )
                    
                    # Round to whole number days (no decimals)
                    location_data['inventory_days_numeric'] = location_data['inventory_days_numeric'].apply(
                        lambda x: int(round(x))
                    )
                    
                    # Create a string-based column for display with "Unlimited" text for zero sales
                    location_data['inventory_days_display'] = location_data.apply(
                        lambda row: "∞ Unlimited" if row['daily_sales_rate'] == 0 or pd.isna(row['daily_sales_rate'])
                                    else f"{int(round(min(999, row['at site'] / row['daily_sales_rate'])))} days", 
                        axis=1
                    )
                    
                    # Use the numeric version for plotting
                    location_data['inventory_days'] = location_data['inventory_days_numeric']
                    
                    # Calculate HBT distribution per store
                    store_hbt = {}
                    
                    # For each location, calculate HBT metrics
                    for location in locations:
                        location_df = mapped_data[mapped_data['location_name'] == location]
                        
                        # Only perform analysis if there's data
                        if len(location_df) > 0:
                            store_hbt[location] = perform_hbt_analysis(location_df)
                    
                    # Store Inventory Comparison Section
                    st.subheader(get_text("store_inventory"))
                    
                    # Show last updated timestamp
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.caption(f"{get_text('last_updated')} {current_time}")
                    
                    # Get both charts from the function (returns a tuple)
                    inventory_chart, sales_chart = create_store_comparison_chart(location_data)
                    
                    # Display the inventory chart first
                    if get_language() == 'en':
                        st.markdown("""
                        This chart shows inventory levels across all stores. 
                        **Inventory Days** (bars on right axis) represents how long the current inventory will last based on the recent sales rate.
                        - The left axis shows the actual units in inventory (Current) compared to the target inventory level.
                        - The right axis shows how many days the current inventory will last.
                        """)
                    else:
                        st.markdown("""
                        Este gráfico muestra los niveles de inventario en todas las tiendas.
                        **Días de Inventario** (barras en el eje derecho) representa cuánto tiempo durará el inventario actual según la tasa de ventas reciente.
                        - El eje izquierdo muestra las unidades reales en inventario (Actual) en comparación con el nivel de inventario objetivo.
                        - El eje derecho muestra cuántos días durará el inventario actual.
                        """)
                    st.plotly_chart(inventory_chart, use_container_width=True, config={'displayModeBar': False})
                    
                    # Display the sales chart
                    if get_language() == 'en':
                        st.markdown("""
                        This chart shows sales volumes across all stores for the last 30, 60, and 90 day periods.
                        """)
                    else:
                        st.markdown("""
                        Este gráfico muestra los volúmenes de ventas en todas las tiendas para los últimos períodos de 30, 60 y 90 días.
                        """)
                    st.plotly_chart(sales_chart, use_container_width=True, config={'displayModeBar': False})
                    
                    # HBT distribution by store
                    st.subheader(get_text("store_hbt_comparison"))
                    if get_language() == 'en':
                        st.markdown("""
                        This chart shows how inventory is distributed among Head (top 30% of sales), Belly (middle tier), 
                        and Tail (bottom 5% of sales) products at each store location.
                        """)
                    else:
                        st.markdown("""
                        Este gráfico muestra cómo se distribuye el inventario entre los productos Head (30% superior de ventas), 
                        Belly (nivel medio) y Tail (5% inferior de ventas) en cada ubicación de tienda.
                        """)
                    hbt_store_chart = create_store_hbt_comparison(store_hbt)
                    st.plotly_chart(hbt_store_chart, use_container_width=True, config={'displayModeBar': False})
                    
                    # Detailed data table
                    st.subheader(get_text("store_metrics"))
                    # Include inventory_days in the displayed data using the display version with "Unlimited"
                    # Create a copy of the dataframe for display
                    display_df = location_data.copy()
                    
                    # Use the inventory_days_display column for the table
                    if 'inventory_days_display' in display_df.columns:
                        display_df['inventory_days'] = display_df['inventory_days_display']
                    
                    st.dataframe(
                        display_df.style.format({
                            'at site': '{:,.0f}',
                            'inventory_target': '{:,.0f}',
                            'inventory_gap': '{:,.0f}',
                            'inventory_surplus': '{:,.0f}',
                            'sales_30_days': '{:,.0f}',
                            'sales_60_days': '{:,.0f}',
                            'sales_90_days': '{:,.0f}',
                            'target_percentage': '{:.1f}%',
                        }),
                        use_container_width=True
                    )
                    
                    # Download button for all store data
                    st.download_button(
                        label=get_text("download_store_data"),
                        data=download_csv(location_data),
                        file_name=f"all_stores_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error calculating store metrics: {e}")

else:
    # Display instructions when no data is loaded
    st.info(get_text("no_file_selected"))
    
    # Sample data structure information
    if get_language() == 'en':
        st.markdown("""
        ### Required Data Format
        
        Your CSV file should contain the following information:
        
        - **Product identifiers** (SKU ID or product ID)
        - **Inventory data** (inventory levels across locations)
        - **Sales data** (30, 60, 90 days periods)
        - **Product information** (name, category, price, etc.)
        - **Location details** (for multi-location analysis)
        
        After uploading your file, you'll be able to map your columns to the required fields for analysis.
        """)
    else:
        st.markdown("""
        ### Formato de Datos Requerido
        
        Su archivo CSV debe contener la siguiente información:
        
        - **Identificadores de producto** (SKU ID o ID de producto)
        - **Datos de inventario** (niveles de inventario en diferentes ubicaciones)
        - **Datos de ventas** (períodos de 30, 60, 90 días)
        - **Información del producto** (nombre, categoría, precio, etc.)
        - **Detalles de ubicación** (para análisis de múltiples ubicaciones)
        
        Después de cargar su archivo, podrá asignar sus columnas a los campos requeridos para el análisis.
        """)
    
    # Show example of the interface
    st.image("assets/logo.svg", width=400)