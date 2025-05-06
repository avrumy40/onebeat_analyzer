import pandas as pd
import io
import base64

def download_csv(dataframe):
    """
    Convert a pandas DataFrame to a CSV string for download.
    
    Args:
        dataframe (pd.DataFrame): The DataFrame to convert
        
    Returns:
        str: CSV string
    """
    csv = dataframe.to_csv(index=False)
    return csv

def format_currency(value):
    """
    Format a numeric value as currency with dollar sign.
    No decimal places to match user requirements.
    
    Args:
        value (float): The value to format
        
    Returns:
        str: Formatted currency string without decimal places
    """
    return f"${value:,.0f}"

def format_percent(value):
    """
    Format a numeric value as a percentage.
    
    Args:
        value (float): The value to format (0-100)
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value:.1f}%"

def generate_color_mapping(categories):
    """
    Generate a consistent color mapping for a list of categories.
    
    Args:
        categories (list): List of category values
        
    Returns:
        dict: Mapping of categories to colors
    """
    # Predefined colors for consistent visualization
    colors = [
        '#4A90E2', '#50E3C2', '#F8E71C', '#FF9800', '#4CAF50',
        '#9013FE', '#FF6B6B', '#B8E986', '#BD10E0', '#9E9E9E',
        '#8B572A', '#7ED321', '#417505', '#D0021B', '#F5A623'
    ]
    
    # Map each category to a color
    color_map = {}
    for i, category in enumerate(categories):
        color_map[category] = colors[i % len(colors)]
    
    return color_map

def get_weighted_sales(data):
    """
    Calculate weighted sales based on 30, 60, and 90 day sales.
    
    Args:
        data (pd.DataFrame): DataFrame with sales columns
        
    Returns:
        pd.Series: Weighted sales values
    """
    # Weights: 60% for 30-day, 30% for 60-day, 10% for 90-day
    weights = {
        'sales_30_days': 0.6,
        'sales_60_days': 0.3,
        'sales_90_days': 0.1
    }
    
    # Calculate weighted sum
    weighted_sales = 0
    
    for col, weight in weights.items():
        if col in data.columns:
            weighted_sales += data[col] * weight
    
    return weighted_sales
