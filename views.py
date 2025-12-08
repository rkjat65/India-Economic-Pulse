import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from visualizations import *

def render_overview(all_data):
    """Render the main overview dashboard"""
    gdp_data = all_data['gdp']
    inflation_data = all_data['inflation']
    trade_data = all_data['trade']
    forex_data = all_data['forex']
    rbi_rates_data = all_data['rbi_rates']

    # Latest Values
    latest_gdp = gdp_data.iloc[-1]
    latest_inflation = inflation_data.iloc[-1]
    latest_trade = trade_data.iloc[-1]
    latest_forex = forex_data.iloc[-1]
    latest_rbi = rbi_rates_data.iloc[-1]

    st.markdown('<div class="section-header"><h2>📈 Key Economic Pulse</h2></div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">GDP Growth</div>
                <div class="metric-value">{latest_gdp['GDP_growth']:.2f}%</div>
                <div class="metric-delta">{latest_gdp['GDP_growth_change']:.2f}% QoQ</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">CPI Inflation</div>
                <div class="metric-value">{latest_inflation['CPI_inflation_yoy']:.2f}%</div>
                <div class="metric-delta">YoY</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        trade_status = "Surplus" if latest_trade['trade_balance_rupees'] > 0 else "Deficit"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Trade Balance</div>
                <div class="metric-value">{trade_status}</div>
                <div class="metric-delta">₹{abs(latest_trade['trade_balance_rupees']):,.0f}Cr</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Forex Reserves</div>
                <div class="metric-value">${latest_forex['total_reserves_usd']:,.0f}M</div>
                <div class="metric-delta">{latest_forex['reserves_growth_yoy']:.1f}% YoY</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Repo Rate</div>
                <div class="metric-value">{latest_rbi['repo_rate']:.2f}%</div>
                <div class="metric-delta">Current</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Summary Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("GDP Growth Trend")
        st.plotly_chart(create_gdp_growth_chart(gdp_data.tail(20)), use_container_width=True, key="overview_gdp")
    with col2:
        st.subheader("Inflation Trend")
        st.plotly_chart(create_inflation_chart(inflation_data.tail(24)), use_container_width=True, key="overview_inflation")


def render_gdp_view(all_data):
    """Render Detailed GDP Analysis"""
    st.markdown('<h2 class="page-title">📊 GDP Growth Analysis</h2>', unsafe_allow_html=True)
    
    gdp_data = all_data['gdp']
    
    # Filters handled globally in app.py
    filtered_gdp = gdp_data
        
    st.plotly_chart(create_gdp_growth_chart(filtered_gdp), use_container_width=True, key="gdp_main")
    
    tab1, tab2, tab3 = st.tabs(["Components", "Distribution", "Heatmap"])
    
    with tab1:
        st.plotly_chart(create_gdp_components_growth_chart(filtered_gdp), use_container_width=True, key="gdp_comp")
    with tab2:
        st.plotly_chart(create_growth_distribution_boxplot(filtered_gdp), use_container_width=True, key="gdp_dist")
    with tab3:
        st.plotly_chart(create_quarterly_growth_heatmap(filtered_gdp), use_container_width=True, key="gdp_heat")


def render_inflation_view(all_data):
    """Render Detailed Inflation Analysis"""
    st.markdown('<h2 class="page-title">💰 Inflation Analysis</h2>', unsafe_allow_html=True)
    
    inflation_data = all_data['inflation']
    st.plotly_chart(create_inflation_chart(inflation_data), use_container_width=True, key="infl_main")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Latest CPI: **{:.2f}%**".format(inflation_data.iloc[-1]['CPI_inflation_yoy']))
    with col2:
        st.info("Latest WPI: **{:.2f}%**".format(inflation_data.iloc[-1]['WPI_inflation_yoy']))


def render_trade_view(all_data):
    """Render Detailed Trade Analysis"""
    st.markdown('<h2 class="page-title">🌐 Trade Analysis</h2>', unsafe_allow_html=True)
    
    trade_data = all_data['trade']
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_trade_balance_chart(trade_data.tail(36)), use_container_width=True, key="trade_bal")
    with col2:
        st.plotly_chart(create_exports_imports_chart(trade_data.tail(36)), use_container_width=True, key="trade_exim")


def render_forex_view(all_data):
    """Render Forex & Rates"""
    st.markdown('<h2 class="page-title">💵 Forex & Rates</h2>', unsafe_allow_html=True)
    
    forex_data = all_data['forex']
    rbi_rates_data = all_data['rbi_rates']
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_forex_reserves_chart(forex_data), use_container_width=True, key="forex_main")
    with col2:
        st.plotly_chart(create_rbi_rates_chart(rbi_rates_data), use_container_width=True, key="rbi_main")
