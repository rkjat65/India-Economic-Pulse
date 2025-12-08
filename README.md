# India Economic Pulse 🇮🇳

A real-time, interactive dashboard tracking India's key economic indicators. Built with **Streamlit** and **Plotly**, featuring a premium "Data Portfolio" design.

## Features

-   **GDP Growth Analysis**: Interactive breakdown of growth components, distribution, and heatmaps.
-   **Inflation Tracking**: Detailed CPI and WPI trends with RBI target bands.
-   **Trade Dynamics**: Visualizing exports, imports, and trade balance (surplus/deficit).
-   **Forex & Rates**: Monitoring foreign exchange reserves and RBI policy rates (Repo, Reverse Repo).
-   **Premium UI**: Custom "Glass & Gradient" design, scrollable filters, and publication-quality charts.

## Live Demo

[Run on Streamlit Cloud](https://streamlit.io/cloud) _(Optional: Add link if deployed)_

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/rkjat65/India-Economic-Pulse.git
    cd India-Economic-Pulse
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the application:
    ```bash
    streamlit run app.py
    ```

## Project Structure

-   `app.py`: Main application entry point and layout controller.
-   `views.py`: Logic for individual dashboard views (GDP, Inflation, etc.).
-   `visualizations.py`: Plotly chart generation with custom themes.
-   `utils_ui.py`: Shared UI components and configurations.
-   `data_fetcher.py`: Data loading and caching logic.
-   `assets/style.css`: Custom CSS for the portfolio theme.

## Author

**RK Jat**  
[Website](https://rkjat.in) | [LinkedIn](https://linkedin.com/in/rkjat65) | [GitHub](https://github.com/rkjat65)