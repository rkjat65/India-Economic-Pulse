import streamlit as st
import pandas as pd
from data_fetcher import EconomicDataFetcher
from visualizations import *

st.set_page_config(
    page_title="India Economic Pulse | Live Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL MODERN CSS - Eye-Catching Design
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main content area */
    .main {
        padding: 0rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Title Section - Gradient Effect */
    h1 {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        font-size: 3.5rem !important;
        letter-spacing: -1px;
        padding: 1rem 0;
        border-bottom: 4px solid;
        border-image: linear-gradient(90deg, #667eea, #764ba2) 1;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #667eea !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
    }
    
    /* Subtitle */
    .subtitle {
        color: #8b5cf6;
        font-size: 1.3rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards - Modern Glass Morphism */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px 0 rgba(102, 126, 234, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Metric Label */
    [data-testid="stMetricLabel"] {
        color: #c4b5fd !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Metric Value */
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    
    /* Metric Delta */
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    
    /* Info/Alert Boxes */
    .stAlert {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    /* Expander - Modern Look */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25), rgba(118, 75, 162, 0.25));
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar - Premium Dark */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #667eea !important;
        background: none !important;
        -webkit-text-fill-color: #667eea !important;
    }
    
    /* Sidebar Text */
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e7ff;
    }
    
    /* Download Buttons - Premium Style */
    .stDownloadButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
    }
    
    /* Tabs - Modern Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px 12px 0 0;
        padding: 12px 24px;
        color: #c4b5fd;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.2);
        color: #e0e7ff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        color: #ffffff;
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    /* Radio Buttons */
    .stRadio label {
        color: #e0e7ff !important;
        font-weight: 500;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stRadio label:hover {
        color: #ffffff !important;
    }
    
    /* Multiselect Tags */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Section Headers with Icon */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 2rem 0 1rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    
    /* Social Links Container */
    .social-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 2rem 0;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .social-link {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        text-decoration: none;
    }
    
    .social-link:hover {
        transform: translateY(-5px) scale(1.1);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5);
    }
    
    .social-link.linkedin {
        background: linear-gradient(135deg, #0077b5, #00a0dc);
    }
    
    .social-link.github {
        background: linear-gradient(135deg, #333, #666);
    }
    
    .social-link.twitter {
        background: linear-gradient(135deg, #1DA1F2, #0d8bd9);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 12px;
        color: #c4b5fd;
    }
    
    .footer strong {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Plotly Chart Container */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #f093fb);
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=3600)
def load_all_data():
    fetcher = EconomicDataFetcher()
    
    data = {}
    for name, file, func in [
        ('gdp', 'gdp_data.csv', fetcher.load_gdp_data),
        ('inflation', 'inflation_data.csv', fetcher.load_inflation_data),
        ('trade', 'trade_data.csv', fetcher.load_trade_data),
        ('forex', 'forex_reserves.csv', fetcher.load_forex_reserves_data),
        ('rbi_rates', 'rbi_rates.csv', fetcher.load_rbi_rates_data),
    ]:
        cached = fetcher.load_from_cache(file)
        data[name] = cached if cached is not None else func()
    
    return data

# Header
st.title("🇮🇳 India Economic Pulse Dashboard")
st.markdown('<p class="subtitle">Comprehensive Economic Analysis (2012-2025)</p>', unsafe_allow_html=True)

# Load data
with st.spinner("⚡ Loading economic data..."):
    all_data = load_all_data()
    gdp_data = all_data['gdp']
    inflation_data = all_data['inflation']
    trade_data = all_data['trade']
    forex_data = all_data['forex']
    rbi_rates_data = all_data['rbi_rates']

if gdp_data.empty:
    st.error("❌ No data available. Please run: `python data_fetcher.py`")
    st.stop()

# Sidebar
with st.sidebar:
    # Indian Flag
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/320px-Flag_of_India.svg.png", width=100)
    
    st.markdown("# 📊 Controls & Filters")
    st.markdown("---")
    
    # Year range filter
    st.markdown("### 📅 Select Fiscal Years")
    years = sorted(gdp_data['year'].unique())
    selected_years = st.multiselect(
        "Choose years to analyze",
        options=years,
        default=years[-5:] if len(years) >= 5 else years,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # View selector
    st.markdown("### 🎯 Dashboard Views")
    view = st.radio(
        "Select your view",
        ["📊 GDP Analysis", "💰 Inflation", "🌐 Trade", "💵 Forex & Rates", "📈 All Indicators"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Data info card
    st.markdown("### 📋 Data Coverage")
    st.info(f"""
    **GDP**: {gdp_data['date'].min().strftime('%b %Y')} - {gdp_data['date'].max().strftime('%b %Y')}
    
    **Inflation**: {inflation_data['date'].min().strftime('%b %Y')} - {inflation_data['date'].max().strftime('%b %Y')}
    
    **Trade**: {trade_data['date'].min().strftime('%b %Y')} - {trade_data['date'].max().strftime('%b %Y')}
    
    **Sources**: MoSPI, RBI, DGCI&S
    """)
    
    st.markdown("---")
    
    # Social Links with Icons
    st.markdown("### 🔗 Connect With Me")
    st.markdown("""
        <div class="social-links">
            <a href="https://linkedin.com/in/yourprofile" target="_blank" class="social-link linkedin" title="LinkedIn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
            </a>
            <a href="https://github.com/rkjat65" target="_blank" class="social-link github" title="GitHub">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
            </a>
            <a href="https://twitter.com/yourhandle" target="_blank" class="social-link twitter" title="Twitter/X">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Built with ❤️ by RK Jat")
    st.caption("© 2025 India Economic Pulse")

# Filter GDP data by selected years
if selected_years:
    filtered_gdp = gdp_data[gdp_data['year'].isin(selected_years)]
else:
    filtered_gdp = gdp_data

# Get latest values
latest_gdp = filtered_gdp.iloc[-1]
latest_inflation = inflation_data.iloc[-1]
latest_trade = trade_data.iloc[-1]
latest_forex = forex_data.iloc[-1]
latest_rbi = rbi_rates_data.iloc[-1]

# Key Metrics Section
st.markdown('<div class="section-header"><span style="font-size: 2rem;">📈</span><h3 style="margin: 0;">Key Economic Indicators</h3></div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="💰 GDP Growth",
        value=f"{latest_gdp['GDP_growth']:.2f}%",
        delta=f"{latest_gdp['GDP_growth_change']:.2f}% QoQ" if pd.notna(latest_gdp['GDP_growth_change']) else "N/A"
    )

with col2:
    st.metric(
        label="📊 CPI Inflation",
        value=f"{latest_inflation['CPI_inflation_yoy']:.2f}%",
        delta="YoY"
    )

with col3:
    trade_status = "Surplus ✅" if latest_trade['trade_balance_rupees'] > 0 else "Deficit ⚠️"
    st.metric(
        label="🌐 Trade Balance",
        value=trade_status,
        delta=f"₹{abs(latest_trade['trade_balance_rupees']):,.0f}Cr"
    )

with col4:
    st.metric(
        label="💵 Forex Reserves",
        value=f"${latest_forex['total_reserves_usd']:,.0f}M",
        delta=f"{latest_forex['reserves_growth_yoy']:.1f}% YoY" if pd.notna(latest_forex['reserves_growth_yoy']) else "N/A"
    )

with col5:
    st.metric(
        label="🏦 Repo Rate",
        value=f"{latest_rbi['repo_rate']:.2f}%",
        delta="Current"
    )

st.markdown("---")

# ========================================
# VIEW: GDP ANALYSIS
# ========================================
if view == "📊 GDP Analysis":
    st.markdown("## 📊 GDP Growth Analysis")
    
    # Main GDP chart
    # st.plotly_chart(
    #     **create_gdp_growth_chart(filtered_gdp)),
    #     use_container_width=True
    # )
    
    with st.expander("💡 Key Insights - GDP Growth"):
        avg_growth = filtered_gdp['GDP_growth'].mean()
        max_growth = filtered_gdp['GDP_growth'].max()
        min_growth = filtered_gdp['GDP_growth'].min()
        max_date = filtered_gdp.loc[filtered_gdp['GDP_growth'].idxmax(), 'date']
        min_date = filtered_gdp.loc[filtered_gdp['GDP_growth'].idxmin(), 'date']
        
        st.write(f"""
        **Growth Performance:**
        - 📊 **Average Growth**: {avg_growth:.2f}%
        - 🔝 **Peak Growth**: {max_growth:.2f}% in {max_date.strftime('%b %Y')}
        - 📉 **Lowest Growth**: {min_growth:.2f}% in {min_date.strftime('%b %Y')}
        - 🎯 **Latest Growth**: {latest_gdp['GDP_growth']:.2f}%
        
        **Recent Trend:** 
        {"📈 Accelerating" if latest_gdp['GDP_growth_change'] > 0 else "📉 Slowing"} 
        ({latest_gdp['GDP_growth_change']:+.2f}% change from previous quarter)
        
        **COVID-19 Impact:**
        - The sharp drop around 2020 reflects pandemic-induced contraction
        - Strong recovery visible in 2021-2022
        """)
    
    # Tabs for detailed analysis
    tab1, tab2, tab3 = st.tabs(["🧩 Components", "📊 Distribution", "🔥 Heatmap"])
    
    with tab1:
        st.markdown("#### GDP Growth Components")
        st.plotly_chart(
            create_gdp_components_growth_chart(filtered_gdp),
            use_container_width=True
        )
        
        st.markdown("**Component Analysis:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Private Consumption Growth",
                f"{latest_gdp['PFCE_growth']:.2f}%"
            )
        
        with col2:
            st.metric(
                "Investment Growth (GFCF)",
                f"{latest_gdp['GFCF_growth']:.2f}%"
            )
        
        with col3:
            st.metric(
                "Exports Growth",
                f"{latest_gdp['exports_growth']:.2f}%"
            )
    
    with tab2:
        st.markdown("#### Distribution of Growth Rates")
        st.plotly_chart(
            create_growth_distribution_boxplot(filtered_gdp),
            use_container_width=True
        )
        
        st.markdown("""
        **Understanding the Box Plot:**
        - Box shows the middle 50% of values (25th to 75th percentile)
        - Line in box = median growth rate
        - Whiskers show range of typical values
        - Dots = outliers (extreme values)
        """)
    
    with tab3:
        st.markdown("#### Growth Rate Heatmap by Year & Quarter")
        st.plotly_chart(
            create_quarterly_growth_heatmap(filtered_gdp),
            use_container_width=True
        )

# ========================================
# VIEW: INFLATION
# ========================================
elif view == "💰 Inflation":
    st.markdown("## 💰 Inflation Analysis")
    
    # Filter inflation data by date range matching GDP
    if selected_years:
        min_date = filtered_gdp['date'].min()
        max_date = filtered_gdp['date'].max()
        filtered_inflation = inflation_data[
            (inflation_data['date'] >= min_date) & 
            (inflation_data['date'] <= max_date)
        ]
    else:
        filtered_inflation = inflation_data
    
    st.plotly_chart(
        create_inflation_chart(filtered_inflation),
        use_container_width=True
    )
    
    with st.expander("💡 Key Insights - Inflation"):
        avg_cpi = filtered_inflation['CPI_inflation_yoy'].mean()
        avg_wpi = filtered_inflation['WPI_inflation_yoy'].mean()
        
        st.write(f"""
        **Inflation Trends:**
        - 📊 **Average CPI Inflation**: {avg_cpi:.2f}%
        - 📊 **Average WPI Inflation**: {avg_wpi:.2f}%
        - 🎯 **Current CPI**: {latest_inflation['CPI_inflation_yoy']:.2f}%
        - 🎯 **Current WPI**: {latest_inflation['WPI_inflation_yoy']:.2f}%
        
        **RBI Targets:**
        - Target: 4% ± 2% (2-6% band)
        - Current Status: {"✅ Within target" if 2 <= latest_inflation['CPI_inflation_yoy'] <= 6 else "⚠️ Outside target"}
        
        **Rural vs Urban:**
        - Rural CPI: {latest_inflation['CPI_rural_inflation_yoy']:.2f}%
        - Urban CPI: {latest_inflation['CPI_urban_inflation_yoy']:.2f}%
        """)
    
    # Detailed inflation metrics
    st.markdown("#### Detailed Inflation Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "CPI - Combined",
            f"{latest_inflation['CPI_inflation_yoy']:.2f}%",
            delta=f"{latest_inflation['CPI_inflation_mom']:.2f}% MoM"
        )
    
    with col2:
        st.metric(
            "CPI - Rural",
            f"{latest_inflation['CPI_rural_inflation_yoy']:.2f}%",
            delta="YoY"
        )
    
    with col3:
        st.metric(
            "CPI - Urban",
            f"{latest_inflation['CPI_urban_inflation_yoy']:.2f}%",
            delta="YoY"
        )

# ========================================
# VIEW: TRADE
# ========================================
elif view == "🌐 Trade":
    st.markdown("## 🌐 Foreign Trade Analysis")
    
    # Filter trade data
    if selected_years:
        min_date = filtered_gdp['date'].min()
        max_date = filtered_gdp['date'].max()
        filtered_trade = trade_data[
            (trade_data['date'] >= min_date) & 
            (trade_data['date'] <= max_date)
        ]
    else:
        filtered_trade = trade_data
    
    # Trade balance chart
    st.plotly_chart(
        create_trade_balance_chart(filtered_trade),
        use_container_width=True
    )
    
    with st.expander("💡 Key Insights - Trade"):
        total_exports = filtered_trade['exports_rupees'].sum()
        total_imports = filtered_trade['imports_rupees'].sum()
        total_deficit = total_imports - total_exports
        avg_cover_ratio = filtered_trade['import_cover_ratio'].mean()
        
        st.write(f"""
        **Trade Performance:**
        - 📤 **Total Exports**: ₹{total_exports:,.0f} Crores
        - 📥 **Total Imports**: ₹{total_imports:,.0f} Crores
        - 📊 **Trade Balance**: ₹{-total_deficit:,.0f} Crores ({"Deficit" if total_deficit > 0 else "Surplus"})
        - 🎯 **Import Cover Ratio**: {avg_cover_ratio:.2f} (Exports/Imports)
        
        **Latest Month:**
        - Exports: ₹{latest_trade['exports_rupees']:,.0f} Cr ({latest_trade['exports_growth_yoy']:.1f}% YoY)
        - Imports: ₹{latest_trade['imports_rupees']:,.0f} Cr ({latest_trade['imports_growth_yoy']:.1f}% YoY)
        - Balance: ₹{latest_trade['trade_balance_rupees']:,.0f} Cr
        """)
    
    # Exports & Imports trend
    st.markdown("#### Exports & Imports Trends")
    st.plotly_chart(
        create_exports_imports_chart(filtered_trade),
        use_container_width=True
    )
    
    # Breakdown by oil/non-oil
    st.markdown("#### Trade Composition")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Exports Composition (Latest)**")
        fig_exports = go.Figure(data=[go.Pie(
            labels=['Oil Exports', 'Non-Oil Exports'],
            values=[latest_trade['exports_oil_rupees'], latest_trade['exports_nonoil_rupees']],
            hole=.3,
            marker_colors=['#ff7f0e', '#2ca02c']
        )])
        fig_exports.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig_exports, use_container_width=True)
    
    with col2:
        st.markdown("**Imports Composition (Latest)**")
        fig_imports = go.Figure(data=[go.Pie(
            labels=['Oil Imports', 'Non-Oil Imports'],
            values=[latest_trade['imports_oil_rupees'], latest_trade['imports_nonoil_rupees']],
            hole=.3,
            marker_colors=['#d62728', '#1f77b4']
        )])
        fig_imports.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig_imports, use_container_width=True)

# ========================================
# VIEW: FOREX & RATES
# ========================================
elif view == "💵 Forex & Rates":
    st.markdown("## 💵 Forex Reserves & Policy Rates")
    
    # Forex reserves
    st.markdown("### Foreign Exchange Reserves")
    st.plotly_chart(
        create_forex_reserves_chart(forex_data),
        use_container_width=True
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Reserves",
            f"${latest_forex['total_reserves_usd']:,.0f}M",
            delta=f"{latest_forex['reserves_growth_yoy']:.1f}% YoY" if pd.notna(latest_forex['reserves_growth_yoy']) else "N/A"
        )
    
    with col2:
        st.metric(
            "Gold Reserves",
            f"${latest_forex['gold_usd']:,.0f}M",
            delta=f"{latest_forex['gold_pct']:.1f}% of total"
        )
    
    with col3:
        st.metric(
            "Foreign Currency Assets",
            f"${latest_forex['fca_usd']:,.0f}M",
            delta=f"{latest_forex['fca_pct']:.1f}% of total"
        )
    
    st.markdown("---")
    
    # RBI Policy Rates
    st.markdown("### RBI Policy Rates")
    st.plotly_chart(
        create_rbi_rates_chart(rbi_rates_data),
        use_container_width=True
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Repo Rate", f"{latest_rbi['repo_rate']:.2f}%")
    
    with col2:
        st.metric("Reverse Repo", f"{latest_rbi['reverse_repo']:.2f}%")
    
    with col3:
        st.metric("CRR", f"{latest_rbi['crr']:.2f}%")
    
    with col4:
        st.metric("SLR", f"{latest_rbi['slr']:.2f}%")
    
    with st.expander("💡 Understanding RBI Rates"):
        st.write("""
        **Key Policy Rates:**
        
        - **Repo Rate**: Rate at which RBI lends to banks. Higher rate = tighter monetary policy
        - **Reverse Repo Rate**: Rate at which RBI borrows from banks
        - **CRR (Cash Reserve Ratio)**: % of deposits banks must keep with RBI
        - **SLR (Statutory Liquidity Ratio)**: % of deposits banks must keep in liquid assets
        
        **Current Stance:** 
        Latest repo rate is {latest_rbi['repo_rate']:.2f}%, indicating 
        {"accommodative" if latest_rbi['repo_rate'] < 5 else "neutral" if latest_rbi['repo_rate'] < 6 else "hawkish"} 
        monetary policy stance.
        """)

# ========================================
# VIEW: ALL INDICATORS
# ========================================
elif view == "📈 All Indicators":
    st.markdown("## 📈 All Economic Indicators - Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### GDP Growth")
        st.plotly_chart(
            create_gdp_growth_chart(filtered_gdp),
            use_container_width=True
        )
    
    with col2:
        st.markdown("### Inflation")
        if selected_years:
            min_date = filtered_gdp['date'].min()
            max_date = filtered_gdp['date'].max()
            filtered_inflation = inflation_data[
                (inflation_data['date'] >= min_date) & 
                (inflation_data['date'] <= max_date)
            ]
        else:
            filtered_inflation = inflation_data
        
        st.plotly_chart(
            create_inflation_chart(filtered_inflation),
            use_container_width=True
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Trade Balance")
        if selected_years:
            filtered_trade = trade_data[
                (trade_data['date'] >= min_date) & 
                (trade_data['date'] <= max_date)
            ]
        else:
            filtered_trade = trade_data
        
        st.plotly_chart(
            create_trade_balance_chart(filtered_trade),
            use_container_width=True
        )
    
    with col4:
        st.markdown("### Forex Reserves")
        st.plotly_chart(
            create_forex_reserves_chart(forex_data),
            use_container_width=True
        )

# ========================================
# DATA DOWNLOAD SECTION
# ========================================
st.markdown("---")
st.markdown("## 📥 Download Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    csv_gdp = filtered_gdp.to_csv(index=False)
    st.download_button(
        label="📄 GDP Data (CSV)",
        data=csv_gdp,
        file_name=f"india_gdp_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col2:
    csv_inflation = inflation_data.to_csv(index=False)
    st.download_button(
        label="📄 Inflation Data (CSV)",
        data=csv_inflation,
        file_name=f"india_inflation_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col3:
    csv_trade = trade_data.to_csv(index=False)
    st.download_button(
        label="📄 Trade Data (CSV)",
        data=csv_trade,
        file_name=f"india_trade_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col4:
    # Excel with all data
    from io import BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        filtered_gdp.to_excel(writer, sheet_name='GDP', index=False)
        inflation_data.to_excel(writer, sheet_name='Inflation', index=False)
        trade_data.to_excel(writer, sheet_name='Trade', index=False)
        forex_data.to_excel(writer, sheet_name='Forex', index=False)
        rbi_rates_data.to_excel(writer, sheet_name='RBI Rates', index=False)
    
    st.download_button(
        label="📊 All Data (Excel)",
        data=buffer.getvalue(),
        file_name=f"india_economic_data_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p><strong>📊 Data Sources:</strong> Ministry of Statistics and Programme Implementation (MoSPI), Reserve Bank of India (RBI), DGCI&S</p>
    <p>📅 Last Updated: November 2025 | All growth rates are Year-over-Year unless specified</p>
    <p>⚠️ <strong>Note:</strong> GDP data represents growth rates (%), not absolute values</p>
    <p style="margin-top: 1rem;">Built by RKJat with passion for data-driven insights 💜</p>
</div>
""", unsafe_allow_html=True)