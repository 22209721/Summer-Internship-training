# ☀️ Solar Yield & Inverter Performance Dashboard

This repository contains a data analysis and interactive visualization suite for monitoring solar inverter site performance. It includes a Python-based Streamlit dashboard for real-time monitoring and forecasting, alongside a Jupyter Notebook for in-depth Exploratory Data Analysis (EDA) and data preprocessing.

## 📊 Features

### 1. Interactive Streamlit Dashboard

The Streamlit application provides an interactive web interface with sidebar filtering for specific years and months. It features four main analysis tabs:

* **Plant Overview:** Displays high-level metrics including total yield, missing value percentages, and the number of monitored inverters. It also visualizes total annual yield, total annual yield by seaon, and continuous cumulative yield trends.


* **Inverter Performance:** It includes direct time-series comparisons between selected inverters


* **Anomaly Analysis:** Automatically detects high-variance faults across the fleet if the Coefficient of Variation (CV) exceeds 0.15. and boxplots for outlier analysis.


* **Forecast Predictions:** Uses an Exponential Smoothing model with an additive trend and 12-month seasonal periods to predict future solar yield. Users can dynamically adjust the forecast horizon between 1 and 24 months.



### 2. Exploratory Data Analysis (EDA) Notebook

The Jupyter Notebook is designed for initial data ingestion, cleaning, and statistical profiling:

* Merges raw, semicolon-delimited CSV files spanning the years 2020, 2023, 2025, and 2026.


* Cleans string artifacts (like equal signs and quotes), standardizes date formats, and converts yield values to numeric data types.


* Calculates the overall missing data percentage across the entire dataset.


* Generates detailed descriptive statistics for each inverter, including mean, standard deviation, variance, skewness, kurtosis, quartiles (Q1, Q3), IQR, min, max, median, and mode.


* Exports the cleaned dataset as `solar_analysis_final_data.csv` and the statistical summary as `inverter_descriptive_statistics.csv`.



## Repository Structure

* `app.py`: The main Streamlit application script containing the dashboard logic.


* `EDA_Notebook.ipynb`: The Jupyter Notebook used for initial data exploration and generating the final descriptive statistics.


* `Analysis_YYYY.csv`: The required input data files containing monthly mean yield values for the overall site and individual inverters.



## Prerequisites and Installation

To run this project locally, ensure you have Python 3 installed along with the following dependencies.

```bash
pip install streamlit pandas numpy plotly statsmodels matplotlib seaborn

```

Note: `matplotlib` and `seaborn` are primarily used within the EDA notebook, while `streamlit`, `plotly`, and `statsmodels` power the interactive dashboard.

## Usage

### Running the Dashboard

1. Ensure your raw data files (`Analysis_2020.csv`, `Analysis_2023.csv`, `Analysis_2025.csv`, `Analysis_2026.csv`) are located in the same directory as the Python script.


2. Launch the Streamlit app from your terminal:
```bash
streamlit run app.py OR python -m streamlit run app.py

```


3. Open the provided localhost URL in your web browser to interact with the dashboard.

### Running the EDA Notebook

1. Open the Jupyter Notebook in your preferred environment (e.g., JupyterLab, VS Code, or Google Colab).
2. Execute the cells sequentially to process the raw `.csv` files and view the statistical outputs.


3. Retrieve your cleaned outputs (`solar_analysis_final_data.csv` and `inverter_descriptive_statistics.csv`) from the working directory.
