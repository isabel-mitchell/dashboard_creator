import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

######################################################################################
############################### Global variables #####################################

animals=['giraffes', 'orangutans', 'monkeys', 'elephants', 'gorillas']
counts = [20, 14, 23, 12, 15]
df = pd.DataFrame(list(zip(animals, counts)), columns=['animals', 'counts'])

data_dict = {filename: pd.read_csv(f'data/{filename}') for filename in os.listdir('data')}
print(list(data_dict))

fig = go.Figure([go.Bar(x=df['animals'], y=df['counts'])])

figure_list = []

######################################################################################

app.layout = html.Div(id='body', children=[
    dbc.DropdownMenu(
        id='new-element-menu',
        label='Create a new element',
        className='m-2',
        children=[
            dbc.DropdownMenuItem('Title', id={'type': 'title', 'action':'create'}),
            dbc.DropdownMenuItem('Text', id={'type': 'text', 'action':'create'}),
            dbc.DropdownMenuItem('Bar chart', id={'type': 'bar-chart', 'action':'create'}),
            dbc.DropdownMenuItem('Pie chart', id={'type': 'pie-chart', 'action':'create'})
        ]
    ),
    dbc.Modal(
            [
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
        Input('edit-button', 'n_clicks'), 
        Input({'index': ALL, 'action': 'delete', 'type': ALL}, 'n_clicks')
    ],
    [State('body', 'children'), State("new-plot", "figure"), State("modal-xl", "is_open"), State('modal-header', 'children')]
)
def update_body(add_but_clicks, edit_but_clicks, delete_but_clicks, current_body, new_fig, is_open, modal_title):

    input_trigger = get_input_trigger_id(dash.callback_context)

    if input_trigger == 'X':
        raise PreventUpdate

    elif input_trigger == 'add-button' and add_but_clicks > 0:
        
        global figure_list

        figure_id = f'figure_{len(figure_list)}'
        figure_list.append(figure_id)

        new_figure = dcc.Graph(id={'index':figure_id, 'type':'figure'}, figure=new_fig)
        delete_button = html.Button(f'Delete {figure_id}', id={'index':figure_id, 'action':'delete', 'type':'figure'}, n_clicks=0)
        edit_button = html.Button(f'Edit {figure_id}', id={'index':figure_id, 'action':'edit', 'type':'figure'}, n_clicks=0)

        ### Closing modal ###
        modal = [element for element in current_body if element['type'] == 'Modal'][0]
        modal['props']['is_open'] = False

        current_body = [element if element['props']['id'] != 'modal-xl' else modal for element in current_body]

        return current_body + [edit_button, delete_button, new_figure]

    elif input_trigger == 'edit-button' and edit_but_clicks > 0:
        
        figure_id = {'index': modal_title['props']['children'][8:], 'type': 'figure'}
        figure = [element for element in current_body if element['props']['id'] == figure_id][0]
        figure['props']['figure'] = new_fig
        current_body = [element if element['props']['id'] != figure_id else figure for element in current_body]
        
        return current_body

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

        else:
            raise PreventUpdate

@app.callback(
    [
        Output("modal-header", "children"), 
        Output("modal-body", "children"),
        Output("modal-footer", "children"),
        Output("modal-xl", "is_open")
    ],
    [
        Input({'action': 'create', 'type': ALL}, 'n_clicks'), 
        Input({'index': ALL, 'action': 'edit', 'type': ALL}, 'n_clicks'),
        Input("close-modal", "n_clicks")
    ],
    [State("modal-xl", "is_open"), State("body", 'children')],
)
def update_modal(create_element_n_clicks, edit_but_n_clicks, close_modal_n_clicks, is_open, all_elements):

    input_trigger = get_input_trigger_id(dash.callback_context)

    if input_trigger == 'X':
        return dash.no_update, dash.no_update, dash.no_update, False

    elif input_trigger == 'close-modal':
        modal_footer=[
                        html.Div(
                            [
                                dbc.Button("Add Element", id="add-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Edit Element", id="edit-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Close", id="close-modal", className='mx-2')
                            ]
                        )
                    ]
        return dash.no_update, dash.no_update, modal_footer, False

    else:
        input_trigger = json.loads(input_trigger)
        trigger_action, trigger_type = input_trigger['action'], input_trigger['type']

        if trigger_action == 'create':
            modal_body = [
                dbc.Row([
                    dbc.Col(dcc.Graph(id='new-plot', figure=fig), width=8),
                    dbc.Col(
                        html.Div(
                            [
                                html.H2('Control Panel'),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('Data', className='col-3'), 
                                        dbc.Select(
                                            id='data-dd', className='col-8',
                                            options = [{'label':filename, 'value': filename} for filename in list(data_dict)]
                                        )
                                    ]
                                ), 
                                html.Br(),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('X', className='col-3'), 
                                        dbc.Select(
                                            id='x-col-dd', className='col-8'
                                        )
                                    ]
                                ), 
                                html.Br(),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('Y', className='col-3'), 
                                        dbc.Select(
                                            id='x-col-dd', className='col-8'
                                        )
                                    ]
                                ), 
                                html.Br(),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('Title', className='col-3'), 
                                        dbc.Input(id={'index':'title', 'action':'change', 'type':'bar-chart'}, className='col-8')
                                    ]
                                ), 
                                html.Br(),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('X-axis title', className='col-3'), 
                                        dbc.Input(id={'index':'x-title', 'action':'change', 'type':'bar-chart'}, className='col-8')
                                    ]
                                ), 
                                html.Br(),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('Y-axis title', className='col-3'), 
                                        dbc.Input(id={'index':'y-title', 'action':'change', 'type':'bar-chart'}, className='col-8')
                                    ]
                                )
                            ]
                        ), width=4
                    )
                ])
            ]

            modal_footer=[
                        html.Div(
                            [
                                dbc.Button("Add Element", id="add-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Edit Element", id="edit-button", n_clicks=0, className='mx-2', style="display: none"),
                                dbc.Button("Close", id="close-modal", className='mx-2')
                            ]
                        )
                    ]

            return html.H2(f'Creating new {trigger_type}'), modal_body, modal_footer, True

        elif trigger_action == 'edit':

            trigger_id = input_trigger['index']

            graphs = [element for element in all_elements if element['type'] == 'Graph']
            edit_fig = [graph for graph in graphs if graph['props']['id']['index'] == trigger_id]

            modal_body = [
                dbc.Row([
                    dbc.Col(dcc.Graph(id='new-plot', figure=edit_fig[0]['props']["figure"]), width=8),
                    dbc.Col(
                        html.Div(
                            [
                                html.H2('Control Panel'),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('Title', className='col-3'), 
                                        dbc.Input(id={'index':'title', 'action':'change', 'type':'bar-chart'}, className='col-8')
                                    ]
                                ), 
                                html.Br(),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('X-axis title', className='col-3'), 
                                        dbc.Input(id={'index':'x-title', 'action':'change', 'type':'bar-chart'}, className='col-8')
                                    ]
                                ), 
                                html.Br(),
                                dbc.InputGroup(
                                    [
                                        dbc.Label('Y-axis title', className='col-3'), 
                                        dbc.Input(id={'index':'y-title', 'action':'change', 'type':'bar-chart'}, className='col-8')
                                    ]
                                )
                            ]
                        ), width=4
                    )
                ])
            ]

            modal_footer=[
                        html.Div(
                            [
                                dbc.Button("Add Element", id="add-button", n_clicks=0, className='mx-2', style="display: none"),
                                dbc.Button("Edit Element", id="edit-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Close", id="close-modal", className='mx-2')
                            ]
                        )
                    ]

            return html.H2(f'Editing {trigger_id}'), modal_body, modal_footer, True

@app.callback(
    Output("new-plot", 'figure'),
    [Input({'action': 'change', 'type': ALL, 'index': ALL}, 'value')],
    [State("new-plot", "figure")],
)
def change_plot(change_value, fig):
    input_trigger = get_input_trigger_id(dash.callback_context)

    if input_trigger == 'X':
        return fig 

    else:
        input_trigger = json.loads(input_trigger)
        trigger_change, trigger_type = input_trigger['index'], input_trigger['type'] 

        if trigger_change == 'title':
            fig['layout']['title'] = change_value[0]

        elif trigger_change == 'x-title':
            fig['layout']['xaxis']['title'] = {'text': change_value[1]}
        
        elif trigger_change == 'y-title':
            fig['layout']['yaxis']['title'] = {'text': change_value[2]}

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)