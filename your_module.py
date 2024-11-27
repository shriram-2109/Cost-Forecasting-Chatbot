import os
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings
import openai
warnings.filterwarnings("ignore")

openai.api_key = os.getenv('OPENAI_API_KEY')

def query_to_code_llm(query: str, columns: str):
    prompt = f"""
    You are a helpful assistant. Your task is to generate Python code to answer questions based on a dataframe named 'salaries_df'.
    The dataframe has the following columns: {columns}.
    
    User query: {query}

    Generate the Python code to answer this query. Ensure the code uses the dataframe 'salaries_df' and returns the result.
    The code should be executable Python code with no extra text.

    Don't add the code to a separate variable and return that variable.
    Eg: For query give me employee names and their salary who works as GENERAL MANAGER-METROPOLITAN TRANSIT AUTHORITY,the code should be 
    
    data_df[data_df['JobTitle'] == 'GENERAL MANAGER-METROPOLITAN TRANSIT AUTHORITY'][['EmployeeName', 'TotalPay']] 
    
    and it should not be
    
    result_df = data_df[data_df['JobTitle'] == 'GENERAL MANAGER-METROPOLITAN TRANSIT AUTHORITY'][['EmployeeName', 'TotalPay']]
    result_df
    
    Don't add '''python (generated code)''' while processing a query.
    Example: For a query provide me monthly data,the code should be 
    
    salaries_df.resample('M', on='UsageDate').sum() 
    
    and it should not be like
    
    ```python
    salaries_df.resample('M', on='UsageDate').sum()
    ```    
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=1
    )
    
    code = response.choices[0].message.content
    return code

def execute_code(code: str, df):
    try:
        local_vars = {'salaries_df': df, 'pd': pd}
        exec(f"result = {code}", {}, local_vars)
        result = local_vars['result']
        return result
    except Exception as e:
        print(f"Error executing code: {e}")
        return None
    
def check_if_dataframe_with_date(result, date_col, value_col):
    if isinstance(result, pd.DataFrame) and date_col in result.columns and value_col in result.columns:
        return True
    return False

def check_stationarity(data):
    result = adfuller(data)
    p_value = result[1]
    threshold = 0.05
    
    if p_value < threshold:
        return 0
    else:
        return 1

def best_arima_model(series, d):
    best_aic = np.inf
    best_order = None
    best_model = None
    for p in range(1, 5):
        for q in range(1, 5):
            try:
                model = ARIMA(series, order=(p, d, q))
                model_fit = model.fit()
                aic = model_fit.aic
                if aic < best_aic:
                    best_aic = aic
                    best_order = (p, d, q)
                    best_model = model_fit
            except Exception:
                continue
    return best_model

def seasonal_decomposition_plot(data, column, date_col, plot_path):
    try:
        data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
        data = data.dropna(subset=[date_col])
        data.set_index(date_col, inplace=True)
        data = data.fillna(0)
        
        result_df = data[[column]]
        
        decomposition = seasonal_decompose(result_df[column], model='additive', period=12)

        plt.figure(figsize=(12, 8))
        plt.subplot(411)
        plt.plot(result_df[column], label='Original')
        plt.legend(loc='upper left')
        plt.title('Seasonal Decomposition')

        plt.subplot(412)
        plt.plot(decomposition.trend, label='Trend')
        plt.legend(loc='upper left')

        plt.subplot(413)
        plt.plot(decomposition.seasonal, label='Seasonal')
        plt.legend(loc='upper left')

        plt.subplot(414)
        plt.plot(decomposition.resid, label='Residual')
        plt.legend(loc='upper left')

        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        return decomposition
    
    except Exception as e:
        print(f"Error in seasonal decomposition: {e}")
        return None

def forecast_data(data, column, date_col, forecast_months=6, plot_path=None):
    try:
        data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
        data = data.dropna(subset=[date_col])
        data.set_index(date_col, inplace=True)
        data = data.fillna(0)
        data = data.resample('M').sum()

        results_df = data[[column]]

        d = check_stationarity(results_df[column])
        model_fit = best_arima_model(results_df[column], d)

        forecast = model_fit.forecast(steps=forecast_months)
        
        forecast_index = pd.date_range(start=results_df.index[-1], periods=forecast_months + 1, freq='M')[1:]
        forecast_df = pd.DataFrame({column: forecast}, index=forecast_index)

        plt.figure(figsize=(10, 6))
        plt.plot(results_df.index, results_df[column], label='Historical Data')
        plt.plot(forecast_df.index, forecast_df[column], label='Forecast', linestyle='--')
        plt.title(f'{column} Forecast')
        plt.xlabel('Date')
        plt.ylabel(column)
        plt.legend()
        if plot_path:
            plt.savefig(plot_path)
            plt.close()
        
        return forecast_df

    except Exception as e:
        print(f"Error in forecasting data: {e}")
        return None