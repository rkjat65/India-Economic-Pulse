"""
Professional-grade visualization functions for Economic Pulse Dashboard
Enhanced with animations, advanced interactivity, and publication-quality styling
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils import get_color_palette, create_annotation_dict

# Modern Professional Color Palette
COLORS = get_color_palette('professional')

# Professional chart template
# Vibrant chart template
# Premium Portfolio Chart Template
PROFESSIONAL_TEMPLATE = {
    'layout': {
        'template': 'plotly_dark',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'color': '#94a3b8',
            'family': 'Inter, sans-serif',
            'size': 12
        },
        'title_font': {
            'color': '#f8fafc',
            'size': 18,
            'family': 'Inter, sans-serif',
            'weight': 600
        },
        'title_x': 0,
        'title_xanchor': 'left',
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': '#1e293b',
            'bordercolor': '#334155',
            'font': {'color': '#f8fafc', 'size': 12},
            'namelength': -1
        },
        'xaxis': {
            'gridcolor': '#334155',
            'showgrid': True,
            'zeroline': False,
            'gridwidth': 0.5
        },
        'yaxis': {
            'gridcolor': '#334155',
            'showgrid': True,
            'zeroline': False,
            'gridwidth': 0.5
        },
        'colorway': ['#38bdf8', '#818cf8', '#34d399', '#f87171', '#fbbf24', '#a78bfa']
    }
}

def create_gdp_growth_chart(df):
    """Enhanced GDP growth rate chart with moving average and annotations"""
    
    fig = go.Figure()
    
    # Enhanced bars with gradient colors
    colors = [COLORS['success'] if x > 0 else COLORS['danger'] for x in df['GDP_growth']]
    
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['GDP_growth'],
        name='GDP Growth (%)',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.1)', width=1),
            opacity=0.8
        ),
        hovertemplate='<b>%{x|%B %Y}</b><br>' +
                      'Growth Rate: <b>%{y:.2f}%</b><br>' +
                      '<extra></extra>',
        showlegend=True
    ))
    
    # Enhanced moving average line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['GDP_growth_ma4'],
        name='4-Quarter Moving Average',
        mode='lines+markers',
        line=dict(
            color=COLORS['primary'],
            width=3,
            shape='spline',
            smoothing=1.3
        ),
        marker=dict(size=6, color=COLORS['primary']),
        fill='tonexty',
        fillcolor=f'rgba(102, 126, 234, 0.1)',
        hovertemplate='<b>%{x|%B %Y}</b><br>' +
                      'Moving Avg: <b>%{y:.2f}%</b><br>' +
                      '<extra></extra>'
    ))
    
    # Zero line
    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color=COLORS['text'],
        line_width=2,
        opacity=0.5
    )
    
    # Add COVID-19 annotation if in date range
    covid_date = pd.Timestamp('2020-04-01')
    if df['date'].min() <= covid_date <= df['date'].max():
        fig.add_annotation(
            x=covid_date,
            y=df[df['date'] <= covid_date]['GDP_growth'].iloc[-1] if len(df[df['date'] <= covid_date]) > 0 else 0,
            text="COVID-19 Impact",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLORS['warning'],
            bgcolor='rgba(245, 158, 11, 0.2)',
            bordercolor=COLORS['warning'],
            borderwidth=2,
            font=dict(size=11, color=COLORS['warning'])
        )
    
    # Update layout with professional template
    fig.update_layout(
        **PROFESSIONAL_TEMPLATE['layout'],
        title='India GDP Growth Rate (Year-over-Year %)',
        xaxis_title='',
        yaxis_title='Growth Rate (%)',
        height=550,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)',
            bordercolor='#e0e0e0',
            borderwidth=1
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        transition={'duration': 500}
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
        **PROFESSIONAL_TEMPLATE['layout'],
        title='GDP Growth Components (All in % Growth Rates)',
        xaxis_title='',
        yaxis_title='Growth Rate (%)',
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
        **PROFESSIONAL_TEMPLATE['layout'],
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
        **PROFESSIONAL_TEMPLATE['layout'],
        title='GDP Growth Rate Heatmap (% YoY)',
        xaxis_title='Quarter',
        yaxis_title='Fiscal Year',
        height=500,
    )
    
    return fig

def create_inflation_chart(df):
    """Enhanced inflation trends chart with RBI targets"""
    
    fig = go.Figure()
    
    # CPI Inflation with enhanced styling
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['CPI_inflation_yoy'],
        name='CPI Inflation',
        mode='lines+markers',
        line=dict(
            color=COLORS['danger'],
            width=3,
            shape='spline',
            smoothing=1.3
        ),
        marker=dict(size=5, color=COLORS['danger']),
        fill='tozeroy',
        fillcolor=f'rgba(239, 68, 68, 0.1)',
        hovertemplate='<b>CPI Inflation</b><br>' +
                      '%{x|%B %Y}<br>' +
                      'Rate: <b>%{y:.2f}%</b><br>' +
                      '<extra></extra>'
    ))
    
    # WPI Inflation
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['WPI_inflation_yoy'],
        name='WPI Inflation',
        mode='lines+markers',
        line=dict(
            color=COLORS['warning'],
            width=3,
            shape='spline',
            smoothing=1.3
        ),
        marker=dict(size=5, color=COLORS['warning']),
        hovertemplate='<b>WPI Inflation</b><br>' +
                      '%{x|%B %Y}<br>' +
                      'Rate: <b>%{y:.2f}%</b><br>' +
                      '<extra></extra>'
    ))
    
    # RBI Target lines
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=COLORS['text'],
        line_width=1,
        opacity=0.5
    )
    fig.add_hline(
        y=4,
        line_dash="dot",
        line_color=COLORS['success'],
        line_width=2,
        annotation_text="RBI Target (4%)",
        annotation_position="right"
    )
    fig.add_hline(
        y=6,
        line_dash="dot",
        line_color=COLORS['danger'],
        line_width=2,
        annotation_text="Upper Tolerance (6%)",
        annotation_position="right"
    )
    
    # Update layout
    fig.update_layout(
        **PROFESSIONAL_TEMPLATE['layout'],
        title='Inflation Trends (Year-over-Year %)',
        xaxis_title='',
        yaxis_title='Inflation Rate (%)',
        height=550,
        margin=dict(l=50, r=50, t=80, b=50)
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
        **PROFESSIONAL_TEMPLATE['layout'],
        title='Trade Balance (Exports - Imports) in ₹ Crores',
        xaxis_title='',
        yaxis_title='₹ Crores',
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
        **PROFESSIONAL_TEMPLATE['layout'],
        title='Exports & Imports Trends',
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
        **PROFESSIONAL_TEMPLATE['layout'],
        title='Foreign Exchange Reserves (USD Million)',
        xaxis_title='',
        yaxis_title='USD Million',
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
        **PROFESSIONAL_TEMPLATE['layout'],
        title='RBI Policy Rates Over Time',
        xaxis_title='',
        yaxis_title='Rate (%)',
        height=450
    )
    
    return fig