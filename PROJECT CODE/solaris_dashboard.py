import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

st.set_page_config(page_title="Solar Performance Dashboard", layout="wide")
st.title("☀️ Solar Yield & Inverter Performance Dashboard")

@st.cache_data
def load_and_process_data():
  years= [2020, 2023, 2025, 2026]
  df_list= [pd.read_csv(f'Analysis_{year}.csv',delimiter=";") for year in years]
  solaris_df= pd.concat(df_list,axis=0)
  solaris_df= solaris_df.rename(columns= {solaris_df.columns[0]: "Date"})

  solaris_df['Date']= (solaris_df['Date'].astype(str)
    .str.replace('=','',regex=False)
    .str.replace('"', '', regex=False).str.strip()
    )

  for col in solaris_df.columns[1:]:
      solaris_df[col] = solaris_df[col].astype(str).str.replace(',', '', regex=False).str.strip()
      solaris_df[col] = pd.to_numeric(solaris_df[col], errors='coerce')

  solaris_df['Datetime'] = pd.to_datetime(solaris_df['Date'], format='%b %y')
  solar_analysis = solaris_df.sort_values('Datetime').reset_index(drop=True)
  solar_analysis['Month'] = solar_analysis['Datetime'].dt.strftime('%b')
  solar_analysis['Year'] = solar_analysis['Datetime'].dt.year

  return solar_analysis

df= load_and_process_data()
inverter_cols = [col for col in df.columns if 'INV NO:' in col]
total_yield_col = 'CIU Arazi / Total yield / Mean values [kWh]'

season_map = {
    'Dec': 'Winter', 'Jan': 'Winter', 'Feb': 'Winter',
    'Mar': 'Spring', 'Apr': 'Spring', 'May': 'Spring',
    'Jun': 'Summer', 'Jul': 'Summer', 'Aug': 'Summer',
    'Sep': 'Autumn', 'Oct': 'Autumn', 'Nov': 'Autumn'
}
season_order = ['Winter', 'Spring', 'Summer', 'Autumn']

month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthly_yearly_total_yield = df.groupby(['Year', 'Month'], observed=False)[total_yield_col].sum().reset_index()
monthly_yearly_total_yield['Month'] = pd.Categorical(monthly_yearly_total_yield['Month'], categories=month_order, ordered=True)
monthly_yearly_total_yield = monthly_yearly_total_yield.sort_values(by=['Year', 'Month']).reset_index(drop=True)

st.sidebar.header("Filters")
selected_years = st.sidebar.multiselect("Select Year(s)", options=df['Year'].unique(), default=df['Year'].unique())
selected_months = st.sidebar.multiselect("Select Month(s)", options=month_order, default=month_order)
filtered_df = df[df['Year'].isin(selected_years) & df['Month'].isin(selected_months)].copy()

tab1, tab2, tab3, tab4 = st.tabs(["PLant Overview", "Inverter Comparison", "Anomaly Analysis", "Forecast Predictions"])

with tab1:
  st.subheader("High-Level Metrics")
  s1, s2, s3 = st.columns(3)
  total_yield = filtered_df[total_yield_col].sum()
  missing_pct = (filtered_df[total_yield_col].isna().sum() / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0

  s1.metric("Total Yield", f"{total_yield:.2f} kWh")
  s2.metric("Missing Values", f"{missing_pct:.2f}%")
  s3.metric("INverters monitored", f"{len(inverter_cols)}")

  st.markdown('----')

  annual_yield = filtered_df.groupby('Year', observed=False)[total_yield_col].sum().reset_index()
  monthly_yearly_total_yield['Season'] = monthly_yearly_total_yield['Month'].map(season_map)
  seasonal_yield_by_year = (
    monthly_yearly_total_yield
    .groupby(['Year', 'Season'], observed=False)[total_yield_col]
    .sum()
    .reset_index()
    .rename(columns={total_yield_col: 'Total Yield [kWh]'}))
  seasonal_yield_by_year['Season'] = pd.Categorical(seasonal_yield_by_year['Season'], categories=season_order, ordered=True)
  seasonal_yield_by_year = seasonal_yield_by_year.sort_values(by=['Year', 'Season']).reset_index(drop=True)

  st.markdown('----')
  st.subheader("Annual Yield & Annual Change")
  fig_annual = px.bar(
      annual_yield, 
      x='Year', 
      y=total_yield_col, 
      color='Year', 
      title='Total Annual Yield by Year',
      labels={'Year_Str': 'Year'},
      color_discrete_sequence=px.colors.sequential.Viridis)

  st.plotly_chart(fig_annual, use_container_width=True)

  
  fig2 = px.bar(
      seasonal_yield_by_year, 
      x='Year', 
      y='Total Yield [kWh]', 
      color='Season',
      barmode='group', 
      title='Total Seasonal Yield by Year',
      color_discrete_sequence= px.colors.qualitative.Pastel)

  st.plotly_chart(fig2, use_container_width=True)
  
  st.subheader('Continous Yield Progress')
  solar_analysis_sorted = filtered_df.sort_values('Datetime').reset_index(drop=True)
  solar_analysis_sorted['Cumulative Yield'] = solar_analysis_sorted[total_yield_col].cumsum()

  fig_sum = go.Figure()
  fig_sum.add_trace(go.Scatter(x=solar_analysis_sorted['Datetime'], y=solar_analysis_sorted[total_yield_col], name="Monthly Yield [kWh]", mode='lines+markers'))
  fig_sum.add_trace(go.Scatter(x=solar_analysis_sorted['Datetime'], y=solar_analysis_sorted['Cumulative Yield'], name="Cumulative Yield [kWh]", mode='lines', line=dict(dash='dash')))
  fig_sum.update_layout(title="Continuous Monthly vs. Cumulative Yield Trend", xaxis_title="Date", yaxis_title="kWh")
  st.plotly_chart(fig_sum, use_container_width=True)

with tab2:

      st.markdown("---")
      st.subheader("Direct Inverter Comparison")

      selected_inverters = st.multiselect("Select Inverters to Compare:", options=inverter_cols, default=inverter_cols[:2])

      if selected_inverters:

          fig_compare_time = px.line(
                    filtered_df,
                    x='Datetime',
                    y=selected_inverters,
                    title="Inverter Yield Over Time",
                    labels={'value': 'Yield [kWh]', 'variable': 'Inverter'},
                    markers=True
                )
          fig_compare_time.update_layout(hovermode='x unified')
          st.plotly_chart(fig_compare_time, use_container_width=True)

          compare_totals = filtered_df[selected_inverters].sum().reset_index()
          compare_totals.columns = ['Inverter', 'Total Yield']
                
          fig_compare_total = px.bar(
                  compare_totals,
                  x='Inverter',
                  y='Total Yield',
                  title="Total Yield (Filtered Period)",
                  color='Inverter',
                  text_auto='.2s'
                )
          fig_compare_total.update_layout(showlegend=False)
          st.plotly_chart(fig_compare_total, use_container_width=True)
      st.markdown("---")
  

with tab3:
    st.subheader("Inverter Performance")
    if not filtered_df.empty:
      filtered_df['Fleet_Mean'] = filtered_df[inverter_cols].mean(axis=1)
      filtered_df['Fleet_Std'] = filtered_df[inverter_cols].std(axis=1)
      filtered_df['Fleet_CV'] = filtered_df['Fleet_Std'] / filtered_df['Fleet_Mean']

      fault_months = filtered_df[filtered_df['Fleet_CV'] > 0.15][['Datetime', 'Month', 'Year', 'Fleet_Mean', 'Fleet_Std', 'Fleet_CV']]

      if not fault_months.empty:
          st.warning("⚠️ High variance detected across the inverter fleet (CV > 0.15) for the following months:")
          st.dataframe(fault_months.sort_values('Fleet_CV', ascending=False))
      else:
          st.success("✅ No high-variance faults detected in the selected timeframe.")

      st.markdown("**Inverter Yield Distribution (Outlier Analysis)**")

      fig_boxplot= px.box(
          filtered_df[inverter_cols],
          title = 'Inverter Yield Distribution and Outliers',
          color_discrete_sequence=px.colors.qualitative.Dark24
      )

      st.plotly_chart(fig_boxplot, use_container_width=True)


with tab4:
  st.subheader("Forecast Predictions")
  df_valid = df[df[total_yield_col].notna() & (df[total_yield_col]> 0)].copy()
  df_monthly= df_valid.groupby(pd.Grouper(key='Datetime', freq='ME'))[total_yield_col].sum().reset_index()

  st.subheader('Yield Forecasting')
  forecast_horizon= st.slider("Select Forecast Horizon (Months):", min_value=1, max_value=24, value=6)
  last_date= df_monthly['Datetime'].iloc[-1]
  last_yield = df_monthly[total_yield_col].iloc[-1]
  model = ExponentialSmoothing(df_monthly[total_yield_col], trend='add', seasonal='add', seasonal_periods=12)
  fitted_model= model.fit()
  forecast_values = fitted_model.forecast(forecast_horizon)
  future_dates = pd.date_range(start=last_date, periods=forecast_horizon + 1, freq='ME')[1:]

  df_forecast= pd.DataFrame({'Datetime': future_dates, 'Forecast Yield': forecast_values.values})
  
  connector_row = pd.DataFrame({'Datetime': [last_date], 'Forecast Yield': [last_yield]})
  df_forecast_plot = pd.concat([connector_row, df_forecast], ignore_index=True)

  forecast_fig= go.Figure()

  forecast_fig.add_trace(go.Scatter(
    x= df_monthly['Datetime'],
    y= df_monthly[total_yield_col],
    mode= 'lines+markers',
    name= 'Historical Yield',
    line= dict(color= '#1f77b4', width=2)
  ))

  forecast_fig.add_trace(go.Scatter(
    x= df_forecast['Datetime'],
    y= df_forecast['Forecast Yield'],
    mode= 'lines+markers',
    name= 'Forecast Yield',
    line= dict(color= '#ff7f0e', width=2, dash='dash')
  ))

  forecast_fig.update_layout(
    title= 'Historical vs Forecasted Solar Yield',
    xaxis_title= 'Date',
    yaxis_title= 'Solar Yield [kWh]',
    hovermode= 'x unified',
    height= 500
  )

  st.plotly_chart(forecast_fig, use_container_width=True)

