# 🇮🇳 India Economic Pulse Dashboard

A modern dashboard for analyzing Indian economic data with professional visualizations.

## ✨ Features

### 📊 **Economic Data Analysis**
- **GDP Analysis:** Growth trends, components breakdown, quarterly heatmaps
- **Inflation Tracking:** CPI and WPI trends with RBI targets
- **Trade Dynamics:** Exports, imports, and trade balance
- **Forex & Rates:** Foreign exchange reserves and RBI policy rates
- **Interactive Filters:** Year-wise filtering across all indicators

### 🎯 **Modern UI**
- Sleek dark theme with gradient accents
- Glass morphism effects
- Smooth animations and transitions
- Mobile-responsive design
- Professional color palette

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rkjat65/India-Economic-Pulse.git
   cd "Economic Pulse"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**

   The app will automatically open at: http://localhost:8501

## 📖 Usage

### Viewing Economic Data

1. **Navigate** through tabs: Overview, GDP, Inflation, Trade, Forex & Rates
2. **Filter** data by fiscal years using the expandable filter panel
3. **Interact** with charts - hover for details, zoom, pan

## 📁 Project Structure

```
Economic Pulse/
├── app.py                              # Main application entry point
├── views.py                            # Dashboard view components
├── visualizations.py                   # Chart generation functions
├── data_fetcher.py                     # Data loading utilities
├── utils.py                            # General utilities
├── utils_ui.py                         # UI utilities
├── assets/
│   └── style.css                       # Modern theme CSS
├── data/                               # Economic data CSV files
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## 🎨 UI Theme

The dashboard features a modern dark theme with:
- **Primary Color:** Sky Blue (#0ea5e9)
- **Secondary Color:** Purple (#8b5cf6)
- **Success:** Green (#10b981)
- **Danger:** Red (#ef4444)
- **Background:** Dark Navy with gradient overlays
- **Effects:** Glass morphism, smooth animations, gradient accents

## 📊 Data Sources

- **GDP Data:** Ministry of Statistics and Programme Implementation (MoSPI)
- **Inflation Data:** MoSPI, RBI
- **Trade Data:** Directorate General of Commercial Intelligence & Statistics (DGCI&S)
- **Forex Reserves:** Reserve Bank of India (RBI)
- **Policy Rates:** Reserve Bank of India (RBI)

## 👤 Author

**RK Jat (@rkjat65)**
- Twitter: [@rkjat65](https://twitter.com/rkjat65)
- Website: [rkjat.in](https://rkjat.in)
- LinkedIn: [linkedin.com/in/rkjat65](https://linkedin.com/in/rkjat65)
- GitHub: [github.com/rkjat65](https://github.com/rkjat65)

---

**Built with ❤️ by RK Jat | Data Sources: MoSPI, RBI, DGCI&S**
