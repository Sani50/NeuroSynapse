from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import dash

# File paths for the different prediction types
alzheimers_file_path = r"C:\Users\sanvi\OneDrive\Desktop\neurosynapseFrontBack\alz_updated.xlsx"
seizure_file_path = r"C:\Users\sanvi\OneDrive\Desktop\neurosynapseFrontBack\extended_predictions.xlsx"
parkinsons_file_path = r"C:\Users\sanvi\OneDrive\Desktop\neurosynapseFrontBack\alz_updated.xlsx"

# Load data for each prediction type
try:
    alz_data = pd.read_excel(alzheimers_file_path)
    seizure_data = pd.read_excel(seizure_file_path)
    parkinsons_data = pd.read_excel(parkinsons_file_path)
except Exception as e:
    print(f"Error loading files: {e}")
    exit()

# Ensure required columns are present for each prediction type
required_columns = ["Time", "Prediction Probability", "Risk Level"]

def check_required_columns(data, prediction_type):
    if not all(col in data.columns for col in required_columns):
        print(f"Missing required columns in {prediction_type} data. Ensure your file contains: {required_columns}")
        exit()

check_required_columns(alz_data, "Alzheimer's")
check_required_columns(seizure_data, "Seizures")
check_required_columns(parkinsons_data, "Parkinson's")

# Define the risk threshold for low/high risk (for example, 0.5)
RISK_THRESHOLD = 0.5

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Real-Time Prediction Display"

# Layout
app.layout = html.Div([    
    html.H1("Real-Time Predictions", style={'text-align': 'center'}),

    # Alzheimer's graph and risk
    html.Div([
        dcc.Graph(id="alzheimers-graph"),
        html.Div(id="latest-alzheimers-prediction", style={'text-align': 'center', 'font-size': '1.5rem', 'margin-top': '20px'})
    ]),

    # Seizure graph and risk
    html.Div([
        dcc.Graph(id="seizure-graph"),
        html.Div(id="latest-seizure-prediction", style={'text-align': 'center', 'font-size': '1.5rem', 'margin-top': '20px'})
    ]),

    # Parkinson's graph and risk
    html.Div([
        dcc.Graph(id="parkinsons-graph"),
        html.Div(id="latest-parkinsons-prediction", style={'text-align': 'center', 'font-size': '1.5rem', 'margin-top': '20px'})
    ]),

    # Interval for updates
    dcc.Interval(id="update-interval", interval=2000, n_intervals=0),  # Update every 2 seconds
])


@app.callback(
    [Output("alzheimers-graph", "figure"),
     Output("seizure-graph", "figure"),
     Output("parkinsons-graph", "figure"),
     Output("latest-alzheimers-prediction", "children"),
     Output("latest-seizure-prediction", "children"),
     Output("latest-parkinsons-prediction", "children")],
    [Input("update-interval", "n_intervals")]
)
def update_predictions(n_intervals):
    # Debugging print to track callback triggering
    print(f"Callback triggered for interval: {n_intervals}")
    
    buffer_size = 20  # Number of rows to display at once
    start_index = n_intervals * buffer_size
    end_index = start_index + buffer_size

    # Alzheimer's graph
    alz_rows_to_show = alz_data.iloc[start_index:end_index]
    alz_figure = go.Figure()
    if not alz_rows_to_show.empty:
        alz_figure.add_trace(go.Scatter(
            x=alz_rows_to_show["Time"],
            y=alz_rows_to_show["Prediction Probability"],
            mode="lines+markers",
            name="Alzheimer's Prediction Probability",
            line=dict(color='blue')
        ))
        alz_figure.update_layout(
            title="Real-Time Prediction Probabilities of Alzheimer's",
            xaxis_title="Time",
            yaxis_title="Prediction Probability",
            yaxis_range=[0, 1]
        )

    # Seizure graph
    seizure_rows_to_show = seizure_data.iloc[start_index:end_index]
    seizure_figure = go.Figure()
    if not seizure_rows_to_show.empty:
        seizure_figure.add_trace(go.Scatter(
            x=seizure_rows_to_show["Time"],
            y=seizure_rows_to_show["Prediction Probability"],
            mode="lines+markers",
            name="Seizure Prediction Probability",
            line=dict(color='green')
        ))
        seizure_figure.update_layout(
            title="Real-Time Prediction Probabilities of Seizures",
            xaxis_title="Time",
            yaxis_title="Prediction Probability",
            yaxis_range=[0, 1]
        )

    # Parkinson's graph
    parkinsons_rows_to_show = parkinsons_data.iloc[start_index:end_index]
    parkinsons_figure = go.Figure()
    if not parkinsons_rows_to_show.empty:
        parkinsons_figure.add_trace(go.Scatter(
            x=parkinsons_rows_to_show["Time"],
            y=parkinsons_rows_to_show["Prediction Probability"],
            mode="lines+markers",
            name="Parkinson's Prediction Probability",
            line=dict(color='red')
        ))
        parkinsons_figure.update_layout(
            title="Real-Time Prediction Probabilities of Parkinson's",
            xaxis_title="Time",
            yaxis_title="Prediction Probability",
            yaxis_range=[0, 1]
        )

    # Get latest predictions
    def get_risk_level_label(prediction_prob):
        if prediction_prob >= RISK_THRESHOLD:
            return html.Span("HIGH", style={'color': 'red', 'fontWeight': 'bold'})
        else:
            return html.Span("LOW", style={'color': 'green', 'fontWeight': 'bold'})

    latest_alz_prediction = "No data available" if alz_rows_to_show.empty else f"Latest Alzheimer's Risk Level: {get_risk_level_label(alz_rows_to_show.iloc[-1]['Prediction Probability'])}"
    latest_seizure_prediction = "No data available" if seizure_rows_to_show.empty else f"Latest Seizure Risk Level: {get_risk_level_label(seizure_rows_to_show.iloc[-1]['Prediction Probability'])}"
    latest_parkinsons_prediction = "No data available" if parkinsons_rows_to_show.empty else f"Latest Parkinson's Risk Level: {get_risk_level_label(parkinsons_rows_to_show.iloc[-1]['Prediction Probability'])}"

    # Correct the format to display risk levels as proper Dash components
    latest_alz_prediction = get_risk_level_label(alz_rows_to_show.iloc[-1]['Prediction Probability']) if not alz_rows_to_show.empty else "No data available"
    latest_seizure_prediction = get_risk_level_label(seizure_rows_to_show.iloc[-1]['Prediction Probability']) if not seizure_rows_to_show.empty else "No data available"
    latest_parkinsons_prediction = get_risk_level_label(parkinsons_rows_to_show.iloc[-1]['Prediction Probability']) if not parkinsons_rows_to_show.empty else "No data available"

    return alz_figure, seizure_figure, parkinsons_figure, latest_alz_prediction, latest_seizure_prediction, latest_parkinsons_prediction


# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
