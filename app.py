"""
India Economic Pulse - Main Application
Enhanced with AI Image Generation capability
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# Import existing modules
from data_fetcher import load_all_data
from views import render_gdp_view, render_inflation_view, render_trade_view, render_forex_view, render_overview
from utils_ui import load_css, render_sidebar

# Import new AI Image Generator
from ai_image_generator import render_image_generator_ui, add_to_app_sidebar


# Page Configuration
st.set_page_config(
    page_title="India Economic Pulse 🇮🇳",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
load_css()

# Initialize session state
if 'show_image_generator' not in st.session_state:
    st.session_state['show_image_generator'] = False
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'Overview'


def main():
    """Main application logic"""
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='color: #FF9933; margin: 0;'>🇮🇳 India Economic Pulse</h1>
            <p style='color: #128807; font-size: 1.1rem; margin-top: 0.5rem;'>
                Real-time Economic Intelligence Dashboard (2012-2025)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("📊 Loading economic data..."):
        raw_data = load_all_data()
        data = {
            'gdp': raw_data['GDP'],
            'inflation': raw_data['Inflation'],
            'trade': raw_data['Foreign Trade'],
            'forex': raw_data['Forex Reserves'],
            'rbi_rates': raw_data['RBI Rates'],
        }

    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 📌 Navigation")
        
        selected_view = option_menu(
            menu_title=None,
            options=["Overview", "GDP Analysis", "Inflation Tracker", "Trade Dynamics", "Forex & Rates", "AI Image Generator"],
            icons=["speedometer2", "graph-up-arrow", "fire", "globe-asia-pacific", "currency-exchange", "palette"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#0E1117"},
                "icon": {"color": "#FF9933", "font-size": "18px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "#FAFAFA",
                    "--hover-color": "#262730",
                },
                "nav-link-selected": {"background-color": "#128807"},
            }
        )
        
        st.session_state['current_view'] = selected_view
        
        # Sidebar filters (if not in AI Generator view)
        if selected_view != "AI Image Generator":
            render_sidebar()
        
        # Quick AI Generator access
        if selected_view != "AI Image Generator":
            st.markdown("---")
            st.markdown("### 🎨 Quick AI Generator")
            if st.button("🚀 Generate Economic Viz", use_container_width=True, type="primary"):
                st.session_state['show_image_generator'] = True
                st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; font-size: 0.8rem; color: #888;'>
                <p><strong>Created by RK Jat</strong></p>
                <p>
                    <a href='https://rkjat.in' target='_blank' style='color: #FF9933;'>Website</a> | 
                    <a href='https://linkedin.com/in/rkjat65' target='_blank' style='color: #FF9933;'>LinkedIn</a> | 
                    <a href='https://github.com/rkjat65' target='_blank' style='color: #FF9933;'>GitHub</a>
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Main Content Area
    if selected_view == "Overview":
        render_overview(data)
    
    elif selected_view == "GDP Analysis":
        render_gdp_view(data)
    
    elif selected_view == "Inflation Tracker":
        render_inflation_view(data)
    
    elif selected_view == "Trade Dynamics":
        render_trade_view(data)
    
    elif selected_view == "Forex & Rates":
        render_forex_view(data)
    
    elif selected_view == "AI Image Generator":
        # Full AI Image Generator Interface
        st.markdown("## 🎨 AI Economic Visualization Generator")
        st.markdown("""
            Generate professional economic visualizations, infographics, and social media content 
            powered by AI. Perfect for presentations, reports, and social media posts.
        """)
        
        # Render the full image generator UI
        render_image_generator_ui(current_view=st.session_state.get('current_view'))
    
    # Show image generator popup if triggered from other views
    if st.session_state.get('show_image_generator') and selected_view != "AI Image Generator":
        with st.expander("🎨 AI Image Generator", expanded=True):
            render_image_generator_ui(current_view=selected_view)
            if st.button("Close Generator"):
                st.session_state['show_image_generator'] = False
                st.rerun()


if __name__ == "__main__":
    main()