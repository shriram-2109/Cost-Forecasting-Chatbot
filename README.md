# Cost Forecasting Chatbot

This chatbot is capable of predicting costs based on input data and performing time series analysis using ARIMA model. GPT-4 model is used to convert query (in English) to executable code (in Python) to analyze user data. 


## Installation

#### 1. Clone the repository:
   - ```bash
     git clone https://github.com/shriram-2109/Cost-Forecasting-Chatbot.git
     ```
#### 2. Install necessary packages:
   - ```bash
     pip install -r requirements.txt
     ```
#### 3. Set OpenAI API Key as an environment variable using secret .env file.
   - ```.env
      OPENAI_API_KEY = "your-api-key"`
     ```
#### 4. Usage:
  - ```bash
    python app.py
    ```
#### 5. Output: 
##### Main Page
![out1](https://github.com/shriram-2109/Cost-Forecasting-Chatbot/blob/main/images/Main%20Page.png)
##### Seasonal Decomposition Query
![out2](https://github.com/shriram-2109/Cost-Forecasting-Chatbot/blob/main/images/Seasonal%20Decomposition.png)
##### Seasonal Decomposition Plot
![out3](https://github.com/shriram-2109/Cost-Forecasting-Chatbot/blob/main/images/Seasonal%20Decomposition%20Plot.png)
##### Forecasting Query
![out3](https://github.com/shriram-2109/Cost-Forecasting-Chatbot/blob/main/images/Forecasting.png)
##### Forecasting Plot
![out3](https://github.com/shriram-2109/Cost-Forecasting-Chatbot/blob/main/images/Forecasting%20Plot.png)


## License

This project is licensed under the MIT License - see the LICENSE file for details.
