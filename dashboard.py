import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
from datetime import datetime
import pytz
from collections import defaultdict

# Constants for IP and port
IP_ADDRESS = "xx.xxx.xxx.xx"
PORT_STH = 8666
DASH_HOST = "0.0.0.0"  # Allow access from any IP

# Function to get data from the API
def get_data(attribute, lastN):
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/Lamp/id/urn:ngsi-ld:Lamp:001/attributes/{attribute}?lastN={lastN}"
    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
            return values
        except (KeyError, IndexError) as e:
            print(f"Error accessing data for {attribute}: {e}")
            return []
    else:
        print(f"Error accessing {url}: {response.status_code}")
        return []

# Function to convert UTC timestamps to Lisbon time
def convert_to_lisbon_time(timestamps):
    utc = pytz.utc
    lisbon = pytz.timezone('Europe/Lisbon')
    converted_timestamps = []
    for timestamp in timestamps:
        try:
            timestamp = timestamp.replace('T', ' ').replace('Z', '')
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')).astimezone(lisbon)
        except ValueError:
            # Handle case where milliseconds are not present
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).astimezone(lisbon)
        converted_timestamps.append(converted_time)
    return converted_timestamps

# Set lastN value
lastN = 30  # Get 30 most recent points at each interval

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Luminosity, Temperature and Humidity Data Viewer'),
    dcc.Graph(id='luminosity-graph'),
    dcc.Graph(id='temperature-graph'),
    dcc.Graph(id='humidity-graph'),
    # Store to hold historical data
    dcc.Store(id='data-store', data={'timestamps': [], 'luminosity_values': [], 'temperature_values': [], 'humidity_values': []}),
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds (10 seconds)
        n_intervals=0
    )
])

@app.callback(
    Output('data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('data-store', 'data')
)
def update_data_store(n, stored_data):
    # Get luminosity, temperature, and humidity data
    luminosity_data = get_data('luminosity', lastN)
    temperature_data = get_data('temperature', lastN)
    humidity_data = get_data('humidity', lastN)

    if luminosity_data or temperature_data or humidity_data:
        # Store values in a temporary dictionary to avoid index errors
        timestamps_dict = defaultdict(lambda: {'luminosity': [], 'temperature': [], 'humidity': []})

        # Process luminosity data
        for entry in luminosity_data:
            timestamp = entry['recvTime']
            timestamps_dict[timestamp]['luminosity'].append(float(entry['attrValue']))

        # Process temperature data
        for entry in temperature_data:
            timestamp = entry['recvTime']
            timestamps_dict[timestamp]['temperature'].append(float(entry['attrValue']))

        # Process humidity data
        for entry in humidity_data:
            timestamp = entry['recvTime']
            timestamps_dict[timestamp]['humidity'].append(float(entry['attrValue']))

        # Update stored data with aggregated values
        stored_data['timestamps'] = list(timestamps_dict.keys())
        stored_data['luminosity_values'] = [sum(values['luminosity']) / len(values['luminosity']) if values['luminosity'] else None for values in timestamps_dict.values()]
        stored_data['temperature_values'] = [sum(values['temperature']) / len(values['temperature']) if values['temperature'] else None for values in timestamps_dict.values()]
        stored_data['humidity_values'] = [sum(values['humidity']) / len(values['humidity']) if values['humidity'] else None for values in timestamps_dict.values()]

        return stored_data

    return stored_data

@app.callback(
    Output('luminosity-graph', 'figure'),
    Output('temperature-graph', 'figure'),
    Output('humidity-graph', 'figure'),
    Input('data-store', 'data')
)
def update_graphs(stored_data):
    figures = []
    for data_type in ['luminosity_values', 'temperature_values', 'humidity_values']:
        if stored_data['timestamps'] and stored_data[data_type]:
            # Create traces for the plot
            trace = go.Scatter(
                x=stored_data['timestamps'],
                y=stored_data[data_type],
                mode='lines+markers',
                name=data_type.capitalize(),
                line=dict(color='orange' if data_type == 'luminosity_values' else 'blue' if data_type == 'temperature_values' else 'green')
            )

            # Create figure
            fig = go.Figure(data=[trace])

            # Update layout
            fig.update_layout(
                title=f'{data_type.capitalize().replace("_values", "")} Over Time',
                xaxis_title='Timestamp',
                yaxis_title=data_type.capitalize().replace("_values", ""),
                hovermode='closest'
            )
            figures.append(fig)
        else:
            figures.append(go.Figure())  # Empty figure if no data

    return figures[0], figures[1], figures[2]

if __name__ == '__main__':
    app.run_server(debug=True, host=DASH_HOST, port=8051)
