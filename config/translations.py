"""
Translations module for multilingual support.
Contains dictionaries with text in English and Spanish (MX).
"""

# English translations (default)
en_translations = {
    # Navigation and UI
    "app_title": "Inventory Analytics Dashboard",
    "upload_data": "Upload Your Data",
    "language_selector": "Language / Idioma",
    "english": "English",
    "spanish": "Español (MX)",
    "sidebar_title": "Navigation",
    "filter_options": "Filter Options",
    "product_categories": "Product Categories",
    "locations": "Locations",
    "brands": "Brands",
    "home_page": "Home",
    "hbt_analysis": "HBT Analysis",
    "misdistribution": "Misdistribution Analysis",
    "store_analysis": "Store Analysis",
    "insights": "Insights",
    
    # Home Page
    "welcome_title": "Welcome to the Inventory Analytics Dashboard",
    "welcome_text": "This tool helps you analyze your inventory data across multiple locations using advanced Head-Belly-Tail (HBT) categorization.",
    "get_started": "To get started, upload your CSV file with inventory and sales data.",
    "data_requirements": "Your data should include:",
    "upload_csv": "Upload CSV File",
    "map_columns": "Map Columns",
    
    # Column Mapping Page
    "mapping_title": "Column Mapping",
    "mapping_instructions": "Match your CSV columns to the required fields below:",
    "mapping_help": "For each required field, select the corresponding column from your CSV.",
    "confirm_mapping": "Confirm Mapping",
    "required_column": "Required Column",
    "your_column": "Your Column",
    "description": "Description",
    
    # Required Fields
    "product_id": "Product ID",
    "product_name": "Product Name",
    "sku": "SKU",
    "location_id": "Location ID",
    "location_name": "Location Name",
    "inventory": "Inventory",
    "cost": "Cost",
    "sales_30_days": "Sales (30 Days)",
    "sales_60_days": "Sales (60 Days)",
    "sales_90_days": "Sales (90 Days)",
    
    # Field Descriptions
    "product_id_desc": "Unique identifier for each product",
    "product_name_desc": "Name or description of the product",
    "sku_desc": "Stock Keeping Unit - unique identifier for each product variant",
    "location_id_desc": "Unique identifier for each store or warehouse location",
    "location_name_desc": "Name of the store or warehouse location",
    "inventory_desc": "Current inventory count (units) at each location",
    "cost_desc": "Cost per unit (in currency)",
    "sales_30_days_desc": "Units sold in the last 30 days",
    "sales_60_days_desc": "Units sold in the last 60 days",
    "sales_90_days_desc": "Units sold in the last 90 days",
    
    # HBT Analysis Tab
    "hbt_title": "Head-Belly-Tail Analysis",
    "hbt_description": "This analysis categorizes your products into Head (top 30% of sales), Belly (middle), and Tail (bottom 5% of sales).",
    "cumulative_graph": "Cumulative HBT Graph",
    "hbt_distribution": "HBT Distribution",
    "product_list": "Product Classification",
    "search_products": "Search Products",
    "download_full_report": "Download Full Report",
    "head_products": "Head Products",
    "belly_products": "Belly Products",
    "tail_products": "Tail Products",
    "class": "Class",
    "head": "Head",
    "belly": "Belly",
    "tail": "Tail",
    "products": "Products",
    "sales": "Sales",
    "inventory": "Inventory",
    
    # Misdistribution Analysis Tab
    "misdistribution_title": "Misdistribution Analysis",
    "lead_time_days": "Lead Time (Days)",
    "location_inventory": "Inventory by Location",
    "inventory_distribution": "Inventory Distribution",
    "misdistribution_metrics": "Misdistribution Metrics",
    "target_adjustment": "Target Adjustment",
    "redistribution_opportunities": "Redistribution Opportunities",
    "from_location": "From Location",
    "to_location": "To Location",
    "units_to_move": "Units to Move",
    "value_to_move": "Value to Move",
    "current_inventory": "Current Inventory",
    "target_inventory": "Target Inventory",
    "inventory_gap": "Inventory Gap",
    "inventory_surplus": "Inventory Surplus",
    "inventory_days": "Inventory Days",
    "unlimited_days": "Unlimited",
    "update_lead_time": "Update Lead Time",
    "days": "days",
    "last_updated": "Last updated at",
    
    # Store Analysis Tab
    "store_title": "Store Analysis",
    "store_inventory": "Store Inventory",
    "store_sales": "Store Sales",
    "store_hbt_comparison": "Store HBT Comparison",
    "inventory_value": "Inventory Value",
    "coverage": "Coverage",
    "select_store": "Select Store",
    "all_stores": "All Stores",
    "inventory_units": "Inventory Units",
    "sales_units": "Sales Units",
    "store_metrics": "Store Metrics Details",
    "download_store_data": "Download All Store Analysis Data",
    "no_data": "No data available for this store",
    
    # Metrics and KPIs
    "total_units": "Total Units",
    "total_value": "Total Value",
    "average_coverage": "Average Coverage",
    "excess_inventory": "Excess Inventory",
    "shortage_inventory": "Shortage Inventory",
    "average_days": "Average Days",
    
    # Filter Actions
    "apply_filters": "Apply Filters",
    "reset_filters": "Reset Filters",
    "filters_applied": "Filters applied! Showing {0} of {1} items ({2}%).",
    "filters_reset": "All filters have been reset.",
    
    # Alerts and Messages
    "data_loaded": "Data loaded successfully!",
    "mapping_complete": "Column mapping completed.",
    "lead_time_updated": "Lead time updated successfully!",
    "no_file_selected": "No file selected. Please upload a CSV file.",
    "invalid_file": "Invalid file. Please upload a CSV file.",
    "mapping_incomplete": "Please complete all column mappings before proceeding.",
    "calculation_error": "Error in calculations. Please check your data."
}

# Spanish (Mexico) translations
es_mx_translations = {
    # Navigation and UI
    "app_title": "Panel de Análisis de Inventario",
    "upload_data": "Cargar Sus Datos",
    "language_selector": "Language / Idioma",
    "english": "English",
    "spanish": "Español (MX)",
    "sidebar_title": "Navegación",
    "filter_options": "Opciones de Filtro",
    "product_categories": "Categorías de Productos",
    "locations": "Ubicaciones",
    "brands": "Marcas",
    "home_page": "Inicio",
    "hbt_analysis": "Análisis HBT",
    "misdistribution": "Análisis de Mala Distribución",
    "store_analysis": "Análisis de Tiendas",
    "insights": "Estadísticas",
    
    # Home Page
    "welcome_title": "Bienvenido al Panel de Análisis de Inventario",
    "welcome_text": "Esta herramienta le ayuda a analizar sus datos de inventario en múltiples ubicaciones utilizando la categorización avanzada Head-Belly-Tail (HBT).",
    "get_started": "Para comenzar, cargue su archivo CSV con datos de inventario y ventas.",
    "data_requirements": "Sus datos deben incluir:",
    "upload_csv": "Cargar Archivo CSV",
    "map_columns": "Mapear Columnas",
    
    # Column Mapping Page
    "mapping_title": "Mapeo de Columnas",
    "mapping_instructions": "Haga coincidir las columnas de su CSV con los campos requeridos a continuación:",
    "mapping_help": "Para cada campo requerido, seleccione la columna correspondiente de su CSV.",
    "confirm_mapping": "Confirmar Mapeo",
    "required_column": "Columna Requerida",
    "your_column": "Su Columna",
    "description": "Descripción",
    
    # Required Fields
    "product_id": "ID de Producto",
    "product_name": "Nombre de Producto",
    "sku": "SKU",
    "location_id": "ID de Ubicación",
    "location_name": "Nombre de Ubicación",
    "inventory": "Inventario",
    "cost": "Costo",
    "sales_30_days": "Ventas (30 Días)",
    "sales_60_days": "Ventas (60 Días)",
    "sales_90_days": "Ventas (90 Días)",
    
    # Field Descriptions
    "product_id_desc": "Identificador único para cada producto",
    "product_name_desc": "Nombre o descripción del producto",
    "sku_desc": "Unidad de Mantenimiento de Stock - identificador único para cada variante de producto",
    "location_id_desc": "Identificador único para cada ubicación de tienda o almacén",
    "location_name_desc": "Nombre de la ubicación de tienda o almacén",
    "inventory_desc": "Recuento actual de inventario (unidades) en cada ubicación",
    "cost_desc": "Costo por unidad (en moneda)",
    "sales_30_days_desc": "Unidades vendidas en los últimos 30 días",
    "sales_60_days_desc": "Unidades vendidas en los últimos 60 días",
    "sales_90_days_desc": "Unidades vendidas en los últimos 90 días",
    
    # HBT Analysis Tab
    "hbt_title": "Análisis Head-Belly-Tail",
    "hbt_description": "Este análisis categoriza sus productos en Head (30% superior de ventas), Belly (medio) y Tail (5% inferior de ventas).",
    "cumulative_graph": "Gráfico Acumulativo HBT",
    "hbt_distribution": "Distribución HBT",
    "product_list": "Clasificación de Productos",
    "search_products": "Buscar Productos",
    "download_full_report": "Descargar Informe Completo",
    "head_products": "Productos Head",
    "belly_products": "Productos Belly",
    "tail_products": "Productos Tail",
    "class": "Clase",
    "head": "Head",
    "belly": "Belly",
    "tail": "Tail",
    "products": "Productos",
    "sales": "Ventas",
    "inventory": "Inventario",
    
    # Misdistribution Analysis Tab
    "misdistribution_title": "Análisis de Mala Distribución",
    "lead_time_days": "Tiempo de Entrega (Días)",
    "location_inventory": "Inventario por Ubicación",
    "inventory_distribution": "Distribución de Inventario",
    "misdistribution_metrics": "Métricas de Mala Distribución",
    "target_adjustment": "Ajuste de Objetivo",
    "redistribution_opportunities": "Oportunidades de Redistribución",
    "from_location": "Desde Ubicación",
    "to_location": "A Ubicación",
    "units_to_move": "Unidades a Mover",
    "value_to_move": "Valor a Mover",
    "current_inventory": "Inventario Actual",
    "target_inventory": "Inventario Objetivo",
    "inventory_gap": "Brecha de Inventario",
    "inventory_surplus": "Excedente de Inventario",
    "inventory_days": "Días de Inventario",
    "unlimited_days": "Ilimitado",
    "update_lead_time": "Actualizar Tiempo de Entrega",
    "days": "días",
    "last_updated": "Actualizado a las",
    
    # Store Analysis Tab
    "store_title": "Análisis de Tiendas",
    "store_inventory": "Inventario de Tienda",
    "store_sales": "Ventas de Tienda",
    "store_hbt_comparison": "Comparación HBT de Tiendas",
    "inventory_value": "Valor de Inventario",
    "coverage": "Cobertura",
    "select_store": "Seleccionar Tienda",
    "all_stores": "Todas las Tiendas",
    "inventory_units": "Unidades de Inventario",
    "sales_units": "Unidades de Ventas",
    "store_metrics": "Detalles de Métricas de Tienda",
    "download_store_data": "Descargar Datos de Análisis de Todas las Tiendas",
    "no_data": "No hay datos disponibles para esta tienda",
    
    # Metrics and KPIs
    "total_units": "Unidades Totales",
    "total_value": "Valor Total",
    "average_coverage": "Cobertura Promedio",
    "excess_inventory": "Exceso de Inventario",
    "shortage_inventory": "Escasez de Inventario",
    "average_days": "Días Promedio",
    
    # Filter Actions
    "apply_filters": "Aplicar Filtros",
    "reset_filters": "Restablecer Filtros",
    "filters_applied": "¡Filtros aplicados! Mostrando {0} de {1} elementos ({2}%).",
    "filters_reset": "Todos los filtros han sido restablecidos.",
    
    # Alerts and Messages
    "data_loaded": "¡Datos cargados exitosamente!",
    "mapping_complete": "Mapeo de columnas completado.",
    "lead_time_updated": "¡Tiempo de entrega actualizado exitosamente!",
    "no_file_selected": "No se seleccionó ningún archivo. Por favor, cargue un archivo CSV.",
    "invalid_file": "Archivo inválido. Por favor, cargue un archivo CSV.",
    "mapping_incomplete": "Por favor, complete todos los mapeos de columnas antes de continuar.",
    "calculation_error": "Error en los cálculos. Por favor, verifique sus datos."
}

# Dictionary mapping language codes to translation dictionaries
translations = {
    'en': en_translations,
    'es_mx': es_mx_translations
}