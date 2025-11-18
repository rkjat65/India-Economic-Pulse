import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# Modern Professional Color Palette
COLORS = {
    'primary': '#667eea',      # Purple-Blue
    'secondary': '#764ba2',    # Deep Purple
    'accent': '#f093fb',       # Light Purple
    'success': '#10b981',      # Emerald Green
    'danger': '#ef4444',       # Modern Red
    'warning': '#f59e0b',      # Amber
    'info': '#06b6d4',         # Cyan
    'neutral': '#6b7280',      # Gray
    'background': '#1a1a2e',   # Dark Blue
    'surface': '#16213e',      # Darker Blue
    'text': '#e0e7ff'          # Light Purple-White
}

def create_gdp_growth_chart(df):
    """GDP growth rate with moving average"""
    
    fig = go.Figure()
    
    # Bars colored by positive/negative
    colors = ['#2ca02c' if x > 0 else '#d62728' for x in df['GDP_growth']]
    
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['GDP_growth'],
        name='GDP Growth (%)',
        marker=dict(color=colors),
        opacity=0.7,
        hovertemplate='<b>%{x|%Y %b}</b><br>Growth: %{y:.2f}%<extra></extra>'
    ))
    
    # Moving average
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['GDP_growth_ma4'],
        name='4-Quarter Avg',
        mode='lines',
        line=dict(color=COLORS['primary'], width=3),
        hovertemplate='<b>%{x|%Y %b}</b><br>Avg: %{y:.2f}%<extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='India GDP Growth Rate (Year-over-Year %)',
        xaxis_title='',
        yaxis_title='Growth Rate (%)',
        hovermode='x unified',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_gdp_components_growth_chart(df):
    """GDP growth components"""
    
    fig = go.Figure()
    
    components = {
        'PFCE_growth': 'Private Consumption',
        'GFCE_growth': 'Govt Consumption',
        'GFCF_growth': 'Investment',
        'exports_growth': 'Exports',
        'imports_growth': 'Imports'
    }
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, (col, label) in enumerate(components.items()):
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[col],
            name=label,
            mode='lines',
            line=dict(width=2, color=colors[i]),
            hovertemplate=f'<b>{label}</b><br>%{{y:.2f}}%<extra></extra>'
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='GDP Growth Components (All in % Growth Rates)',
        xaxis_title='',
        yaxis_title='Growth Rate (%)',
        hovermode='x unified',
        height=500
    )
    
    return fig

def create_growth_distribution_boxplot(df):
    """Box plot showing distribution of growth rates"""
    
    fig = go.Figure()
    
    components = [
        ('PFCE_growth', 'Private\nConsumption'),
        ('GFCE_growth', 'Govt\nConsumption'),
        ('GFCF_growth', 'Investment'),
        ('exports_growth', 'Exports'),
        ('imports_growth', 'Imports'),
        ('GDP_growth', 'GDP')
    ]
    
    for col, label in components:
        fig.add_trace(go.Box(
            y=df[col],
            name=label,
            boxmean='sd'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='Distribution of Growth Rates by Component (2012-2023)',
        yaxis_title='Growth Rate (%)',
        height=450
    )
    
    return fig

def create_quarterly_growth_heatmap(df):
    """Heatmap of GDP growth by year and quarter"""
    
    df_pivot = df.copy()
    df_pivot['year_only'] = df_pivot['year']
    
    pivot = df_pivot.pivot_table(
        index='year_only',
        columns='quarter',
        values='GDP_growth',
        aggfunc='first'
    )
    
    quarter_order = ['Q1', 'Q2', 'Q3', 'Q4']
    pivot = pivot[[q for q in quarter_order if q in pivot.columns]]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=0,
        text=pivot.values.round(2),
        texttemplate='%{text}%',
        textfont={"size": 10},
        colorbar=dict(title="Growth %")
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='GDP Growth Rate Heatmap (% YoY)',
        xaxis_title='Quarter',
        yaxis_title='Fiscal Year',
        height=500,
    )
    
    return fig

def create_inflation_chart(df):
    """Inflation trends - CPI and WPI"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['CPI_inflation_yoy'],
        name='CPI Inflation',
        mode='lines',
        line=dict(color=COLORS['danger'], width=2),
        hovertemplate='<b>CPI</b><br>%{y:.2f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['WPI_inflation_yoy'],
        name='WPI Inflation',
        mode='lines',
        line=dict(color=COLORS['warning'], width=2),
        hovertemplate='<b>WPI</b><br>%{y:.2f}%<extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_hline(y=4, line_dash="dot", line_color="green", annotation_text="RBI Target (4%)")
    fig.add_hline(y=6, line_dash="dot", line_color="red", annotation_text="Upper Tolerance (6%)")
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='Inflation Trends (Year-over-Year %)',
        xaxis_title='',
        yaxis_title='Inflation Rate (%)',
        hovermode='x unified',
        height=450
    )
    
    return fig

def create_trade_balance_chart(df):
    """Trade balance over time"""
    
    fig = go.Figure()
    
    colors = ['#2ca02c' if x > 0 else '#d62728' for x in df['trade_balance_rupees']]
    
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['trade_balance_rupees'],
        name='Trade Balance',
        marker=dict(color=colors),
        hovertemplate='<b>%{x|%Y %b}</b><br>Balance: ₹%{y:,.0f} Cr<extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='Trade Balance (Exports - Imports) in ₹ Crores',
        xaxis_title='',
        yaxis_title='₹ Crores',
        hovermode='x',
        height=450,
        annotations=[
            dict(
                text="Surplus" if df['trade_balance_rupees'].iloc[-1] > 0 else "Deficit",
                xref="paper", yref="paper",
                x=0.95, y=0.95,
                showarrow=False,
                font=dict(size=14, color="green" if df['trade_balance_rupees'].iloc[-1] > 0 else "red")
            )
        ]
    )
    
    return fig

def create_exports_imports_chart(df):
    """Exports and imports trends"""
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['exports_rupees'],
            name='Exports',
            mode='lines',
            line=dict(color='#2ca02c', width=2),
            hovertemplate='<b>Exports</b><br>₹%{y:,.0f} Cr<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['imports_rupees'],
            name='Imports',
            mode='lines',
            line=dict(color='#d62728', width=2),
            hovertemplate='<b>Imports</b><br>₹%{y:,.0f} Cr<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['import_cover_ratio'],
            name='Import Cover Ratio',
            mode='lines',
            line=dict(color='#1f77b4', width=2, dash='dash'),
            hovertemplate='<b>Ratio</b><br>%{y:.2f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="₹ Crores", secondary_y=False)
    fig.update_yaxes(title_text="Import Cover Ratio", secondary_y=True)
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='Exports & Imports Trends',
        hovermode='x unified',
        height=450
    )
    
    return fig

def create_forex_reserves_chart(df):
    """Forex reserves trend"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_reserves_usd'],
        name='Total Reserves (USD)',
        mode='lines',
        line=dict(color=COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.2)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>$%{y:,.0f}M<extra></extra>'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='Foreign Exchange Reserves (USD Million)',
        xaxis_title='',
        yaxis_title='USD Million',
        hovermode='x',
        height=450
    )
    
    return fig

def create_rbi_rates_chart(df):
    """RBI policy rates over time"""
    
    fig = go.Figure()
    
    rates = [
        ('repo_rate', 'Repo Rate'),
        ('reverse_repo', 'Reverse Repo'),
        ('crr', 'CRR'),
        ('slr', 'SLR')
    ]
    
    colors = ['#d62728', '#2ca02c', '#ff7f0e', '#1f77b4']
    
    for (col, label), color in zip(rates, colors):
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[col],
            name=label,
            mode='lines',
            line=dict(color=color, width=2),
            hovertemplate=f'<b>{label}</b><br>%{{y:.2f}}%<extra></extra>'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 26, 46, 0.5)',
        font=dict(color='#e0e7ff', family='Inter, sans-serif', size=12),
        title_font=dict(color='#c4b5fd', size=18, family='Inter'),
        title='RBI Policy Rates Over Time',
        xaxis_title='',
        yaxis_title='Rate (%)',
        hovermode='x unified',
        height=450
    )
    
    return fig