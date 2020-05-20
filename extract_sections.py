#### My Dash Code #####

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_ui as dui

import os
import pickle

from phrase_funcs import *

external_stylesheets = ["https://codepen.io/rmarren1/pen/mLqGRg.css"]

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
server = app.server


useable_text = '''This is where the useable text will go.

There will be an introduction section of the page that will look like this. It will probably be one or two sentences.

Then there might be a summary section that tells us about what we will learn in the webinar. This could be independent of a bulleted list that might follow.

If there is a list, we would learn:
- That a list isn't always necessary
- They can tell us what we'll learn, but not in this case
- There's no certainty that this list will be the one we need.

'''

grid = dui.Grid(_id="grid", num_rows=12, num_cols=12, grid_padding=1)

# grid.add_element(
#     col=1, row=1, width=10, height=2,
#     element=html.Div([
#         dcc.Upload(
#             id='upload-data',
#             children=html.Div([
#                 'Drag and Drop or ',
#                 html.A('Select Files')
#             ]),
#             style={
#                 'width': '100%',
#                 'height': '60px',
#                 'lineHeight': '60px',
#                 'borderWidth': '1px',
#                 'borderStyle': 'dashed',
#                 'borderRadius': '5px',
#                 'textAlign': 'center',
#                 'margin': '10px'
#             })
#         ])

#     )
####### Left side of the page
grid.add_element(
    col=1, row=1, width=4, height=1,
    element=html.Div([
        html.H1('Classifying Sections of Text'),
        html.P('Paste text to be analyzed into the text box below.'),
        ])
    )
grid.add_element(
    col=1, row=2, width=4, height=7,
    element=html.Div([dcc.Textarea(
        id='input_body',
        value=useable_text,
        style={'width': '100%', 'height': '350px', 'color': 'blue', 'font-size': '130%'})
        ])
    )

####### Right side of the page
grid.add_element(
    col=6, row=1, width=4, height=1,
    element=html.Div([html.H3('Introduction:')]))
grid.add_element(
    col=6, row=2, width=4, height=2,
    element=html.Div([
        html.Div([dcc.Markdown(id='result1', style={'font-size': '130%', 'border-style': 'solid', 'padding': '1px', 'border-width': '2px'})])
        ])
    )
grid.add_element(
    col=6, row=4, width=4, height=1,
    element=html.Div([html.H3('Sentence "What you will learn":')]))
grid.add_element(
    col=6, row=5, width=4, height=2,
    element=html.Div([
        html.Div([dcc.Markdown(id='result2', style={'font-size': '130%', 'border-style': 'solid', 'padding': '1px', 'border-width': '2px'})])
        ])
    )
grid.add_element(
    col=6, row=7, width=4, height=1,
    element=html.Div([html.H3('List "What you will learn":')]))
grid.add_element(
    col=6, row=8, width=4, height=2,
    element=html.Div([
        html.Div([dcc.Markdown(id='result3', style={'font-size': '130%', 'border-style': 'solid', 'padding': '1px', 'border-width': '2px'})])
        ])
    )
grid.add_element(
    col=6, row=10, width=4, height=1,
    element=html.Div([html.H3('Speaker(s):')]))
grid.add_element(
    col=6, row=11, width=4, height=2,
    element=html.Div([
        html.Div([dcc.Markdown(id='result4', style={'font-size': '130%', 'border-style': 'solid', 'padding': '1px', 'border-width': '2px'})])
        ])
    )
app.layout = html.Div(grid.get_component(), style={
    "height": "calc(100vh - 20px)",
    "width": "calc(100vw - 20px)"
})

@app.callback(
    [Output('result1','children'),
     Output('result2','children'),
     Output('result3','children'),
     Output('result4','children')],
    [Input('input_body', 'value')]
)
def find_sections(input_body):
    i, s, l, sp = extract_sections(input_body)

    return i, s, l, sp


if __name__ == '__main__':
    app.run_server(debug=False)
