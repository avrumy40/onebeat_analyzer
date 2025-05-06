import pandas as pd
import numpy as np

def perform_hbt_analysis(data):
    """
    Perform Head-Belly-Tail (HBT) analysis on the product data.
    - Head: Products that contribute to the top 30% of total sales value
    - Tail: Products that contribute to the bottom 5% of total sales value
    - Belly: Everything in between
    
    Args:
        data (pd.DataFrame): The processed data with sales and inventory information
    
    Returns:
        dict: Results of the HBT analysis containing:
              - product_classification: DataFrame with HBT class for each product
              - cumulative_data: DataFrame with cumulative percentages for plotting
              - summary: Summary statistics of the HBT analysis
    """
    # Make a copy of the data to avoid modifying the original
    if hasattr(data, 'copy'):
        analysis_data = data.copy()
    else:
        # If data is a tuple or another non-DataFrame object, try to handle it
        import pandas as pd
        if isinstance(data, tuple) and len(data) > 0 and isinstance(data[0], pd.DataFrame):
            # If it's a tuple with a DataFrame as first item, use that
            analysis_data = data[0].copy()
        else:
            # If we can't determine what to do, just use the original data
            analysis_data = data
    
    # Group by product name/ID if data is at SKU level
    if 'sku_id' in analysis_data.columns and 'sku_count' not in analysis_data.columns:
        # Import the grouping function from data_processor
        from modules.data_processor import group_by_product
        analysis_data = group_by_product(analysis_data)
        
        # If we're using product-level data now, ensure we have an sku_id column for the rest of the analysis
        if 'sku_id' not in analysis_data.columns and 'product_id' in analysis_data.columns:
            analysis_data['sku_id'] = analysis_data['product_id']
    
    # Calculate sales value by multiplying quantity sold by price
    # Use weighted sales approach: 60% weight to 30-day sales, 30% to 60-day, 10% to 90-day
    if 'sales_30_days' in analysis_data.columns:
        analysis_data['sales_30_weighted'] = analysis_data['sales_30_days'] * 0.6
    else:
        analysis_data['sales_30_weighted'] = 0
    
    if 'sales_60_days' in analysis_data.columns:
        analysis_data['sales_60_weighted'] = analysis_data['sales_60_days'] * 0.3
    else:
        analysis_data['sales_60_weighted'] = 0
    
    if 'sales_90_days' in analysis_data.columns:
        analysis_data['sales_90_weighted'] = analysis_data['sales_90_days'] * 0.1
    else:
        analysis_data['sales_90_weighted'] = 0
    
    # Calculate weighted sales
    analysis_data['weighted_sales'] = (
        analysis_data['sales_30_weighted'] + 
        analysis_data['sales_60_weighted'] + 
        analysis_data['sales_90_weighted']
    )
    
    # Calculate sales value (weighted sales * price)
    analysis_data['sales_value'] = analysis_data['weighted_sales'] * analysis_data['catalog_price']
    
    # Calculate inventory value
    analysis_data['inventory_value'] = analysis_data['total_inventory'] * analysis_data['catalog_price']
    
    # Prepare aggregation dictionary
    agg_dict = {
        'product_name': 'first',
        'sales_30_days': 'sum',
        'sales_60_days': 'sum',
        'sales_90_days': 'sum',
        'weighted_sales': 'sum',
        'sales_value': 'sum',
        'total_inventory': 'sum',
        'inventory_value': 'sum',
        'catalog_price': 'first',
        'brands': 'first',
        'category': 'first'
    }
    
    # Add inventory location columns if they exist
    inventory_location_columns = ['at site', 'at transit', 'at wh']
    for col in inventory_location_columns:
        if col in analysis_data.columns:
            agg_dict[col] = 'sum'
    
    # Add cost if it exists
    if 'cost' in analysis_data.columns:
        agg_dict['cost'] = 'first'
    
    # Aggregate by product (in case of multiple locations or if still at SKU level)
    # Check if sku_id exists in the columns
    if 'sku_id' in analysis_data.columns:
        product_data = analysis_data.groupby('sku_id').agg(agg_dict).reset_index()
    elif 'product_id' in analysis_data.columns:
        # Use product_id if sku_id is not available
        product_data = analysis_data.groupby('product_id').agg(agg_dict).reset_index()
        # Rename product_id to sku_id for consistency with the rest of the code
        product_data.rename(columns={'product_id': 'sku_id'}, inplace=True)
    else:
        # Create a generic index if neither sku_id nor product_id is available
        analysis_data['generic_id'] = range(len(analysis_data))
        product_data = analysis_data.groupby('generic_id').agg(agg_dict).reset_index()
        product_data.rename(columns={'generic_id': 'sku_id'}, inplace=True)
    
    # Filter out products with 0 at site inventory AND 0 sales in the last 30 days
    if 'at site' in product_data.columns and 'sales_30_days' in product_data.columns:
        # Replace NaN with 0 to ensure proper comparison
        product_data['at site'] = product_data['at site'].fillna(0)
        product_data['sales_30_days'] = product_data['sales_30_days'].fillna(0)
        
        # Keep only products with either some inventory at site OR some recent sales
        product_data = product_data[(product_data['at site'] > 0) | (product_data['sales_30_days'] > 0)]
    
    # Sort by sales value descending
    product_data = product_data.sort_values('sales_value', ascending=False)
    
    # Calculate cumulative sales value
    total_sales_value = product_data['sales_value'].sum()
    product_data['cumulative_sales_value'] = product_data['sales_value'].cumsum()
    product_data['cumulative_sales_pct'] = product_data['cumulative_sales_value'] / total_sales_value * 100
    
    # Calculate cumulative inventory quantity percentage (instead of product count)
    total_inventory_quantity = product_data['total_inventory'].sum()
    product_data['cumulative_inventory_quantity'] = product_data['total_inventory'].cumsum()
    product_data['cumulative_product_pct'] = product_data['cumulative_inventory_quantity'] / total_inventory_quantity * 100
    
    # Calculate cumulative inventory value
    total_inventory_value = product_data['inventory_value'].sum()
    product_data['cumulative_inventory_value'] = product_data['inventory_value'].cumsum()
    product_data['cumulative_inventory_pct'] = product_data['cumulative_inventory_value'] / total_inventory_value * 100
    
    # Classify products into Head, Belly, Tail based on the simplified criteria
    # 1. Head: Products that contribute to the top 30% of sales
    # 2. Tail: Products that contribute to the bottom 5% of sales
    # 3. Belly: Everything in between
    
    # Initialize everything as Belly first
    product_data['hbt_class'] = 'Belly'  # Default classification
    
    # First find Head products (top 30% of sales)
    running_sales_pct = 0
    
    # Go through products in order of highest sales to lowest
    for idx in range(len(product_data)):
        running_sales_pct += product_data.iloc[idx]['sales_value'] / total_sales_value * 100
        product_data.iloc[idx, product_data.columns.get_indexer(['hbt_class'])[0]] = 'Head'
        if running_sales_pct >= 30:  # Top 30% of sales
            break
    
    # Now find Tail products (bottom 5% of sales)
    running_tail_pct = 0
    
    # Go through products in reverse order (lowest sales to highest)
    for idx in range(len(product_data)-1, -1, -1):
        # Skip if already classified as Head
        if product_data.iloc[idx]['hbt_class'] == 'Head':
            continue
            
        running_tail_pct += product_data.iloc[idx]['sales_value'] / total_sales_value * 100
        product_data.iloc[idx, product_data.columns.get_indexer(['hbt_class'])[0]] = 'Tail'
        if running_tail_pct >= 5:  # Bottom 5% of sales
            break
        
    # Ensure no overlap between Head and Tail (Head takes precedence)
    tail_mask = (product_data['hbt_class'] == 'Tail')
    head_mask = (product_data['hbt_class'] == 'Head')
    product_data.loc[tail_mask & head_mask, 'hbt_class'] = 'Head'
    
    # Prepare data for cumulative graph
    cumulative_data = product_data[['cumulative_product_pct', 'cumulative_sales_pct', 'cumulative_inventory_pct']].copy()
    
    # Calculate summary statistics by HBT class
    summary = product_data.groupby('hbt_class').agg({
        'sku_id': 'count',
        'sales_value': 'sum',
        'inventory_value': 'sum',
        'weighted_sales': 'sum',
        'total_inventory': 'sum'  # Add total inventory count
    }).reset_index()
    
    # Add inventory count to summary to help with debugging
    summary['inventory_count'] = summary['total_inventory']
    
    # Calculate percentage columns to summary
    total_product_count = len(product_data)
    summary['product_count_pct'] = summary['sku_id'] / total_product_count * 100
    summary['sales_value_pct'] = summary['sales_value'] / total_sales_value * 100
    summary['inventory_value_pct'] = summary['inventory_value'] / total_inventory_value * 100
    
    # No need to force percentages as they're calculated directly from the data
    # The percentages should now accurately reflect our Head-Belly-Tail classification
    
    # Rename count column
    summary = summary.rename(columns={'sku_id': 'product_count'})
    
    # Return all relevant results
    return {
        'product_classification': product_data,
        'cumulative_data': cumulative_data,
        'summary': summary
    }

def calculate_kpis(hbt_results, data):
    """
    Calculate Key Performance Indicators (KPIs) from the HBT analysis results.
    
    Args:
        hbt_results (dict): Results from the HBT analysis
        data (pd.DataFrame): The full processed data
    
    Returns:
        dict: KPIs including head product percentage, tail inventory cost, and head availability
    """
    # Extract summary data
    summary = hbt_results['summary']
    product_classification = hbt_results['product_classification']
    
    # 1. Head Product Percentage: Percentage of unique products in the Head category
    total_products = summary['product_count'].sum()
    head_product_count = summary[summary['hbt_class'] == 'Head']['product_count'].values[0] if 'Head' in summary['hbt_class'].values else 0
    head_product_percentage = (head_product_count / total_products) * 100 if total_products > 0 else 0
    
    # 2. Tail Inventory Cost: Dollar value of slow-moving inventory
    tail_inventory_cost = summary[summary['hbt_class'] == 'Tail']['inventory_value'].values[0] if 'Tail' in summary['hbt_class'].values else 0
    
    # 3. Head Availability: Percentage of Head products with inventory
    head_products = product_classification[product_classification['hbt_class'] == 'Head']
    head_products_with_inventory = head_products[head_products['total_inventory'] > 0]
    head_availability = len(head_products_with_inventory) / len(head_products) * 100 if len(head_products) > 0 else 0
    
    return {
        'head_product_percentage': head_product_percentage,
        'tail_inventory_cost': tail_inventory_cost,
        'head_availability': head_availability
    }
