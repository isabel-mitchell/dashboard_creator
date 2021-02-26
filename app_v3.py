import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import ClientsideFunction, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import pickle
import numpy as np
import os

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

#fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

data_dict = {filename: pd.read_csv(f'data/{filename}') for filename in os.listdir('data')}

def createH1(element):
    return html.H1(
        id=element['id'], 
        className='draggable', 
        style={
            'border': '1px black solid',
            'position': 'absolute',
            'top': element['top'],
            'left': element['left'],
            'height': element['height'],
            'width': element['width']
        }, 
        children=element['text']
    )

def createP(element):
    return html.P(
        id=element['id'], 
        className='draggable', 
        style={
            'border': '1px black solid',
            'position': 'absolute',
            'top': element['top'],
            'left': element['left'],
            'height': element['height'],
            'width': element['width']
        }, 
        children=element['text']
    )

def createGraph(element):
    fig = go.Figure(
        data=[
            go.Bar(
                x=data_dict[element['data']['df']][element['data']['x']],
                y=data_dict[element['data']['df']][element['data']['y']],
                marker_color=element['data']['marker_color']
            )
        ]
    )

    return html.Div(
        id=element['id'], 
        className='draggable graph', 
        style={
            'border': '1px black solid',
            'position': 'absolute',
            'top': element['top'],
            'left': element['left'],
            'height': element['height'],
            'width': element['width']
        }, 
        children=dcc.Graph(figure=fig, style={'height': '100%', 'width': '100%'})
    )

element_key = {
    'h1': createH1,
    'p': createP,
    'div': createGraph
}

def createElement(element):
    createFunction = element_key[element['type']]
    return createFunction(element)

def createBody(saved_layout):
    body = [createElement(element) for element in saved_layout]
    return body

def createDataStore(saved_layout):
    dataStore = {element['id']: element['data'] for element in saved_layout if element['graph']}
    return dataStore


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP, "https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css"]
external_scripts = ["https://code.jquery.com/jquery-1.12.4.js", "https://code.jquery.com/ui/1.12.1/jquery-ui.js"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts = external_scripts, suppress_callback_exceptions=True)

app.layout = html.Div(
    children=[
        dcc.Store(id='memory', data="No data"),
        dcc.Store(id='data-store', data="No data"),
        html.Button('Save layout', id='save-but', style={'position': 'absolute', 'bottom':50,'right':110}),
        html.Div(id='body', style={'height':'100vh', 'width': '100vw'}, children=[])
    ]
)

###############################################################################################################
#                                                  CALLBACKS                                                  #
###############################################################################################################

###############################################################################################################
############################################### Helper functions ##############################################
###############################################################################################################

def get_input_trigger_id(ctx):
    if not ctx.triggered:
        input_trigger = 'X'
    else:
        input_trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    return input_trigger


@app.callback(
    [Output('body', 'children'), Output('data-store', 'data')],
    [Input('memory', 'data')],
    [State('body', 'children')]
)
def update_body(stored_data, body):

    input_trigger = get_input_trigger_id(dash.callback_context)
    print(input_trigger)

    if input_trigger == 'X':
        return dash.no_update, dash.no_update
        
    elif input_trigger == 'memory' and stored_data == "":
        ### 1) Populating body with most recent saved layout
        ### 2) Populating data store with any data for plots 

        print('updating layout with stored data')
        with open('layouts/saved_layout.txt', 'r') as f:
            stored_layout = json.load(f)
        f.close()

        return createBody(stored_layout['layout']), createDataStore(stored_layout['layout'])

    elif input_trigger == 'memory' and stored_data != "":
        ### Saving current layout 
        with open('layouts/saved_layout.txt', 'w') as f:
            json.dump({'layout': stored_data}, f)
        f.close()

        return dash.no_update, dash.no_update

        


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='saveLayoutTest'
    ),
    Output('memory', 'data'),
    Input('save-but', 'n_clicks'),
    State('body', 'children'),
    State('data-store', 'data')
)

###############################################################################################################
############################################### Update Body ###################################################
###############################################################################################################



if __name__ == '__main__':
    app.run_server(debug=True)