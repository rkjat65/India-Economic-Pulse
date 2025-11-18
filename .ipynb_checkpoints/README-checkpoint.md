# Indian Economic Data Fetcher

A comprehensive Python class for loading and processing Indian economic data from Excel spreadsheets.

## 📊 Supported Datasets

1. **GDP Data** - Quarterly GDP components and growth rates
2. **Inflation Data** - CPI, WPI, and various inflation indices
3. **Foreign Trade** - Exports, imports, and trade balance (oil and non-oil)
4. **Forex Reserves** - Weekly foreign exchange reserves data
5. **Exchange Rates** - Daily rupee exchange rates (USD, EUR, GBP, JPY)
6. **RBI Policy Rates** - Repo rate, CRR, SLR, and other policy rates
7. **Industrial Production (IIP)** - Index of Industrial Production
8. **Payment Systems** - Digital payment transaction data

## 🚀 Quick Start

### Installation

```python
import pandas as pd
from economic_data_fetcher import EconomicDataFetcher
```

### Basic Usage

```python
# Initialize the fetcher
fetcher = EconomicDataFetcher(raw_data_dir='raw_data', cache_dir='data')

# Load individual datasets
gdp = fetcher.load_gdp_data()
inflation = fetcher.load_inflation_data()
trade = fetcher.load_trade_data()

# Or process all data at once
all_data = fetcher.process_all_data()

# Get summary of cached datasets
summary = fetcher.get_summary()
print(summary)
```

## 📁 File Structure

```
project/
├── raw_data/                    # Place your Excel files here
│   ├── gdp_data.xlsx
│   ├── inflation_data.xlsx
│   ├── Foreign-Trade.xlsx
│   ├── Forex.xlsx
│   ├── Rupee-Exchange-Rate.xlsx
│   ├── RBI-Rates.xlsx
│   ├── IIP.xlsx
│   └── Payment-Data.xlsx
├── data/                        # Processed CSV files stored here
│   ├── gdp_data.csv
│   ├── inflation_data.csv
│   └── ...
└── economic_data_fetcher.py     # The main class file
```

## 📖 Detailed Usage

### 1. GDP Data

```python
gdp = fetcher.load_gdp_data()

# Available columns:
# - date, year, quarter
# - PFCE, GFCE, GFCF, change_in_stock, valuables
# - exports, imports, discrepancies, GDP
# - gdp_growth_yoy, gdp_growth_qoq
# - net_exports, trade_balance_pct
# - total_consumption, consumption_pct, investment_rate

# Example analysis
print(gdp[['date', 'GDP', 'gdp_growth_yoy', 'investment_rate']].tail())
```

### 2. Inflation Data

```python
inflation = fetcher.load_inflation_data()

# Available columns:
# - date
# - CPI_combined, CPI_rural, CPI_urban
# - CPI_industrial_2001, CPI_industrial_2016
# - WPI, WPI_primary, WPI_fuel, WPI_manufactured
# - CPI_inflation_yoy, CPI_inflation_mom
# - WPI_inflation_yoy, WPI_inflation_mom

# Plot inflation trends
import matplotlib.pyplot as plt
plt.plot(inflation['date'], inflation['CPI_inflation_yoy'])
plt.title('CPI Inflation YoY %')
plt.show()
```

### 3. Foreign Trade Data

```python
trade = fetcher.load_trade_data()

# Available columns:
# - date, year
# - exports_rupees, exports_usd
# - exports_oil_rupees, exports_oil_usd
# - exports_nonoil_rupees, exports_nonoil_usd
# - imports_rupees, imports_usd
# - trade_balance_rupees, trade_balance_usd
# - trade_openness_rupees, import_cover_ratio
# - exports_growth_yoy, imports_growth_yoy

# Calculate trade deficit
trade_deficit = trade['trade_balance_rupees'].mean()
print(f"Average trade deficit: ₹{trade_deficit:,.0f} crores")
```

### 4. Forex Reserves

```python
forex = fetcher.load_forex_reserves_data()

# Available columns:
# - date
# - total_reserves_inr, total_reserves_usd
# - fca_inr, fca_usd (Foreign Currency Assets)
# - gold_inr, gold_usd
# - sdr_inr, sdr_usd (Special Drawing Rights)
# - imf_reserve_inr, imf_reserve_usd
# - reserves_growth_yoy, reserves_growth_wow
# - gold_pct, fca_pct

print(f"Latest reserves: ${forex['total_reserves_usd'].iloc[-1]:,.0f} million")
```

### 5. Exchange Rates

```python
exchange = fetcher.load_exchange_rate_data()

# Available columns:
# - date
# - USD_INR, GBP_INR, EUR_INR, JPY_INR
# - USD_INR_change, GBP_INR_change, EUR_INR_change, JPY_INR_change
# - USD_INR_yoy

# Calculate rupee depreciation
latest_rate = exchange['USD_INR'].iloc[-1]
year_ago_rate = exchange['USD_INR'].iloc[-252]
depreciation = ((latest_rate - year_ago_rate) / year_ago_rate) * 100
print(f"Rupee depreciation: {depreciation:.2f}%")
```

### 6. RBI Policy Rates

```python
rbi = fetcher.load_rbi_rates_data()

# Available columns:
# - date
# - bank_rate, repo_rate, reverse_repo
# - sdf_rate (Standing Deposit Facility)
# - msf_rate (Marginal Standing Facility)
# - crr (Cash Reserve Ratio)
# - slr (Statutory Liquidity Ratio)

# Current policy stance
print(rbi[['date', 'repo_rate', 'crr']].tail())
```

## 🔧 Advanced Usage

### Merging Multiple Datasets

```python
# Merge GDP and inflation on date
merged = pd.merge(
    gdp[['date', 'GDP', 'gdp_growth_yoy']],
    inflation[['date', 'CPI_inflation_yoy']],
    on='date',
    how='inner'
)

# Analyze relationship
correlation = merged['gdp_growth_yoy'].corr(merged['CPI_inflation_yoy'])
print(f"GDP Growth vs Inflation correlation: {correlation:.3f}")
```

### Time Series Analysis

```python
# Resample daily exchange rate to monthly average
exchange_monthly = exchange.set_index('date').resample('M')['USD_INR'].mean()

# Calculate rolling volatility
exchange['volatility_30d'] = exchange['USD_INR_change'].rolling(30).std()
```

### Caching and Performance

The fetcher automatically caches processed data as CSV files:

```python
# Load from cache (much faster)
cached_data = fetcher.load_from_cache('gdp_data.csv')

# Check what's cached
summary = fetcher.get_summary()
print(summary)
```

## 📝 Data Dictionary

### GDP Components:
- **PFCE**: Private Final Consumption Expenditure
- **GFCE**: Government Final Consumption Expenditure
- **GFCF**: Gross Fixed Capital Formation

### Policy Rates:
- **Repo Rate**: Rate at which RBI lends to banks
- **Reverse Repo**: Rate at which RBI borrows from banks
- **CRR**: Cash Reserve Ratio - % of deposits banks must keep with RBI
- **SLR**: Statutory Liquidity Ratio - % of deposits in liquid assets
- **SDF**: Standing Deposit Facility Rate
- **MSF**: Marginal Standing Facility Rate

## ⚙️ Configuration

### Custom Directory Structure

```python
fetcher = EconomicDataFetcher(
    raw_data_dir='/path/to/excel/files',
    cache_dir='/path/to/cached/csvs'
)
```

### Loading Specific IIP Sheets

```python
# IIP file has multiple sheets
iip_growth = fetcher.load_iip_data(sheet_name='IIP Growth Rate')
iip_industry = fetcher.load_iip_data(sheet_name='IIP-Industry-Base(2011-12)')
```

## 🐛 Error Handling

The fetcher includes robust error handling:

```python
gdp = fetcher.load_gdp_data()

if gdp.empty:
    print("Failed to load GDP data")
else:
    print(f"Successfully loaded {len(gdp)} records")
```

## 📊 Example Analysis Script

```python
from economic_data_fetcher import EconomicDataFetcher
import pandas as pd
import matplotlib.pyplot as plt

# Initialize
fetcher = EconomicDataFetcher(raw_data_dir='raw_data', cache_dir='data')

# Load data
gdp = fetcher.load_gdp_data()
inflation = fetcher.load_inflation_data()

# Create visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# GDP Growth
ax1.plot(gdp['date'], gdp['gdp_growth_yoy'])
ax1.set_title('GDP Growth Rate (YoY %)')
ax1.grid(True)

# Inflation
ax2.plot(inflation['date'], inflation['CPI_inflation_yoy'], label='CPI')
ax2.plot(inflation['date'], inflation['WPI_inflation_yoy'], label='WPI')
ax2.set_title('Inflation Rates (YoY %)')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()
```

## 🔍 Troubleshooting

### Common Issues:

1. **File Not Found Error**
   - Ensure Excel files are in the `raw_data_dir` directory
   - Check file names match exactly (case-sensitive)

2. **Empty DataFrame Returned**
   - Check console output for specific error messages
   - Verify Excel file format hasn't changed
   - Ensure Excel files contain expected data structure

3. **Date Parsing Errors**
   - The fetcher handles footer notes automatically
   - If dates still fail, check Excel date format

## 📈 Performance Tips

1. **Use cached data**: After initial processing, load from CSV
2. **Process in batches**: Load only needed datasets
3. **Filter early**: Apply date filters before calculations
4. **Use appropriate data types**: Consider downcasting for memory efficiency

## 🤝 Contributing

To add support for new data files:

1. Create a new `load_*_data()` method
2. Follow the existing pattern:
   - Load Excel file
   - Clean and validate data
   - Handle footer notes
   - Convert dates and numeric columns
   - Calculate derived metrics
   - Cache results

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 👤 Author

Created for Indian economic data analysis projects.

## 🔗 Related Resources

- Reserve Bank of India (RBI): https://www.rbi.org.in/
- Ministry of Statistics: https://www.mospi.gov.in/
- Economic Survey: https://www.indiabudget.gov.in/
