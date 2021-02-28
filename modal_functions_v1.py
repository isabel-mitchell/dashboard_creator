import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def populate_header(trigger_action, trigger_type, id=None):
    text = f'Create new {trigger_type}' if trigger_action == 'create' else f'Edit {id}'
    return html.H1(text)

def populate_footer(trigger_action):
    if trigger_action == 'create':
        children = [
                        html.Div(
                            [
                                dbc.Button("Add Element", id="add-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Close", id="close-modal", className='mx-2')
                            ]
                        )
                    ]
    else:
        children=[
                        html.Div(
                            [
                                dbc.Button("Edit Element", id="edit-button", n_clicks=0, className='mx-2'),
                                dbc.Button("Close", id="close-modal", className='mx-2')
                            ]
                        )
                    ]
    return children

def make_accordion_item(title, content):
    return dbc.Card(
        [
            html.Button(
                html.H2(title),
                id={'action':'collapse-but', 'key':title}
            ),
            dbc.Collapse(
                dbc.CardBody(content),
                id={'action':'collapse-card', 'key':title},
                is_open=False
            ),
        ]
    )

def make_data_panel(trigger_type, data_dict, *arg):
    return [
        dbc.InputGroup(
            [
                dbc.Label('Data', className='col-3'), 
                dbc.Select(
                    id={'type':'input', 'plot':trigger_type, 'input_id':'data-dd', 'panel':'data'}, 
                    className='col-8',
                    options = [{'label':filename, 'value': filename} for filename in list(data_dict)]
                )
            ]
        ), 
        html.Br(),
        dbc.InputGroup(
            [
                dbc.Label('X', className='col-3'), 
                dbc.Select(
                    id={'type':'input-col', 'plot':trigger_type, 'input_id':'x-col-dd', 'panel':'data'},
                    className='col-8'
                )
            ]
        ), 
        html.Br(),
        dbc.InputGroup(
            [
                dbc.Label('Y', className='col-3'), 
                dbc.Select(
                    id={'type':'input-col', 'plot':trigger_type, 'input_id':'y-col-dd', 'panel':'data'},
                    className='col-8'
                )
            ]
        )
    ]

def make_text_panel(trigger_type, *arg):
    return [
        dbc.InputGroup(
            [
                dbc.Label('Title', className='col-3'), 
                dbc.Input(id={'input_id':'title', 'type':'input-col', 'plot':trigger_type, 'panel':'text'}, className='col-8')
            ]
        ), 
        html.Br(),
        dbc.InputGroup(
            [
                dbc.Label('X-axis title', className='col-3'), 
                dbc.Input(id={'input_id':'x-title', 'type':'input-col', 'plot':trigger_type, 'panel':'text'}, className='col-8')
            ]
        ), 
        html.Br(),
        dbc.InputGroup(
            [
                dbc.Label('Y-axis title', className='col-3'), 
                dbc.Input(id={'input_id':'y-title', 'type':'input-col', 'plot':trigger_type, 'panel':'text'}, className='col-8')
            ]
        )
    ]


modal_dict = {
    'bar-chart': {
        'accordion':[
            ['Data', make_data_panel], 
            ['Text', make_text_panel]#, 
            #['Specifics', make_data_panel], 
            #['Callbacks', make_text_panel]
        ]
    },
    'text': {
        'accordion':[
            ['Text', make_text_panel], 
            ['Specifics', make_data_panel]
        ]
    },
    'pie-chart': {
        'accordion':[
            ['Data', make_data_panel], 
            ['Text', make_text_panel], 
            ['Specifics', make_data_panel], 
            ['Callbacks', make_text_panel]
        ]
    },
    'title': {
        'accordion':[
            ['Specifics', make_data_panel], 
            ['Callbacks', make_text_panel]
        ]
    },
}

def populate_body(trigger_action, trigger_type, data_dict=None, id=None, current_body=None):
    control_panel = html.Div(
                        [make_accordion_item(panel[0], panel[1](trigger_type,data_dict)) for panel in modal_dict[trigger_type]['accordion']],
                        className="accordion"
                )
    return dbc.Row([
        dbc.Col(dcc.Graph(id={'id':'new-plot', 'plot':trigger_type, 'type':'modal'}, figure=go.Figure(data=[], layout={})), width=8),
        dbc.Col(control_panel, width=4, style={'overflowY':'scroll', 'height': '450px'})
    ])