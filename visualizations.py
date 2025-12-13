"""
Professional-grade visualization functions for Economic Pulse Dashboard
Enhanced with animations, advanced interactivity, and publication-quality styling
AI-powered chart generation and social media integration
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils import get_color_palette, create_annotation_dict
import streamlit as st
from datetime import datetime

# Modern Professional Color Palette
COLORS = get_color_palette('professional')

# Enhanced Professional Template with Animations
PROFESSIONAL_TEMPLATE = {
    'layout': {
        'template': 'plotly_dark',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(30, 41, 59, 0.4)',  # Subtle background
        'font': {
            'color': '#e2e8f0',
            'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            'size': 13
        },
        'title_font': {
            'color': '#f8fafc',
            'size': 22,
            'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            'weight': 700
        },
        'title_x': 0.02,
        'title_xanchor': 'left',
        'title_y': 0.95,
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': 'rgba(30, 41, 59, 0.95)',
            'bordercolor': '#0ea5e9',
            'font': {'color': '#f8fafc', 'size': 13, 'family': 'Inter'},
            'namelength': -1,
            'align': 'left'
        },
        'xaxis': {
            'gridcolor': 'rgba(51, 65, 85, 0.3)',
            'showgrid': True,
            'zeroline': False,
            'gridwidth': 1,
            'linecolor': '#475569',
            'tickcolor': '#64748b',
            'tickfont': {'color': '#cbd5e1', 'size': 11}
        },
        'yaxis': {
            'gridcolor': 'rgba(51, 65, 85, 0.3)',
            'showgrid': True,
            'zeroline': False,
            'gridwidth': 1,
            'linecolor': '#475569',
            'tickcolor': '#64748b',
            'tickfont': {'color': '#cbd5e1', 'size': 11}
        },
        'colorway': ['#0ea5e9', '#8b5cf6', '#10b981', '#ef4444', '#f59e0b', '#06b6d4', '#ec4899', '#84cc16'],
        'legend': {
            'bgcolor': 'rgba(30, 41, 59, 0.8)',
            'bordercolor': '#475569',
            'font': {'color': '#e2e8f0', 'size': 12}
        },
        'annotations': [],
        'shapes': []
    }
}

def add_watermark(fig: go.Figure, twitter_handle: str = "@YourHandle") -> go.Figure:
    """Add watermark and social media branding to chart"""
    
    # Add twitter handle watermark
    fig.add_annotation(
        text=twitter_handle,
        xref="paper", yref="paper",
        x=0.99, y=0.01,
        showarrow=False,
        font=dict(size=11, color='rgba(100, 116, 139, 0.7)', family='Inter'),
        align="right",
        bgcolor='rgba(15, 23, 42, 0.8)',
        bordercolor='rgba(100, 116, 139, 0.3)'
    )
    
    # Add "Economic Pulse" branding
    fig.add_annotation(
        text="Economic Pulse Dashboard",
        xref="paper", yref="paper",
        x=0.01, y=0.01,
        showarrow=False,
        font=dict(size=10, color='rgba(56, 189, 248, 0.8)', family='Inter', weight='bold'),
        align="left"
    )
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    fig.add_annotation(
        text=f"Generated: {timestamp}",
        xref="paper", yref="paper",
        x=0.5, y=0.01,
        showarrow=False,
        font=dict(size=9, color='rgba(100, 116, 139, 0.6)', family='Inter'),
        align="center"
    )
    
    return fig

def create_animated_transition(fig: go.Figure) -> go.Figure:
    """Add smooth animations to chart"""
    
    fig.update_layout(
        transition={'duration': 800, 'easing': 'cubic-in-out'},
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [{
                'label': '▶ Animate',
                'method': 'animate',
                'args': [None, {
                    'frame': {'duration': 500, 'redraw': True},
                    'transition': {'duration': 300}
                }]
            }]
        }]
    )
    
    return fig

def create_gdp_growth_chart(df, twitter_handle="@YourHandle"):
    """Ultra-enhanced GDP growth rate chart with animations and professional styling"""
    
    fig = go.Figure()
    
    # Create gradient colors based on performance
    colors = []
    for x in df['GDP_growth']:
        if x > 7:
            colors.append('#10b981')  # Excellent growth - green
        elif x > 4:
            colors.append('#38bdf8')  # Good growth - blue
        elif x > 0:
            colors.append('#fbbf24')  # Moderate growth - yellow
        else:
            colors.append('#ef4444')  # Negative growth - red
    
    # Enhanced bars with gradient and glow effect
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['GDP_growth'],
        name='GDP Growth Rate',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.2)', width=2),
            opacity=0.85,
            pattern=dict(
                shape="",
                bgcolor="rgba(255,255,255,0.1)",
                fgcolor="rgba(255,255,255,0.05)"
            )
        ),
        hovertemplate='<b>%{x|%B %Y}</b><br>' +
                      'GDP Growth: <b>%{y:.2f}%</b><br>' +
                      'Quarter: <b>%{customdata}</b><br>' +
                      '<extra></extra>',
        customdata=df['quarter'],
        showlegend=True
    ))
    
    # Enhanced moving average with area fill
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['GDP_growth_ma4'],
        name='4-Quarter Moving Average',
        mode='lines+markers',
        line=dict(
            color='#818cf8',
            width=4,
            shape='spline',
            smoothing=1.3
        ),
        marker=dict(
            size=8, 
            color='#818cf8',
            line=dict(color='white', width=2)
        ),
        fill='tonexty',
        fillcolor='rgba(129, 140, 248, 0.15)',
        hovertemplate='<b>%{x|%B %Y}</b><br>' +
                      'Moving Average: <b>%{y:.2f}%</b><br>' +
                      '<extra></extra>'
    ))
    
    # Add trend line
    if len(df) > 4:
        z = np.polyfit(range(len(df)), df['GDP_growth'], 1)
        trend_line = np.poly1d(z)(range(len(df)))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=trend_line,
            name='Trend Line',
            mode='lines',
            line=dict(
                color='rgba(168, 85, 247, 0.8)',
                width=3,
                dash='dash'
            ),
            hovertemplate='<b>Trend: %{y:.2f}%</b><extra></extra>'
        ))
    
    # Performance zones
    fig.add_hrect(y0=6, y1=10, fillcolor="rgba(16, 185, 129, 0.1)", 
                  annotation_text="Excellent Growth Zone", line_width=0)
    fig.add_hrect(y0=4, y1=6, fillcolor="rgba(56, 189, 248, 0.1)", 
                  annotation_text="Good Growth Zone", line_width=0)
    fig.add_hrect(y0=0, y1=4, fillcolor="rgba(251, 191, 36, 0.1)", 
                  annotation_text="Moderate Growth Zone", line_width=0)
    fig.add_hrect(y0=-5, y1=0, fillcolor="rgba(239, 68, 68, 0.1)", 
                  annotation_text="Contraction Zone", line_width=0)
    
    # Zero line with emphasis
    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color='rgba(255, 255, 255, 0.6)',
        line_width=3,
        opacity=0.8
    )
    
    # Add key economic events annotations
    events = [
        {'date': '2020-04-01', 'text': 'COVID-19 Lockdown', 'color': '#ef4444'},
        {'date': '2016-11-01', 'text': 'Demonetization', 'color': '#f59e0b'},
        {'date': '2017-07-01', 'text': 'GST Launch', 'color': '#8b5cf6'}
    ]
    
    for event in events:
        event_date = pd.Timestamp(event['date'])
        if df['date'].min() <= event_date <= df['date'].max():
            # Find closest data point
            closest_idx = (df['date'] - event_date).abs().idxmin()
            y_pos = df.loc[closest_idx, 'GDP_growth']
            
            fig.add_annotation(
                x=event_date,
                y=y_pos + 1,
                text=event['text'],
                showarrow=True,
                arrowhead=2,
                arrowcolor=event['color'],
                arrowwidth=2,
                bgcolor=f"rgba{tuple(list(bytes.fromhex(event['color'][1:])) + [0.2])}",
                bordercolor=event['color'],
                font=dict(size=11, color=event['color'], weight='bold')
            )
    
    # Update layout with enhanced styling
    layout_config = PROFESSIONAL_TEMPLATE['layout'].copy()
    layout_config.update({
        'title': dict(
            text='🇮🇳 India GDP Growth Rate - Quarterly Performance Analysis',
            font=dict(size=24, color='#f8fafc', weight='bold')
        ),
        'xaxis_title': 'Timeline',
        'yaxis_title': 'Growth Rate (%)',
        'height': 650,
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='#475569'
        ),
        'margin': dict(l=60, r=60, t=100, b=80)
    })
    
    fig.update_layout(**layout_config)
    
    # Add watermark and branding
    fig = add_watermark(fig, twitter_handle)
    
    # Add animation
    fig = create_animated_transition(fig)
    
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
    
    # Create layout config without conflicting annotations
    layout_config = PROFESSIONAL_TEMPLATE['layout'].copy()
    layout_config.update({
        'title': 'Trade Balance (Exports - Imports) in ₹ Crores',
        'xaxis_title': '',
        'yaxis_title': '₹ Crores',
        'height': 450
    })
    
    fig.update_layout(**layout_config)
    
    # Add annotation separately
    fig.add_annotation(
        text="Surplus" if df['trade_balance_rupees'].iloc[-1] > 0 else "Deficit",
        xref="paper", yref="paper",
        x=0.95, y=0.95,
        showarrow=False,
        font=dict(size=14, color="green" if df['trade_balance_rupees'].iloc[-1] > 0 else "red")
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