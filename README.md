# Inventory Analytics Dashboard

A robust Streamlit-based inventory analytics platform that transforms complex inventory data into actionable insights through advanced visualization and processing techniques.

## Features

- **HBT Analysis**: Analyze your inventory using Head-Belly-Tail classification for better inventory management
- **Multi-Location Support**: Compare inventory metrics across different store locations
- **Misdistribution Analysis**: Identify opportunities to redistribute inventory between locations
- **Interactive Visualizations**: Rich, interactive charts powered by Plotly
- **Multilingual Support**: Available in English and Spanish (Mexico)
- **Flexible Data Import**: Upload your own CSV files with customizable column mapping

## Requirements

- Python 3.8 or higher
- Streamlit
- Pandas
- NumPy
- Plotly
- Matplotlib

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/inventory-analytics-dashboard.git
cd inventory-analytics-dashboard
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Upload your inventory data CSV file on the home page
2. Map your CSV columns to the required columns
3. Navigate through the different tabs to explore your inventory insights:
   - HBT Analysis
   - Misdistribution Analysis 
   - Store Comparison
   - Sales Trends

## Configuration

The application allows you to customize:
- Lead time days for inventory calculations
- Language preference (English or Spanish)

## License

MIT

## Credits

Developed with ❤️ for better inventory management.