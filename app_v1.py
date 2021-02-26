import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(id='body', children=[
    html.H1(id='heading', children='Hello Dash'),

    html.Div(id='heading2', children='''
        Dash: A web application framework for Python.
    '''),

    dbc.Button('Add Element', id='add-button', n_clicks=0, className='m-2'),
    dbc.Button("Extra large modal", id="open-xl", className='m-2'),
    dbc.Modal(
            [
                dbc.ModalHeader("Header"),
                dbc.ModalBody("An extra large modal."),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-xl", className="ml-auto")
                ),
            ],
            id="modal-xl",
            size="xl",
        ),

])


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

###############################################################################################################
############################################### Update Body ###################################################
###############################################################################################################

@app.callback(
    Output('body', 'children'),
    [
        Input('add-button', 'n_clicks'), 
        Input({'index': ALL, 'action': 'delete', 'type': ALL}, 'n_clicks'),
        Input({'index': ALL, 'action': 'edit', 'type': ALL}, 'n_clicks'),
    ],
    [State('body', 'children')]
)
def update_body(add_but_clicks, delete_but_clicks, edit_but_clicks, current_body):

    input_trigger = get_input_trigger_id(dash.callback_context)

    if input_trigger == 'X':
        raise PreventUpdate

    elif input_trigger == 'add-button':

        figure_id = f'figure_{add_but_clicks}'
        new_figure = dcc.Graph(id={'index':figure_id, 'type':'figure'}, figure=fig)
        delete_button = html.Button(f'Delete {figure_id}', id={'index':figure_id, 'action':'delete', 'type':'figure'}, n_clicks=0)
        edit_button = html.Button(f'Edit {figure_id}', id={'index':figure_id, 'action':'edit', 'type':'figure'}, n_clicks=0)

        return current_body + [edit_button, delete_button, new_figure]

    else:

        input_trigger = json.loads(input_trigger)
        trigger_id, trigger_action, trigger_type = input_trigger['index'], input_trigger['action'], input_trigger['type']
    
        if trigger_action == 'delete':
            del_tuple = (
                {'index': trigger_id, 'type': trigger_type}, 
                {'index':trigger_id, 'action':'delete', 'type': trigger_type},
                {'index':trigger_id, 'action':'edit', 'type': trigger_type},
            )
            new_body = [element for element in current_body if element['props']['id'] not in del_tuple]
            return new_body

        elif trigger_action == 'edit':
            print('open edit modal')
            raise PreventUpdate

        else:
            raise PreventUpdate

@app.callback(
    Output("modal-xl", "is_open"),
    [Input("open-xl", "n_clicks"), Input("close-xl", "n_clicks")],
    [State("modal-xl", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)