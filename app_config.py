# Application configuration

# Application title and description
APP_TITLE = "Inventory Analytics Dashboard"
APP_DESCRIPTION = """
This dashboard provides comprehensive inventory and sales analytics to help you optimize 
your stock levels, identify top performers, and manage slow-moving products. Upload your 
inventory and sales data to get started.
"""

# Required columns for analysis with descriptions
REQUIRED_COLUMNS = {
    "sku_id": {
        "description": "Unique identifier for each product (SKU/Product ID)",
        "required": True
    },
    "product_name": {
        "description": "Name or description of the product",
        "required": True
    },
    "location_name": {
        "description": "Store or warehouse location name",
        "required": True
    },
    "at site": {
        "description": "Inventory quantity at store location",
        "required": False
    },
    "at transit": {
        "description": "Inventory quantity in transit",
        "required": False
    },
    "at wh": {
        "description": "Inventory quantity at warehouse",
        "required": False
    },
    "sales_30_days": {
        "description": "Sales quantity in the last 30 days",
        "required": True
    },
    "sales_60_days": {
        "description": "Sales quantity in the last 60 days",
        "required": False
    },
    "sales_90_days": {
        "description": "Sales quantity in the last 90 days",
        "required": False
    },
    "catalog_price": {
        "description": "Retail price of the product (catalog_price)",
        "required": True,
        "aliases": ["price", "unit_price", "retail_price"]
    },
    "cost": {
        "description": "Cost of the product (purchase price)",
        "required": False,
        "aliases": ["purchase_cost", "supplier_price", "vendor_cost"]
    },
    "brands": {
        "description": "Brand of the product",
        "required": False
    },
    "category": {
        "description": "Product category",
        "required": False
    },
    "styles": {
        "description": "Product style (e.g. MANGA CORTA, MANGA LARGA)",
        "required": False
    },
    "seasons": {
        "description": "Seasonal classification (e.g. VERANO 2024)",
        "required": False
    },
    "size": {
        "description": "Product size",
        "required": False
    },
    "department_name": {
        "description": "Department name",
        "required": False
    }
}

# HBT Analysis configuration
HBT_CONFIG = {
    "head_threshold": 0.2,   # Top 20% of products by count
    "tail_threshold": 0.05,  # Bottom 5% of sales contribution
    "sales_weights": {
        "sales_30_days": 0.6,  # 60% weight for 30-day sales
        "sales_60_days": 0.3,  # 30% weight for 60-day sales
        "sales_90_days": 0.1   # 10% weight for 90-day sales
    }
}

# Visualization settings
VIZ_CONFIG = {
    "color_palette": {
        "head": "#4CAF50",  # Green
        "belly": "#2196F3", # Blue
        "tail": "#FF9800",  # Orange
        "sales": "#4A90E2", # Blue
        "inventory": "#FF6B6B" # Red
    },
    "chart_height": 500
}
