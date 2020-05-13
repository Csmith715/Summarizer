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


with open('whatrules2.data', 'rb') as filehandle:
    what_rules2 = pickle.load(filehandle)

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

grid.add_element(
    col=1, row=1, width=4, height=3,
    element=html.Div([
        html.H1('Classifying Sections of Text'),
        html.P('Paste text to be analyzed into the text box below.'),
        html.Br(),
        html.Div([dcc.Dropdown(
            id='question-dropdown',
            options=[
                {'label': 'Broad', 'value': 'Broad'},
                {'label': 'More Concise', 'value': 'More Concise'}
            ],
            clearable=False,
            value='Broad',
            style={'width': '60%', 'color': 'red', 'font-size': '110%'}
        )
            ])
        ])
    )
grid.add_element(
    col=1, row=5, width=4, height=7,
    element=html.Div([dcc.Textarea(
        id='input_body',
        value=useable_text,
        style={'width': '100%', 'height': '350px', 'color': 'blue', 'font-size': '130%'})
        ])
    )
grid.add_element(
    col=6, row=1, width=4, height=5,
    element=html.Div([html.Br(),
        html.H3('Bulleted Summary:'),
        html.Div([dcc.Markdown(id='result1', style={'font-size': '130%'})]),
        #html.Div(id='result1', style={'font-size': '120%'}),
        html.Br()
        ])
    )
grid.add_element(
    col=6, row=7, width=4, height=5,
    element=html.Div([html.Br(),
        html.H3('Sentence Summary:'),
        html.Div([dcc.Markdown(id='result2', style={'font-size': '130%'})]),
        #html.Div(id='result2', style={'font-size': '120%'}),
        html.Br()
        ])
    )

app.layout = html.Div(grid.get_component(), style={
    "height": "calc(100vh - 20px)",
    "width": "calc(100vw - 20px)"
})

# def parse_contents(contents, filename, date):
#     content_type, content_string = contents.split(',')

#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename:
#             # Assume that the user uploaded a CSV file
#             df = pd.read_csv(
#                 io.StringIO(decoded.decode('utf-8')))
#         elif 'xls' in filename:
#             # Assume that the user uploaded an excel file
#             df = pd.read_excel(io.BytesIO(decoded))

#     return df

@app.callback(
    [Output('result1','children'),
     Output('result2','children')],
    [Input('question-dropdown', 'value'),
     Input('input_body', 'value')]
)
def find_sections(input_selection, input_body):
    if input_selection == 'More Concise':
        l, n = split_text_and_extract_sents(input_body)

        return l, n

    elif input_selection == 'Broad':
        l, n = split_listed_text(input_body, what_rules2)

        return l, n


if __name__ == '__main__':
    app.run_server(debug=False)
