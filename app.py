import streamlit as st
import pandas as pd
from utils_ui import load_css, load_all_data
from views import (
    render_overview, 
    render_gdp_view, 
    render_inflation_view, 
    render_trade_view, 
    render_forex_view
)

# Page Config
st.set_page_config(
    page_title="India Economic Pulse",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Styles
load_css()
st.markdown("""
<style>
/* Hide default sidebar */
[data-testid="stSidebar"] {
    display: none;
}
/* Adjust top padding since no sidebar */
.main .block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Load Data
with st.spinner("🚀 Starting up..."):
    all_data = load_all_data()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Economic Pulse")
    st.markdown("### Transforming Data into Actionable Insights")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
# Filter Section
with st.expander("📅 Filter Fiscal Years", expanded=False):
    st.markdown('<div class="scrollable-checkbox-list">', unsafe_allow_html=True)
    gdp_data = all_data['gdp']
    years = sorted(gdp_data['year'].unique(), reverse=True)
    
    # Create columns for better layout in expander
    cols = st.columns(3)
    selected_years = []
    
    for i, year in enumerate(years):
        with cols[i % 3]:
            # Default to first 5 years checked
            if st.checkbox(year, value=(i < 5), key=f"filter_{year}"):
                selected_years.append(year)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Apply global filter logic
if selected_years:
    # Filter GDP
    all_data['gdp'] = all_data['gdp'][all_data['gdp']['year'].isin(selected_years)]
    
    # Filter others based on date range of filtered GDP
    if not all_data['gdp'].empty:
        min_date = all_data['gdp']['date'].min()
        max_date = all_data['gdp']['date'].max()
        
        all_data['inflation'] = all_data['inflation'][(all_data['inflation']['date'] >= min_date) & 
                                                      (all_data['inflation']['date'] <= max_date)]
        all_data['trade'] = all_data['trade'][(all_data['trade']['date'] >= min_date) & 
                                              (all_data['trade']['date'] <= max_date)]
        all_data['forex'] = all_data['forex'][(all_data['forex']['date'] >= min_date) & 
                                              (all_data['forex']['date'] <= max_date)]
        all_data['rbi_rates'] = all_data['rbi_rates'][(all_data['rbi_rates']['date'] >= min_date) & 
                                                      (all_data['rbi_rates']['date'] <= max_date)]
    else:
         st.warning("No data available for selected period")
if selected_years:
    # Filter GDP
    all_data['gdp'] = all_data['gdp'][all_data['gdp']['year'].isin(selected_years)]
    
    # Filter others based on date range of filtered GDP
    min_date = all_data['gdp']['date'].min()
    max_date = all_data['gdp']['date'].max()
    
    all_data['inflation'] = all_data['inflation'][(all_data['inflation']['date'] >= min_date) & 
                                                  (all_data['inflation']['date'] <= max_date)]
    all_data['trade'] = all_data['trade'][(all_data['trade']['date'] >= min_date) & 
                                          (all_data['trade']['date'] <= max_date)]
    # Forex/Rates usually shown as full trend, but let's filter for consistency if desired
    # or keep them full. User said "filters are enough", implies global filter.
    all_data['forex'] = all_data['forex'][(all_data['forex']['date'] >= min_date) & 
                                          (all_data['forex']['date'] <= max_date)]
    all_data['rbi_rates'] = all_data['rbi_rates'][(all_data['rbi_rates']['date'] >= min_date) & 
                                                  (all_data['rbi_rates']['date'] <= max_date)]

st.markdown("---")

# Top Navigation Tabs
tabs = st.tabs(["🏠 Overview", "📊 GDP", "💰 Inflation", "🌐 Trade", "💵 Forex & Rates"])

with tabs[0]:
    render_overview(all_data)

with tabs[1]:
    render_gdp_view(all_data)

with tabs[2]:
    render_inflation_view(all_data)

with tabs[3]:
    render_trade_view(all_data)

with tabs[4]:
    render_forex_view(all_data)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #888;">
        Built with ❤️ by RK Jat | Data Sources: MoSPI, RBI, DGCI&S
    </div>
""", unsafe_allow_html=True)