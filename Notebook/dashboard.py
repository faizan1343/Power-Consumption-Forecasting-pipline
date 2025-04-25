import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import os

# Define the directory relative to the script
PICKLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "files")

@st.cache_data
def load_forecast_data():
    return pd.read_pickle(os.path.join(PICKLE_DIR, "forecast_results.pkl"))

# Load data
df = pd.read_pickle(os.path.join(PICKLE_DIR, 'volatility_dataset.pkl'))
forecast_results = pd.read_pickle(os.path.join(PICKLE_DIR, 'forecast_results.pkl'))
#streamlit run "e:/TIme series proj/Notebook/dashboard.py"
# Set page configuration with a modern theme
st.set_page_config(page_title="Power Consumption Forecasting Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for attractiveness
st.markdown(
    """
    <style>
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
    }
    .stSelectbox, .stSlider {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    .css-1aumxhk {
        background-color: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load data
PICKLE_DIR = r"E:\TIme series proj\files"  # Adjust path if needed
df = pd.read_pickle(os.path.join(PICKLE_DIR, 'volatility_dataset.pkl'))
forecast_results = pd.read_pickle(os.path.join(PICKLE_DIR, 'forecast_results.pkl'))

# Simulate temperature data for AEP region states (hypothetical, replace with real data if available)
aep_states = ['Ohio', 'West Virginia', 'Kentucky', 'Virginia', 'Indiana', 'Michigan', 'Tennessee']
temp_data = pd.DataFrame({
    'state': aep_states,
    'temperature': [15.5, 14.2, 16.0, 13.8, 14.5, 12.3, 17.1]  # Simulated avg temps in °C for April 2025
})
temp_data['code'] = temp_data['state'].map({'Ohio': 'OH', 'West Virginia': 'WV', 'Kentucky': 'KY', 
                                          'Virginia': 'VA', 'Indiana': 'IN', 'Michigan': 'MI', 'Tennessee': 'TN'})

# Title and description with a modern look
st.title("Power Consumption Forecasting Dashboard")
st.markdown(
    """
    <h4 style='color: #4CAF50;'>Explore 168-Hour Load Forecasts, Volatility, and Temperature Map (2004-01-10 to 2018-08-03)</h4>
    This interactive dashboard showcases forecasts using ARIMA, SARIMA, Exponential Smoothing, and GARCH models, 
    with a temperature map for the AEP region. Dive into the results and model comparisons!
    """, unsafe_allow_html=True
)

# Sidebar for interactivity
st.sidebar.header("Dashboard Controls")
model_select = st.sidebar.selectbox("Select Model for Focus", ["All", "SARIMA", "Exponential Smoothing"], index=0)
time_range = st.sidebar.slider("Select Forecast Horizon (Hours)", 1, 168, (1, 168))

# Corrected 168-Hour Load Forecasts and Volatility Plot
st.header("Corrected 168-Hour Load Forecasts and Volatility")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=forecast_results.index, y=forecast_results['ARIMA_Forecast'], mode='lines', name='ARIMA', line=dict(color='#FF9999')))
fig1.add_trace(go.Scatter(x=forecast_results.index, y=forecast_results['SARIMA_Forecast'], mode='lines', name='SARIMA', line=dict(color='#FFCC00')))
fig1.add_trace(go.Scatter(x=forecast_results.index, y=forecast_results['ES_Forecast'], mode='lines', name='Exponential Smoothing', line=dict(color='#33CC33')))
fig1.add_trace(go.Scatter(x=forecast_results.index, y=forecast_results['GARCH_Variance']**0.5, mode='lines', name='GARCH Volatility', line=dict(color='#6666FF')))
fig1.update_layout(
    title='168-Hour Load Forecasts and Volatility',
    xaxis_title='Hours Ahead (2018-08-03 to 2018-08-10)',
    yaxis_title='Load/Volatility (MW)',
    template='plotly_dark',
    plot_bgcolor='#1E1E1E',
    paper_bgcolor='#1E1E1E',
    font=dict(color='#FFFFFF')
)
st.plotly_chart(fig1)

# Temperature Map
st.header("AEP Region Temperature Map")
fig_map = px.choropleth(
    temp_data,
    locations='code',
    locationmode='USA-states',
    color='temperature',
    color_continuous_scale='RdYlBu_r',
    range_color=[12, 18],
    scope='usa',
    labels={'temperature': 'Avg Temp (°C)'},
    title='Average Temperature in AEP Region (April 2025)'
)
fig_map.update_layout(
    template='plotly_dark',
    plot_bgcolor='#1E1E1E',
    paper_bgcolor='#1E1E1E',
    font=dict(color='#FFFFFF'),
    geo=dict(bgcolor='#1E1E1E')
)
st.plotly_chart(fig_map)

# Forecasting Results with interactivity
st.header("Detailed Forecasting Results")
start_idx, end_idx = time_range
selected_data = forecast_results.iloc[start_idx-1:end_idx]
fig2 = go.Figure()
if model_select == "All":
    fig2.add_trace(go.Scatter(x=selected_data.index, y=selected_data['ARIMA_Forecast'], mode='lines', name='ARIMA', line=dict(color='#FF9999')))
    fig2.add_trace(go.Scatter(x=selected_data.index, y=selected_data['SARIMA_Forecast'], mode='lines', name='SARIMA', line=dict(color='#FFCC00')))
    fig2.add_trace(go.Scatter(x=selected_data.index, y=selected_data['ES_Forecast'], mode='lines', name='Exponential Smoothing', line=dict(color='#33CC33')))
else:
    forecast_data = selected_data['ES_Forecast'] if model_select == "Exponential Smoothing" else selected_data[f'{model_select}_Forecast']
    fig2.add_trace(go.Scatter(x=selected_data.index, y=forecast_data, mode='lines', name=model_select, line=dict(color='#FFCC00' if model_select == "SARIMA" else '#33CC33')))
fig2.update_layout(
    title=f'{model_select if model_select != "All" else "Multi-Model"} 168-Hour Forecast',
    xaxis_title='Hours Ahead',
    yaxis_title='Load (MW)',
    template='plotly_dark',
    plot_bgcolor='#1E1E1E',
    paper_bgcolor='#1E1E1E',
    font=dict(color='#FFFFFF')
)
st.plotly_chart(fig2)

# Model Comparison Metrics with Gauges
st.header("Model Performance Metrics")
metrics = {
    "ARIMA": {"AIC": 1747740, "Residual Std Dev": 327.54},
    "SARIMA": {"AIC": 1602426, "Residual Std Dev": 183.81},
    "Exponential Smoothing": {"AIC": 1385098, "Residual Std Dev": 301.64},
    "GARCH": {"AIC": -70.37, "Residual Std Dev": 0.259}
}
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("ARIMA AIC", f"{metrics['ARIMA']['AIC']:,}")
    st.metric("ARIMA Res Std Dev", f"{metrics['ARIMA']['Residual Std Dev']:.2f}")
with col2:
    st.metric("SARIMA AIC", f"{metrics['SARIMA']['AIC']:,}")
    st.metric("SARIMA Res Std Dev", f"{metrics['SARIMA']['Residual Std Dev']:.2f}")
with col3:
    st.metric("ES AIC", f"{metrics['Exponential Smoothing']['AIC']:,}")
    st.metric("ES Res Std Dev", f"{metrics['Exponential Smoothing']['Residual Std Dev']:.2f}")
with col4:
    st.metric("GARCH AIC", f"{metrics['GARCH']['AIC']:.2f}")
    st.metric("GARCH Res Std Dev", f"{metrics['GARCH']['Residual Std Dev']:.3f}")

# Final Summary
st.header("Project Summary")
with open(os.path.join(PICKLE_DIR, 'final_summary.txt'), 'r') as f:
    summary = f.read()
st.markdown(summary, unsafe_allow_html=True)

# Future Enhancements
st.sidebar.header("Future Enhancements")
st.sidebar.info("Add real temperature data or historical trends with more datasets!")

# Run the app
if __name__ == "__main__":
    st.sidebar.success("Dashboard loaded successfully!")