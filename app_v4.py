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
from layout_functions_v1 import createH1, createP, createGraph, createElement, createBody, createDataStore
from modal_functions_v1 import populate_header, populate_footer, make_accordion_item, populate_body

###############################################################################################################
#                                                GLOBAL VARIABLES                                             #
###############################################################################################################

data_dict = {filename: pd.read_csv(f'data/{filename}') for filename in os.listdir('data')}

element_key = {
    'h1': createH1,
    'p': createP,
    'div': createGraph
}

###############################################################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP, "https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css"]
external_scripts = ["https://code.jquery.com/jquery-1.12.4.js", "https://code.jquery.com/ui/1.12.1/jquery-ui.js"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts = external_scripts)#, suppress_callback_exceptions=True)

app.layout = html.Div(
    children=[
        dcc.Store(id='memory', data="No data"),
        dcc.Store(id='data-store', data="No data"),
        dbc.DropdownMenu(
            id='new-element-menu',
            label='Create a new element',
            style={'position': 'fixed', 'zIndex': 99},
            className='m-3',
            children=[
                dbc.DropdownMenuItem('Title', id={'type': 'title', 'action':'create'}),
                dbc.DropdownMenuItem('Text', id={'type': 'text', 'action':'create'}),
                dbc.DropdownMenuItem('Bar chart', id={'type': 'bar-chart', 'action':'create'}),
                dbc.DropdownMenuItem('Pie chart', id={'type': 'pie-chart', 'action':'create'})
            ]
        ),
        dbc.Modal(
            [   
                dcc.Input(id='modal-ready', value="False", type='hidden'),
                dbc.ModalHeader(id='modal-header'),
                dbc.ModalBody(id='modal-body'),
                dbc.ModalFooter(id='modal-footer',
                    children=[
                        html.Div(
                            [
                                dbc.Button("Add Element", id="add-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Edit Element", id="edit-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Close", id="close-modal", className='mx-2')
                            ]
                        )
                    ]
                ),
            ],
            id="modal-xl",
            size="xl"
        ),
        dbc.Button('Save layout', id='save-but', style={'position': 'fixed', 'bottom':50,'right':110, 'zIndex': 99}),
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
    [
        Input('memory', 'data'),
        Input('add-button', 'n_clicks')
    ],
    [
        State({'id':ALL, 'plot': ALL, 'type':'modal'}, 'figure'),
        State('body', 'children'),
        State('data-store', 'data'),
        State({'type': 'input', 'plot': ALL, 'input_id': ALL, 'panel':'data'}, 'value'),
        State({'type': 'input-col', 'plot': ALL, 'input_id': ALL, 'panel':'data'}, 'value'),
    ]
)
def update_body(
    stored_data, add_button_n_clicks, modal_plot, body, 
    current_stored_data, dataframe_selection, data_inputs
):

    input_trigger = get_input_trigger_id(dash.callback_context)

    if input_trigger == 'X':
        return dash.no_update, dash.no_update
        
    elif input_trigger == 'memory' and stored_data == "":
        ### Updating layout with saved layout
        with open('layouts/saved_layout.txt', 'r') as f:
            stored_layout = json.load(f)
        f.close()

        body = createBody(stored_layout['layout'], element_key, data_dict)
        data_store = createDataStore(stored_layout['layout'])

        return body, data_store

    elif input_trigger == 'memory' and stored_data != "":
        ### Saving current layout 
        with open('layouts/saved_layout.txt', 'w') as f:
            json.dump({'layout': stored_data}, f)
        f.close()

        return dash.no_update, dash.no_update

    elif input_trigger == 'add-button' and add_button_n_clicks > 0:
        body.append(html.Div(
            id=f'test-graph{len(current_stored_data) + 1}',
            className='draggable graph', 
            children=dcc.Graph(figure=modal_plot[0], style={'height': '100%', 'width': '100%'})
            )
        )

        current_stored_data[f'test-graph{len(current_stored_data) + 1}'] = {
            'df': dataframe_selection[0],
            'x': data_inputs[0],
            'y': data_inputs[1],
            'marker_color': 'purple'
        }

        return body, current_stored_data

    else:
        return dash.no_update, dash.no_update



@app.callback(
    Output("modal-xl", "is_open"),
    [
        Input("modal-ready", 'value'), 
        Input("close-modal", "n_clicks")
    ]
)
def toggle_modal(modal_ready, close_modal_n_clicks):
    input_trigger = get_input_trigger_id(dash.callback_context)
    if input_trigger == 'close-modal':
        return False

    elif input_trigger == 'modal-ready' and modal_ready == "True":
        return True
    
    else:
        return False

@app.callback(
    [
        Output('modal-xl', 'children'),
        Output("modal-ready", 'value')
    ],
    [
        Input({'action': 'create', 'type': ALL}, 'n_clicks'),
        Input('add-button', 'n_clicks')
    ],
    [State('modal-xl', 'children')]
)
def update_modal(create_element_n_clicks, add_button_n_clicks, current_modal):
    input_trigger = get_input_trigger_id(dash.callback_context)
    if input_trigger == 'X':
        return dash.no_update, dash.no_update

    elif input_trigger == 'add-button':
        return dash.no_update, "False"

    else:
        input_trigger = json.loads(input_trigger)
        trigger_action, trigger_type = input_trigger['action'], input_trigger['type']

        modal_input = current_modal[0]
        modal_header = current_modal[1]
        modal_body = current_modal[2]
        modal_footer = current_modal[3]

        if trigger_action == 'create':
            modal_header['props']['children'] = populate_header(trigger_action, trigger_type)
            modal_body['props']['children'] = populate_body(trigger_action=trigger_action, trigger_type=trigger_type, data_dict=data_dict)
            modal_footer['props']['children'] = populate_footer(trigger_action)
            
            return [modal_input, modal_header, modal_body, modal_footer], "True"

        elif trigger_action == 'edit':
            return [modal_input, modal_header, modal_body, modal_footer], "True"

        else:
            return dash.no_update, dash.no_update

@app.callback(
    Output({'action':'collapse-card', 'key': MATCH}, 'is_open'),
    [Input({'action':'collapse-but', 'key':MATCH}, 'n_clicks')],
    [State({'action':'collapse-card', 'key': MATCH}, 'is_open')]
)
def toggle_accordion(collapse_but_clicks, collapse_orig):
    input_trigger = get_input_trigger_id(dash.callback_context)
    if input_trigger == 'X':
        return dash.no_update
    else:
        return ~collapse_orig

@app.callback(
    [
        Output({'type':'input-col', 'plot': MATCH, 'input_id':ALL, 'panel':'data'}, 'options'),
        Output({'type':'input-col', 'plot': MATCH, 'input_id':ALL, 'panel':'data'}, 'value'),
    ],
    [Input({'type':'input', 'plot': MATCH, 'input_id':'data-dd', 'panel':'data'}, 'value')]
)
def update_column_selectors(dataframe_selection):
    input_trigger = get_input_trigger_id(dash.callback_context)
    if input_trigger == 'X':
        return dash.no_update
    else:
        df = data_dict[dataframe_selection]
        column_selection = [{'label':col, 'value':col} for col in df.columns]
        return [column_selection, column_selection], [None, None]

@app.callback(
    Output({'id':ALL, 'plot': ALL, 'type':'modal'}, 'figure'),
    [
        Input({'type': 'input-col', 'plot': ALL, 'input_id': ALL, 'panel':'data'}, 'value'),
        Input({'type': 'input-col', 'plot': ALL, 'input_id': ALL, 'panel':'text'}, 'value'),
    ],
    [
        State({'id':ALL, 'plot': ALL, 'type':'modal'}, 'figure'),
        State({'type':'input', 'plot': ALL, 'input_id':'data-dd', 'panel':ALL}, 'value')

    ]
)
def update_plot(data_inputs, text_inputs, modal_plot, dataframe_selection):
    input_trigger = get_input_trigger_id(dash.callback_context)
    if input_trigger == 'X':
        return dash.no_update

    else:
        input_trigger = json.loads(input_trigger)
        trigger_panel, trigger_id = input_trigger['panel'], input_trigger['input_id']

        if trigger_panel == 'data' and None not in data_inputs:
            df = data_dict[dataframe_selection[0]]
            modal_plot[0]['data'] = [go.Bar(x=df[data_inputs[0]], y=df[data_inputs[1]])]
            return modal_plot

        elif trigger_panel == 'text':
            if trigger_id == 'title':
                modal_plot[0]['layout']['title'] = text_inputs[0]

            elif trigger_id == 'x-title':
                modal_plot[0]['layout']['xaxis']['title'] = {'text': text_inputs[1]}
            
            elif trigger_id == 'y-title':
                modal_plot[0]['layout']['yaxis']['title'] = {'text': text_inputs[2]}

            return modal_plot

        else: 
            return dash.no_update

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