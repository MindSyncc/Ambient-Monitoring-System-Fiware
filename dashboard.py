# Import necessary libraries and modules for Dash and Plotly
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
from datetime import datetime
import pytz
from collections import defaultdict

# Constants for IP and port used for accessing the STH-Comet service
IP_ADDRESS = "xx.xxx.xxx.xx"
PORT_STH = 8666
DASH_HOST = "0.0.0.0"  # Allows access from any IP

# Function to retrieve data from the API for a specific attribute and limit the number of records
def get_data(attribute, lastN):
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/Lamp/id/urn:ngsi-ld:Lamp:001/attributes/{attribute}?lastN={lastN}"
    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }
    # Send the GET request to the STH-Comet API
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        try:
            # Return the values from the API response
            values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
            return values
        except (KeyError, IndexError) as e:
            # Handle errors in case the expected data structure is not found
            print(f"Error accessing data for {attribute}: {e}")
            return []
    else:
        # Print error message if the request fails
        print(f"Error accessing {url}: {response.status_code}")
        return []

# Function to convert UTC timestamps to Lisbon time zone
def convert_to_lisbon_time(timestamps):
    utc = pytz.utc  # UTC timezone
    lisbon = pytz.timezone('Europe/Lisbon')  # Lisbon timezone
    converted_timestamps = []
    for timestamp in timestamps:
        try:
            # Convert timestamp format and adjust timezone
            timestamp = timestamp.replace('T', ' ').replace('Z', '')
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')).astimezone(lisbon)
        except ValueError:
            # Handle case where milliseconds are not present in the timestamp
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).astimezone(lisbon)
        converted_timestamps.append(converted_time)
    return converted_timestamps

# Define the number of most recent points to retrieve (lastN)
lastN = 30  # Get 30 most recent points

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1('Luminosity, Temperature and Humidity Data Viewer'),
    dcc.Graph(id='luminosity-graph'),  # Graph for luminosity data
    dcc.Graph(id='temperature-graph'),  # Graph for temperature data
    dcc.Graph(id='humidity-graph'),  # Graph for humidity data
    # Store to hold historical data across all updates
    dcc.Store(id='data-store', data={'timestamps': [], 'luminosity_values': [], 'temperature_values': [], 'humidity_values': []}),
    # Interval component to trigger data update every 10 seconds
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds (10 seconds)
        n_intervals=0
    )
])

# Callback function to update the data store at each interval
@app.callback(
    Output('data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('data-store', 'data')
)
def update_data_store(n, stored_data):
    # Fetch data for luminosity, temperature, and humidity
    luminosity_data = get_data('luminosity', lastN)
    temperature_data = get_data('temperature', lastN)
    humidity_data = get_data('humidity', lastN)

    if luminosity_data or temperature_data or humidity_data:
        # Dictionary to aggregate data based on timestamps
        timestamps_dict = defaultdict(lambda: {'luminosity': [], 'temperature': [], 'humidity': []})

        # Process and store luminosity data
        for entry in luminosity_data:
            timestamp = entry['recvTime']
            timestamps_dict[timestamp]['luminosity'].append(float(entry['attrValue']))

        # Process and store temperature data
        for entry in temperature_data:
            timestamp = entry['recvTime']
            timestamps_dict[timestamp]['temperature'].append(float(entry['attrValue']))

        # Process and store humidity data
        for entry in humidity_data:
            timestamp = entry['recvTime']
            timestamps_dict[timestamp]['humidity'].append(float(entry['attrValue']))

        # Update the stored data with averaged values for each timestamp
        stored_data['timestamps'] = list(timestamps_dict.keys())
        stored_data['luminosity_values'] = [sum(values['luminosity']) / len(values['luminosity']) if values['luminosity'] else None for values in timestamps_dict.values()]
        stored_data['temperature_values'] = [sum(values['temperature']) / len(values['temperature']) if values['temperature'] else None for values in timestamps_dict.values()]
        stored_data['humidity_values'] = [sum(values['humidity']) / len(values['humidity']) if values['humidity'] else None for values in timestamps_dict.values()]

        return stored_data

    return stored_data

# Callback function to update the graphs with the stored data
@app.callback(
    Output('luminosity-graph', 'figure'),
    Output('temperature-graph', 'figure'),
    Output('humidity-graph', 'figure'),
    Input('data-store', 'data')
)
def update_graphs(stored_data):
    figures = []
    # Iterate through the data types and generate figures for each graph
    for data_type in ['luminosity_values', 'temperature_values', 'humidity_values']:
        if stored_data['timestamps'] and stored_data[data_type]:
            # Create traces (data lines) for the graphs
            trace = go.Scatter(
                x=stored_data['timestamps'],  # X-axis is timestamps
                y=stored_data[data_type],  # Y-axis is the selected data type
                mode='lines+markers',  # Line and marker mode for better visualization
                name=data_type.capitalize(),
                line=dict(color='orange' if data_type == 'luminosity_values' else 'blue' if data_type == 'temperature_values' else 'green')
            )

            # Create figure layout
            fig = go.Figure(data=[trace])

            # Update layout details such as title and axis labels
            fig.update_layout(
                title=f'{data_type.capitalize().replace("_values", "")} Over Time',
                xaxis_title='Timestamp',
                yaxis_title=data_type.capitalize().replace("_values", ""),
                hovermode='closest'
            )
            figures.append(fig)
        else:
            figures.append(go.Figure())  # Empty figure if no data available

    return figures[0], figures[1], figures[2]

# Run the Dash server
if __name__ == '__main__':
    app.run_server(debug=True, host=DASH_HOST, port=8051)  # Host on port 8051
