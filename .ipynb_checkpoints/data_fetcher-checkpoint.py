import pandas as pd
import os
from pathlib import Path
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class EconomicDataFetcher:
    """
    Load and process Indian economic data from Excel files
    
    IMPORTANT: GDP data contains GROWTH RATES (%), not absolute values
    """

    def __init__(self, raw_data_dir='raw_data', cache_dir='data'):
        self.raw_data_dir = Path(raw_data_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def load_gdp_data(self):
        """
        Load GDP GROWTH RATE data (all values are % changes, not absolute)
        
        Returns:
            DataFrame with GDP component growth rates
        """
        try:
            file_path = self.raw_data_dir / 'gdp_data.xlsx'
            df = pd.read_excel(file_path, sheet_name=0)

            print("🔍 Loading GDP growth rate data...")

            # Rename columns - THESE ARE ALL GROWTH RATES!
            column_mapping = {
                'Item/ Year': 'year',
                'Quarter': 'quarter',
                '1. PFCE': 'PFCE_growth',
                '2. GFCE': 'GFCE_growth',
                '3. GFCF': 'GFCF_growth',
                '4. Change in Stock': 'stock_change_contribution',
                '5. Valuables': 'valuables_contribution',
                '6. Export of goods & services': 'exports_growth',
                '7. Import of goods & services': 'imports_growth',
                '8. Discrepancies': 'discrepancies',
                '9. Gross Domestic Product': 'GDP_growth'
            }

            df = df.rename(columns=column_mapping)
            df['year'] = df['year'].ffill()
            df = df.dropna(subset=['quarter'])

            # Extract year
            df['year_numeric'] = df['year'].astype(str).str.split('-').str[0].astype(int)

            # Create date (Indian fiscal year: Q1=Apr, Q2=Jul, Q3=Oct, Q4=Jan)
            quarter_to_month = {'Q1': 4, 'Q2': 7, 'Q3': 10, 'Q4': 1}
            df['month'] = df['quarter'].map(quarter_to_month)
            df['calendar_year'] = df['year_numeric']
            df.loc[df['quarter'] == 'Q4', 'calendar_year'] += 1

            df['date'] = pd.to_datetime(
                df['calendar_year'].astype(str) + '-' + 
                df['month'].astype(str).str.zfill(2) + '-01'
            )

            # Select columns
            columns_to_keep = [
                'date', 'year', 'quarter', 
                'PFCE_growth', 'GFCE_growth', 'GFCF_growth', 
                'stock_change_contribution', 'valuables_contribution',
                'exports_growth', 'imports_growth', 
                'discrepancies', 'GDP_growth'
            ]

            df_clean = df[columns_to_keep].copy()
            df_clean = df_clean.sort_values('date').reset_index(drop=True)

            # Calculate additional metrics (all in growth rates)
            df_clean['consumption_growth_avg'] = (
                df_clean['PFCE_growth'] + df_clean['GFCE_growth']
            ) / 2
            
            df_clean['net_exports_contribution'] = (
                df_clean['exports_growth'] - df_clean['imports_growth']
            )
            
            # 4-quarter moving average
            df_clean['GDP_growth_ma4'] = df_clean['GDP_growth'].rolling(window=4).mean()
            
            # Acceleration/deceleration
            df_clean['GDP_growth_change'] = df_clean['GDP_growth'].diff()

            print(f"✅ Processed GDP growth data: {len(df_clean)} records")
            print(f"📅 Date range: {df_clean['date'].min().strftime('%Y-%m')} to {df_clean['date'].max().strftime('%Y-%m')}")
            print(f"📈 Latest GDP Growth: {df_clean['GDP_growth'].iloc[-1]:.2f}%")
            print(f"📊 Average Growth: {df_clean['GDP_growth'].mean():.2f}%")

            self.save_to_cache(df_clean, 'gdp_data.csv')
            return df_clean

        except Exception as e:
            print(f"❌ Error loading GDP data: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    # Keep all your other methods exactly as they are
    # (load_inflation_data, load_trade_data, etc.)
    
    def load_inflation_data(self):
        """Load and process inflation data"""
        try:
            file_path = self.raw_data_dir / 'inflation_data.xlsx'
            print("🔍 Loading inflation data...")
            df = pd.read_excel(file_path, sheet_name=0)

            # Find valid data rows (before notes)
            valid_indices = []
            for idx, val in enumerate(df['Item']):
                if pd.isna(val) or 'Note' in str(val) or 'See' in str(val):
                    break
                valid_indices.append(idx)
            df = df.iloc[valid_indices]

            # Rename columns
            column_mapping = {
                'Item': 'date',
                '1 Consumer Price Index  (2012=100)': 'CPI_combined',
                '1.1 Rural': 'CPI_rural',
                '1.2 Urban': 'CPI_urban',
                'Consumer Price Index for Industrial Workers (2001=100)': 'CPI_industrial_2001',
                '2 Consumer\nPrice Index for\nIndustrial\nWorkers\n(2016=100)': 'CPI_industrial_2016',
                '3 Wholesale Price Index (2011-12=100)': 'WPI',
                '3.1 Primary Articles ': 'WPI_primary',
                '3.2 Fuel and Power': 'WPI_fuel',
                '3.3 Manufactured Products ': 'WPI_manufactured'
            }
            df = df.rename(columns=column_mapping)
            df['date'] = pd.to_datetime(df['date'])

            # Convert to numeric
            for col in df.columns:
                if col != 'date':
                    df[col] = df[col].replace('-', np.nan)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.sort_values('date').reset_index(drop=True)

            # Calculate inflation rates
            df['CPI_inflation_yoy'] = df['CPI_combined'].pct_change(periods=12) * 100
            df['CPI_rural_inflation_yoy'] = df['CPI_rural'].pct_change(periods=12) * 100
            df['CPI_urban_inflation_yoy'] = df['CPI_urban'].pct_change(periods=12) * 100
            df['WPI_inflation_yoy'] = df['WPI'].pct_change(periods=12) * 100
            df['CPI_inflation_mom'] = df['CPI_combined'].pct_change(periods=1) * 100

            print(f"✅ Processed inflation data: {len(df)} records")
            self.save_to_cache(df, 'inflation_data.csv')
            return df

        except Exception as e:
            print(f"❌ Error loading inflation data: {e}")
            return pd.DataFrame()

    def load_trade_data(self):
        """Load foreign trade data"""
        try:
            file_path = self.raw_data_dir / 'Foreign Trade.xlsx'
            print("🔍 Loading foreign trade data...")
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Skip first row (units)
            df = df.iloc[1:].reset_index(drop=True)
            
            # Rename columns
            df.columns = [
                'year', 'month',
                'exports_rupees', 'exports_usd',
                'exports_oil_rupees', 'exports_oil_usd',
                'exports_nonoil_rupees', 'exports_nonoil_usd',
                'imports_rupees', 'imports_usd',
                'imports_oil_rupees', 'imports_oil_usd',
                'imports_nonoil_rupees', 'imports_nonoil_usd',
                'trade_balance_rupees', 'trade_balance_usd',
                'trade_balance_oil_rupees', 'trade_balance_oil_usd',
                'trade_balance_nonoil_rupees', 'trade_balance_nonoil_usd'
            ]
            
            df['date'] = pd.to_datetime(df['month'])
            
            # Convert numeric
            numeric_cols = [col for col in df.columns if col not in ['year', 'month', 'date']]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
            
            # Calculate metrics
            df['trade_openness'] = df['exports_rupees'] + df['imports_rupees']
            df['import_cover_ratio'] = df['exports_rupees'] / df['imports_rupees']
            df['exports_growth_yoy'] = df['exports_rupees'].pct_change(periods=12) * 100
            df['imports_growth_yoy'] = df['imports_rupees'].pct_change(periods=12) * 100
            
            print(f"✅ Processed trade data: {len(df)} records")
            self.save_to_cache(df, 'trade_data.csv')
            return df
            
        except Exception as e:
            print(f"❌ Error loading trade data: {e}")
            return pd.DataFrame()

    def load_forex_reserves_data(self):
        """Load forex reserves data"""
        try:
            file_path = self.raw_data_dir / 'Forex.xlsx'
            print("🔍 Loading forex reserves data...")
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Skip header rows
            df = df.iloc[5:].reset_index(drop=True)
            df.columns = [
                'date',
                'total_reserves_inr', 'total_reserves_usd',
                'fca_inr', 'fca_usd',
                'gold_inr', 'gold_usd',
                'sdr_inr', 'sdr_usd',
                'imf_reserve_inr', 'imf_reserve_usd'
            ]
            
            # Find valid date rows
            valid_indices = []
            for idx, val in enumerate(df['date']):
                try:
                    pd.to_datetime(val)
                    valid_indices.append(idx)
                except:
                    break
            df = df.iloc[valid_indices]
            
            df['date'] = pd.to_datetime(df['date'])
            
            numeric_cols = [col for col in df.columns if col != 'date']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
            
            # Calculate metrics
            df['reserves_growth_yoy'] = df['total_reserves_usd'].pct_change(periods=52) * 100
            df['gold_pct'] = (df['gold_usd'] / df['total_reserves_usd']) * 100
            df['fca_pct'] = (df['fca_usd'] / df['total_reserves_usd']) * 100
            
            print(f"✅ Processed forex reserves: {len(df)} records")
            self.save_to_cache(df, 'forex_reserves.csv')
            return df
            
        except Exception as e:
            print(f"❌ Error loading forex reserves: {e}")
            return pd.DataFrame()

    def load_rbi_rates_data(self):
        """Load RBI policy rates"""
        try:
            file_path = self.raw_data_dir / 'RBI Rates.xlsx'
            print("🔍 Loading RBI rates data...")
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Skip header
            df = df.iloc[1:].reset_index(drop=True)
            df.columns = [
                'date', 'bank_rate', 'repo_rate', 'reverse_repo',
                'sdf_rate', 'msf_rate', 'crr', 'slr'
            ]
            
            # Find valid dates
            valid_indices = []
            for idx, val in enumerate(df['date']):
                try:
                    pd.to_datetime(val)
                    valid_indices.append(idx)
                except:
                    break
            df = df.iloc[valid_indices]
            
            df['date'] = pd.to_datetime(df['date'])
            
            numeric_cols = ['bank_rate', 'repo_rate', 'reverse_repo', 'sdf_rate', 'msf_rate', 'crr', 'slr']
            for col in numeric_cols:
                df[col] = df[col].replace('-', np.nan)
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.sort_values('date')
            for col in numeric_cols:
                df[col] = df[col].ffill()
            
            print(f"✅ Processed RBI rates: {len(df)} records")
            self.save_to_cache(df, 'rbi_rates.csv')
            return df
            
        except Exception as e:
            print(f"❌ Error loading RBI rates: {e}")
            return pd.DataFrame()

    # Helper methods
    def save_to_cache(self, df, filename):
        filepath = self.cache_dir / filename
        df.to_csv(filepath, index=False)
        print(f"💾 Cached: {filename}")

    def load_from_cache(self, filename):
        filepath = self.cache_dir / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            for col in df.columns:
                if 'date' in col.lower():
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return df
        return None

    def process_all_data(self):
        """Process all Excel files"""
        print("="*80)
        print("📊 PROCESSING ALL INDIAN ECONOMIC DATA")
        print("="*80)

        datasets = {
            'GDP': self.load_gdp_data,
            'Inflation': self.load_inflation_data,
            'Foreign Trade': self.load_trade_data,
            'Forex Reserves': self.load_forex_reserves_data,
            'RBI Rates': self.load_rbi_rates_data,
        }

        results = {}
        for name, func in datasets.items():
            print(f"\n{'='*80}")
            print(f"Processing: {name}")
            print('='*80)
            results[name] = func()

        print("\n" + "="*80)
        print("✅ DATA PROCESSING COMPLETE!")
        print("="*80)

        return results