import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import os
import pandas as pd

def createH1(element, data_dict):
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

def createP(element, data_dict):
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

def createGraph(element, data_dict):
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

def createElement(element, element_key, data_dict):
    createFunction = element_key[element['type']]
    return createFunction(element, data_dict)

def createBody(saved_layout, element_key, data_dict):
    body = [createElement(element, element_key, data_dict) for element in saved_layout]
    return body

def createDataStore(saved_layout):
    dataStore = {element['id']: element['data'] for element in saved_layout if element['graph']}
    return dataStore