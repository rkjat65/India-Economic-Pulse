"""
Utility functions for the Economic Pulse Dashboard
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict
import warnings
warnings.filterwarnings('ignore')


def format_currency(value: float, currency: str = 'INR', decimals: int = 0) -> str:
    """Format currency values with proper symbols"""
    if pd.isna(value) or value is None:
        return "N/A"
    
    if currency == 'INR':
        if abs(value) >= 10000000:  # >= 1 Crore
            return f"₹{value/10000000:.2f}Cr"
        elif abs(value) >= 100000:  # >= 1 Lakh
            return f"₹{value/100000:.2f}L"
        else:
            return f"₹{value:,.{decimals}f}"
    elif currency == 'USD':
        if abs(value) >= 1000000:  # >= 1 Million
            return f"${value/1000000:.2f}M"
        elif abs(value) >= 1000:  # >= 1 Thousand
            return f"${value/1000:.2f}K"
        else:
            return f"${value:,.{decimals}f}"
    else:
        return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage values"""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate percentage"""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return np.nan
    return ((current - previous) / previous) * 100


def get_trend_indicator(current: float, previous: float) -> Tuple[str, str]:
    """
    Get trend indicator (up/down/stable) and color
    
    Returns:
        (icon, color_class)
    """
    if pd.isna(current) or pd.isna(previous):
        return ("➖", "text-muted")
    
    diff = current - previous
    if abs(diff) < 0.01:  # Essentially no change
        return ("➖", "text-muted")
    elif diff > 0:
        return ("📈", "text-success")
    else:
        return ("📉", "text-danger")


def get_period_comparison(df: pd.DataFrame, date_col: str, value_col: str, 
                         periods: int = 1) -> pd.DataFrame:
    """Calculate period-over-period comparisons"""
    df = df.sort_values(date_col).copy()
    df[f'{value_col}_prev'] = df[value_col].shift(periods)
    df[f'{value_col}_change'] = df[value_col] - df[f'{value_col}_prev']
    df[f'{value_col}_pct_change'] = calculate_growth_rate(
        df[value_col], df[f'{value_col}_prev']
    )
    return df


def detect_outliers(series: pd.Series, method: str = 'iqr') -> pd.Series:
    """
    Detect outliers in a series
    
    Methods:
        - 'iqr': Interquartile Range method
        - 'zscore': Z-score method (threshold=3)
    """
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (series < lower_bound) | (series > upper_bound)
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > 3
    else:
        raise ValueError(f"Unknown method: {method}")


def get_date_range_filter(df: pd.DataFrame, date_col: str, 
                         years: Optional[List[int]] = None) -> pd.DataFrame:
    """Filter dataframe by year range"""
    if years is None or len(years) == 0:
        return df
    
    if 'year' in df.columns:
        return df[df['year'].isin(years)]
    else:
        df['year'] = pd.to_datetime(df[date_col]).dt.year
        filtered = df[df['year'].isin(years)]
        return filtered.drop(columns=['year'])


def calculate_moving_average(series: pd.Series, window: int = 4) -> pd.Series:
    """Calculate moving average"""
    return series.rolling(window=window, min_periods=1).mean()


def calculate_volatility(series: pd.Series, window: int = 12) -> pd.Series:
    """Calculate rolling volatility (standard deviation)"""
    return series.rolling(window=window, min_periods=1).std()


def get_latest_value(df: pd.DataFrame, date_col: str, value_col: str) -> float:
    """Get the latest value from a dataframe"""
    if df.empty:
        return np.nan
    df_sorted = df.sort_values(date_col)
    return df_sorted[value_col].iloc[-1]


def get_summary_stats(df: pd.DataFrame, value_col: str) -> Dict:
    """Get summary statistics for a column"""
    return {
        'mean': df[value_col].mean(),
        'median': df[value_col].median(),
        'std': df[value_col].std(),
        'min': df[value_col].min(),
        'max': df[value_col].max(),
        'q25': df[value_col].quantile(0.25),
        'q75': df[value_col].quantile(0.75),
    }


def validate_data_quality(df: pd.DataFrame, required_cols: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate data quality
    
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {', '.join(missing_cols)}")
    
    # Check for empty dataframe
    if df.empty:
        issues.append("DataFrame is empty")
    
    # Check for excessive missing values
    for col in required_cols:
        if col in df.columns:
            missing_pct = df[col].isna().sum() / len(df) * 100
            if missing_pct > 50:
                issues.append(f"Column '{col}' has {missing_pct:.1f}% missing values")
    
    return len(issues) == 0, issues


def get_data_freshness(df: pd.DataFrame, date_col: str) -> Dict:
    """Get data freshness information"""
    if df.empty or date_col not in df.columns:
        return {'status': 'unknown', 'days_old': None, 'last_update': None}
    
    df[date_col] = pd.to_datetime(df[date_col])
    last_date = df[date_col].max()
    days_old = (datetime.now() - last_date).days
    
    if days_old <= 7:
        status = 'fresh'
    elif days_old <= 30:
        status = 'recent'
    elif days_old <= 90:
        status = 'stale'
    else:
        status = 'outdated'
    
    return {
        'status': status,
        'days_old': days_old,
        'last_update': last_date.strftime('%Y-%m-%d')
    }


def create_annotation_dict(text: str, x: str, y: float, 
                         xref: str = 'x', yref: str = 'y',
                         showarrow: bool = True, 
                         arrowhead: int = 2,
                         bgcolor: str = 'rgba(255, 255, 255, 0.8)',
                         bordercolor: str = 'rgba(0, 0, 0, 0.5)',
                         borderwidth: int = 1) -> Dict:
    """Create a Plotly annotation dictionary"""
    return {
        'text': text,
        'x': x,
        'y': y,
        'xref': xref,
        'yref': yref,
        'showarrow': showarrow,
        'arrowhead': arrowhead,
        'bgcolor': bgcolor,
        'bordercolor': bordercolor,
        'borderwidth': borderwidth,
        'font': {'size': 12, 'color': 'black'}
    }


def get_color_palette(theme: str = 'professional') -> Dict[str, str]:
    """Get color palette for visualizations"""
    palettes = {
        'professional': {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'info': '#06b6d4',
            'neutral': '#6b7280',
            'background': '#1a1a2e',
            'surface': '#16213e',
            'text': '#e0e7ff'
        },
        'vibrant': {
            'primary': '#6366f1',
            'secondary': '#8b5cf6',
            'accent': '#ec4899',
            'success': '#22c55e',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6',
            'neutral': '#64748b',
            'background': '#0f172a',
            'surface': '#1e293b',
            'text': '#f1f5f9'
        },
        'economic': {
            'primary': '#1e40af',
            'secondary': '#7c3aed',
            'accent': '#db2777',
            'success': '#059669',
            'danger': '#dc2626',
            'warning': '#d97706',
            'info': '#0891b2',
            'neutral': '#4b5563',
            'background': '#111827',
            'surface': '#1f2937',
            'text': '#f9fafb'
        }
    }
    return palettes.get(theme, palettes['professional'])

