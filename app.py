import dash
from dash import dcc, html
import plotly.graph_objs as go
import yfinance as yf
import openai
from dash.dependencies import Input, Output
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave API de OpenAI desde el archivo .env
openai.api_key = os.getenv('API_KEY_OPENAI')  # Utilizando la clave desde .env

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Función para obtener los datos en vivo
def get_data(ticker='BTC-USD'):
    data = yf.download(ticker, period='1d', interval='1m')  # Intervalo de 1 minuto
    return data

# Layout de la aplicación Dash
app.layout = html.Div([
    html.H1('Gráfico Financiero en Vivo'),
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='graph-update',
        interval=60*1000,  # Actualizar cada 1 minuto
        n_intervals=0
    ),
    html.Div(id='analysis-output')
])

# Actualizar el gráfico en tiempo real
@app.callback(
    [Output('live-graph', 'figure'),
     Output('analysis-output', 'children')],
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n):
    # Obtener los datos más recientes
    data = get_data()

    # Crear gráfico de velas
    figure = {
        'data': [
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Activo Financiero'
            )
        ],
        'layout': go.Layout(
            title='Gráfico Financiero',
            xaxis={'rangeslider': {'visible': False}},
            yaxis={'title': 'Precio (USD)'},
            xaxis_rangeslider_visible=False
        )
    }
    
    # Crear un prompt para analizar los datos de los últimos minutos
    prompt = f"""
    Analiza los siguientes datos históricos de un activo financiero y haz una predicción sobre su comportamiento para los próximos minutos:

    Fecha, Apertura, Máximo, Mínimo, Cierre
    {data[['Open', 'High', 'Low', 'Close']].tail(5).to_string(index=False)}
    """
    
    # Solicitar análisis a OpenAI con el nuevo método
    response = openai.Completion.create(
        model="gpt-3.5-turbo",  # Usar el modelo más adecuado
        prompt=prompt,
        max_tokens=150
    )

    analysis = response['choices'][0]['text'].strip()

    return figure, analysis

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
