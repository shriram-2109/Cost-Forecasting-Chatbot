from flask import Flask, render_template, request, session
import pandas as pd
import matplotlib.pyplot as plt
import os
import traceback
from dotenv import load_dotenv
from your_module import *  
from datetime import datetime

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Ensure the 'static' directory exists for storing plots
if not os.path.exists('static'):
    os.makedirs('static')

def generate_unique_filename(prefix):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{timestamp}.png'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        if file:
            try:
                df = pd.read_csv(file)
                session['dataframe'] = df.to_dict()
                session['columns'] = df.columns.tolist() 
                return render_template('chatbot.html', success='File uploaded successfully. You can now interact with the chatbot.', columns=session['columns'])
            except Exception as e:
                return render_template('index.html', error=str(e))
    
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        query = request.form['query']
        df = pd.DataFrame(session.get('dataframe'))  

        if df.empty:
            return render_template('chatbot.html', result='No data available. Please upload a CSV file first.', columns=[])

        columns_list = ', '.join(df.columns)
        code = query_to_code_llm(query, columns_list)

        if 'Error' in code:
            return render_template('chatbot.html', result=f"Error Generating Code:\n{code}", columns=df.columns.tolist())

        result = execute_code(code, df)
        if result is None:
            return render_template('chatbot.html', result="Execution of the generated code failed.", columns=df.columns.tolist())

        date_col = request.form.get('date_col')
        value_col = request.form.get('value_col')

        if check_if_dataframe_with_date(result, date_col, value_col):
            option = request.form.get('option')

            if option == '1':
                try:
                    plot_filename = generate_unique_filename('seasonal_decomposition_plot')
                    plot_path = os.path.join('static', plot_filename)
                    seasonal_decomposition_plot(result, value_col, date_col, plot_path)
                    plot_url = f'/static/{plot_filename}'
                    return render_template('chatbot.html',
                                           result='Seasonal decomposition plot displayed.',
                                           plot_url=plot_url,
                                           columns=df.columns.tolist())
                except Exception as e:
                    return render_template('chatbot.html', result=f"Error performing seasonal decomposition: {e}", columns=df.columns.tolist())

            elif option == '2':
                forecast_months = int(request.form.get('forecast_months', 6))

                try:
                    plot_filename = generate_unique_filename('forecast_plot')
                    plot_path = os.path.join('static', plot_filename)
                    forecast = forecast_data(result, value_col, date_col, forecast_months, plot_path)
                    plot_url = f'/static/{plot_filename}'

                    forecast_html = forecast.to_html(classes='table table-striped', index=False)

                    return render_template('chatbot.html',
                                           result=f'Forecasting plot displayed.',
                                           plot_url=plot_url,
                                           forecast_html=forecast_html,
                                           columns=df.columns.tolist())
                except Exception as e:
                    return render_template('chatbot.html', result=f"Error forecasting data: {e}", columns=df.columns.tolist())

            else:
                if isinstance(result, pd.DataFrame):
                    result_html = result.to_html(classes='table table-striped', index=False)
                    return render_template('chatbot.html', result=f"Query result:<br>{result_html}", columns=df.columns.tolist())
                else:
                    return render_template('chatbot.html', result=f"Query result:\n{result}", columns=df.columns.tolist())
        else:
            if isinstance(result, pd.DataFrame):
                result_html = result.to_html(classes='table table-striped', index=False)
                return render_template('chatbot.html', result=f"Query result:<br>{result_html}", columns=df.columns.tolist())
            else:
                return render_template('chatbot.html', result=f"Query result:\n{result}", columns=df.columns.tolist())

    except Exception as e:
        traceback.print_exc()
        return render_template('chatbot.html', result=f"Error executing code: {e}", columns=df.columns.tolist())

if __name__ == '__main__':
    app.run(debug=True)
