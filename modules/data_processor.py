import pandas as pd
import numpy as np

def process_data(data, column_mapping):
    """
    Process the raw data using the column mapping provided by the user.
    
    Args:
        data (pd.DataFrame): The raw data uploaded by the user
        column_mapping (dict): Mapping of user columns to required columns
    
    Returns:
        pd.DataFrame: Processed data with standardized column names
    """
    # Make a copy of the original data
    processed_data = data.copy()
    
    # Rename columns based on the mapping
    # Only include columns that are mapped (exclude None/empty mappings)
    rename_dict = {user_col: app_col for app_col, user_col in column_mapping.items() 
                  if user_col is not None and user_col != ''}
    
    processed_data = processed_data.rename(columns=rename_dict)
    
    # Ensure numeric columns are numeric
    numeric_cols = ['sales_30_days', 'sales_60_days', 'sales_90_days', 'catalog_price', 'cost',
                   'at site', 'at transit', 'at wh']
    
    for col in numeric_cols:
        if col in processed_data.columns:
            # Replace empty strings with NaN
            processed_data[col] = processed_data[col].replace('', np.nan)
            
            # Convert to numeric, coerce errors to NaN
            processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')
            
            # Fill NaN with 0
            processed_data[col] = processed_data[col].fillna(0)
    
    # Handle missing inventory columns
    inventory_cols = ['at site', 'at transit', 'at wh']
    for col in inventory_cols:
        if col not in processed_data.columns:
            processed_data[col] = 0
    
    # Handle missing sales columns
    sales_cols = ['sales_30_days', 'sales_60_days', 'sales_90_days']
    for col in sales_cols:
        if col not in processed_data.columns:
            processed_data[col] = 0
    
    # Replace NaN values with 0 for inventory columns
    inventory_columns = ['at site', 'at transit', 'at wh']
    for col in inventory_columns:
        if col in processed_data.columns:
            processed_data[col] = processed_data[col].fillna(0)
    
    # Calculate total inventory for each product-location
    processed_data['total_inventory'] = (
        processed_data['at site'] + 
        processed_data['at transit'] + 
        processed_data['at wh']
    )
    
    # Save the original row count
    original_row_count = len(processed_data)
    
    # Filter out rows with zero sales in 90 days AND zero inventory at site/transit
    # Keep rows that have either: sales > 0 OR at_site > 0 OR at_transit > 0
    processed_data = processed_data[
        (processed_data['sales_90_days'] > 0) | 
        (processed_data['at site'] > 0) | 
        (processed_data['at transit'] > 0)
    ]
    
    # Calculate how many rows were removed
    filtered_row_count = len(processed_data)
    rows_removed = original_row_count - filtered_row_count
    
    # Save these metrics to return later
    filtering_stats = {
        'original_rows': original_row_count,
        'filtered_rows': filtered_row_count,
        'rows_removed': rows_removed,
        'percent_removed': round((rows_removed / original_row_count * 100), 1) if original_row_count > 0 else 0
    }
    
    # Ensure product name and sku_id are present
    if 'sku name' in processed_data.columns and 'product_name' not in processed_data.columns:
        processed_data['product_name'] = processed_data['sku name']
        
    # Make sure we have a catalog_price column - important for HBT analysis
    if 'catalog_price' not in processed_data.columns:
        # Try to find a price column in the data
        price_columns = [col for col in processed_data.columns if 'price' in col.lower()]
        if price_columns:
            # Use the first found price column
            processed_data['catalog_price'] = processed_data[price_columns[0]]
            print(f"Used {price_columns[0]} as catalog_price")
    
    # Make sure we have a cost column
    if 'cost' not in processed_data.columns:
        # Try to find a cost column in the data
        cost_columns = [col for col in processed_data.columns if 'cost' in col.lower()]
        if cost_columns:
            # Use the first found cost column
            processed_data['cost'] = processed_data[cost_columns[0]]
            print(f"Used {cost_columns[0]} as cost")
    
    # Convert object types to strings to avoid potential issues
    string_cols = ['sku_id', 'product_name', 'brands', 'category', 'styles', 'seasons']
    for col in string_cols:
        if col in processed_data.columns:
            processed_data[col] = processed_data[col].astype(str)
    
    return processed_data, filtering_stats

def validate_data(data):
    """
    Validate that the processed data contains the necessary columns and values
    for analysis.
    
    Args:
        data (pd.DataFrame): The processed data to validate
    
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    # Check for required columns
    required_columns = ['sku_id', 'product_name', 'catalog_price']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for at least one inventory column
    if 'total_inventory' not in data.columns:
        return False, "Missing inventory data. Please map at least one inventory column."
    
    # Check for at least one sales column
    sales_columns = ['sales_30_days', 'sales_60_days', 'sales_90_days']
    has_sales = any(col in data.columns for col in sales_columns)
    
    if not has_sales:
        return False, "Missing sales data. Please map at least one sales column."
    
    # Check for valid numeric values in price
    if 'catalog_price' in data.columns:
        if data['catalog_price'].isnull().all() or (data['catalog_price'] <= 0).all():
            return False, "Invalid or missing price data. Prices must be positive numbers."
    
    # All checks passed
    return True, "Data validation successful."

def group_by_product(data):
    """
    Group data by product name or product ID instead of SKUs.
    This ensures HBT analysis is performed at the product level rather than SKU level.
    
    Args:
        data (pd.DataFrame): The processed data with SKU-level information
        
    Returns:
        pd.DataFrame: Data aggregated at the product level
    """
    # Determine which column to use as the product identifier
    product_id_col = 'product_name'  # Default to product_name
    
    # Prepare aggregation dict based on available columns
    agg_dict = {
        'sku_id': 'count',  # Count of unique SKUs
        'sales_30_days': 'sum',
        'sales_60_days': 'sum',
        'sales_90_days': 'sum',
        'total_inventory': 'sum',
        'at site': 'sum',
        'at transit': 'sum',
        'at wh': 'sum',
        'catalog_price': 'mean',
        'brands': 'first',
        'category': 'first',
        'styles': 'first',
        'seasons': 'first'
    }
    
    # Add cost if it exists
    if 'cost' in data.columns:
        agg_dict['cost'] = 'mean'
    
    # Group by product identifier and aggregate
    product_data = data.groupby(product_id_col).agg(agg_dict).reset_index()
    
    # Rename columns for clarity
    product_data = product_data.rename(columns={
        'sku_id': 'sku_count',
        product_id_col: 'product_name'
    })
    
    # Create a new product_id column if needed
    if 'product_id' not in product_data.columns:
        product_data['product_id'] = product_data.index
    
    return product_data

def aggregate_inventory_by_location(data):
    """
    Aggregate inventory data by location.
    
    Args:
        data (pd.DataFrame): The processed data with inventory information
    
    Returns:
        pd.DataFrame: Aggregated inventory by location
    """
    if 'location_name' not in data.columns:
        # If location column is missing, return empty DataFrame
        return pd.DataFrame(columns=['location_name', 'total_inventory', 'total_value'])
    
    # Group by location and sum inventory
    location_inventory = data.groupby('location_name').agg({
        'total_inventory': 'sum',
        'at site': 'sum',
        'at transit': 'sum',
        'at wh': 'sum',
        'sku_id': 'count'  # Count of unique products
    }).reset_index()
    
    # Rename the count column
    location_inventory = location_inventory.rename(columns={'sku_id': 'product_count'})
    
    # Calculate average price and total value
    price_by_location = data.groupby('location_name').apply(
        lambda x: np.average(x['catalog_price'], weights=(x['total_inventory']+0.0001))
    ).reset_index()
    price_by_location.columns = ['location_name', 'avg_price']
    
    # Merge average price back to location inventory
    location_inventory = pd.merge(location_inventory, price_by_location, on='location_name', how='left')
    
    # Calculate total inventory value
    location_inventory['total_value'] = location_inventory['total_inventory'] * location_inventory['avg_price']
    
    # Sort by total inventory value descending
    location_inventory = location_inventory.sort_values('total_value', ascending=False)
    
    return location_inventory

def calculate_inventory_targets(data, lead_time_days):
    """
    Calculate inventory targets based on sales patterns and lead time.
    
    Args:
        data (pd.DataFrame): The processed data with sales and inventory information
        lead_time_days (int): The replenishment lead time in days
    
    Returns:
        pd.DataFrame: Updated dataframe with inventory targets
    """
    # Create a copy of the data to avoid modifying the original
    result = data.copy()
    
    # Calculate weighted average daily sales based on 30-60-90 day sales
    # We'll give more weight to recent sales (30 days) and less to older sales
    result['daily_sales_30d'] = result['sales_30_days'] / 30
    result['daily_sales_60d'] = (result['sales_60_days'] - result['sales_30_days']) / 30
    result['daily_sales_90d'] = (result['sales_90_days'] - result['sales_60_days']) / 30
    
    # Weighted average with more emphasis on recent sales
    result['weighted_daily_sales'] = (
        result['daily_sales_30d'] * 0.6 + 
        result['daily_sales_60d'] * 0.3 + 
        result['daily_sales_90d'] * 0.1
    )
    
    # Set negative or zero values to a small positive number to avoid division by zero
    # and to ensure a minimum inventory level
    result['weighted_daily_sales'] = result['weighted_daily_sales'].clip(lower=0.01)
    
    # Calculate inventory target based on the lead time
    # The target is the amount needed to cover sales during lead time
    result['inventory_target'] = result['weighted_daily_sales'] * lead_time_days
    
    # Round to whole numbers since we can't have partial inventory units
    result['inventory_target'] = result['inventory_target'].round().astype(int)
    
    # Ensure the target is never less than 1 (minimum stock level)
    result['inventory_target'] = result['inventory_target'].clip(lower=1)
    
    # Calculate the gap between current inventory and target
    result['inventory_gap'] = result['inventory_target'] - result['at site']
    
    # Calculate surplus (Current Inventory - Target Inventory, keeps all values)
    # True surplus is the direct difference between current inventory and target
    result['inventory_surplus'] = result['at site'] - result['inventory_target']
    
    # Calculate percentage of target
    result['target_percentage'] = result['at site'] / result['inventory_target'] * 100
    
    # Round to 1 decimal place
    result['target_percentage'] = result['target_percentage'].apply(lambda x: round(x, 1))
    
    # Handle division by zero or very small targets
    result['target_percentage'] = result['target_percentage'].replace([float('inf'), float('-inf')], 100)
    result['target_percentage'] = result['target_percentage'].clip(lower=0)
    
    return result

def calculate_redistribution_metrics(data):
    """
    Calculate advanced metrics for redistribution analysis.
    
    Args:
        data (pd.DataFrame): The processed data with inventory targets and gaps
    
    Returns:
        dict: A dictionary containing redistribution metrics and dataframes
    """
    # Create a copy of the data
    df = data.copy()
    
    # Initialize results dictionary
    results = {}
    
    # 1. Total Availability - Percentage of SKUs that are in stock (at site > 0)
    in_stock_count = (df['at site'] > 0).sum()
    total_skus = len(df)
    results['total_availability'] = round((in_stock_count / total_skus * 100), 1) if total_skus > 0 else 0
    
    # 2. Availability for Depleted Warehouse - Only if warehouse data is available
    if 'at wh' in df.columns:
        # Count SKUs with warehouse stock < 1
        depleted_wh_skus = df[df['at wh'] < 1]
        depleted_wh_count = len(depleted_wh_skus)
        
        # Count those that are in stock at site
        depleted_wh_in_stock = (depleted_wh_skus['at site'] > 0).sum()
        
        results['depleted_wh_availability'] = round((depleted_wh_in_stock / depleted_wh_count * 100), 1) if depleted_wh_count > 0 else 0
    else:
        results['depleted_wh_availability'] = None
    
    # 3. Warehouse Potential - How much of the stockouts could be fixed with WH replenishment
    if 'at wh' in df.columns:
        # Identify SKUs that are out of stock at site but have warehouse stock
        stockouts = df[df['at site'] < 1]
        stockouts_with_wh = stockouts[stockouts['at wh'] > 0]
        
        # Calculate potential fixes
        potential_fixes = len(stockouts_with_wh)
        total_stockouts = len(stockouts)
        
        results['wh_potential'] = round((potential_fixes / total_stockouts * 100), 1) if total_stockouts > 0 else 0
    else:
        results['wh_potential'] = None
    
    # 4. Potential Availability from Other Stores - Only if more than one location
    if 'location_name' in df.columns and len(df['location_name'].unique()) > 1:
        # Find SKUs that are out of stock where warehouse stock is depleted
        depleted_wh_stockouts = 0
        potential_fixes_from_stores = 0
        
        # Group by SKU to analyze across locations
        sku_groups = df.groupby('sku_id')
        
        for sku, sku_data in sku_groups:
            # Check if this SKU has warehouse stock < 1 (depleted warehouse)
            if 'at wh' in sku_data.columns and (sku_data['at wh'] < 1).all():
                # Find locations where this SKU is out of stock (at site = 0)
                stockout_locations = sku_data[sku_data['at site'] < 1]
                
                if len(stockout_locations) > 0:
                    depleted_wh_stockouts += len(stockout_locations)
                    
                    # Check if other locations have surplus of this SKU
                    surplus_locations = sku_data[sku_data['inventory_surplus'] > 0]
                    
                    if len(surplus_locations) > 0:
                        # Count how many stockout locations could be fixed with surplus from other stores
                        total_surplus = surplus_locations['inventory_surplus'].sum()
                        potential_fixes = min(len(stockout_locations), total_surplus)
                        potential_fixes_from_stores += potential_fixes
        
        # Calculate percentage of depleted warehouse stockouts that could be fixed with store redistribution
        results['store_redistribution_potential'] = round((potential_fixes_from_stores / depleted_wh_stockouts * 100), 1) if depleted_wh_stockouts > 0 else 0
    else:
        results['store_redistribution_potential'] = None
    
    # 5. Potential Sales Increase from Warehouse Redistribution
    if 'at wh' in df.columns:
        # Calculate potential additional sales if warehouse stock was moved to stores with gaps
        potential_wh_sales = 0
        
        # For each SKU with warehouse stock
        for sku, sku_data in df.groupby('sku_id'):
            # Sum the warehouse stock for this SKU
            wh_stock = sku_data['at wh'].sum()
            
            if wh_stock > 0:
                # Calculate the total gap (needed - current) across locations where it's below target
                total_gap = sku_data[sku_data['inventory_gap'] > 0]['inventory_gap'].sum()
                
                # The stock we can move is the minimum of warehouse stock or the total gap
                movable_stock = min(wh_stock, total_gap)
                
                # Calculate the weighted daily sales for this SKU
                avg_daily_sales = sku_data['weighted_daily_sales'].mean()
                
                # Potential additional sales over 30 days
                potential_wh_sales += movable_stock * avg_daily_sales * 30 / sku_data['inventory_target'].mean()
        
        # Get total 30-day sales for comparison
        total_30day_sales = df['sales_30_days'].sum()
        
        # Calculate percentage increase in sales
        results['potential_wh_sales_increase'] = round((potential_wh_sales / total_30day_sales * 100), 1) if total_30day_sales > 0 else 0
    else:
        results['potential_wh_sales_increase'] = None
    
    # 6. Potential Sales Increase from Store-to-Store Redistribution
    if 'location_name' in df.columns and len(df['location_name'].unique()) > 1:
        # Calculate potential additional sales if stock was redistributed between stores
        potential_store_sales = 0
        
        # For each SKU
        for sku, sku_data in df.groupby('sku_id'):
            # Calculate excess stock (current - target) in locations where it's above target
            excess_stock = sku_data[sku_data['at site'] > sku_data['inventory_target']]
            excess_amount = (excess_stock['at site'] - excess_stock['inventory_target']).sum()
            
            if excess_amount > 0:
                # Calculate the total gap in locations where it's below target
                shortage_stock = sku_data[sku_data['inventory_gap'] > 0]
                shortage_amount = shortage_stock['inventory_gap'].sum()
                
                # The stock we can move is the minimum of excess or shortage
                movable_stock = min(excess_amount, shortage_amount)
                
                # Calculate the weighted daily sales for this SKU
                avg_daily_sales = sku_data['weighted_daily_sales'].mean()
                
                # Potential additional sales over 30 days
                potential_store_sales += movable_stock * avg_daily_sales * 30 / sku_data['inventory_target'].mean()
        
        # Get total 30-day sales for comparison
        total_30day_sales = df['sales_30_days'].sum()
        
        # Calculate percentage increase in sales
        results['potential_store_sales_increase'] = round((potential_store_sales / total_30day_sales * 100), 1) if total_30day_sales > 0 else 0
    else:
        results['potential_store_sales_increase'] = None
    
    return results
