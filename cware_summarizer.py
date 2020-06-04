import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

from transformers import pipeline
#import torch

#torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
#summarizer = pipeline('summarization', model='bart-large-cnn', tokenizer='bart-large-cnn', device=0)
summarizer = pipeline('summarization', model='facebook/bart-large-cnn', tokenizer='facebook/bart-large-cnn')

char_len = [100,150,200,250,300,350,400,450]

app = dash.Dash(__name__)
server = app.server

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Textarea(
        id='input_text',
        value='''A block of text that needs to be summarized. This could be several sentences long or possibly one short sentence. Idealy, this algorithm will detect the short ones and determine that there is no need to abbreviate the text.\n\nHowever, in some cases, the text may be far too much and it will need to be shortened for future use in social media posts.''',
        style={'font-size': '130%', 'width': '100%', 'height': 300},
    ),
    dcc.Slider(
        id='slider_val',
        min=100,
        max=450,
        #step=25,
        marks={str(v): str(v) for v in char_len},
        value=150,
    ),
    html.Button('Submit', id='submit_val', n_clicks=0),
    dcc.Markdown(
        id='sum_text', 
        style={'font-size': '130%', 'border-style': 'solid', 'padding': '1px', 'border-width': '2px'})
])

@app.callback(
    Output('sum_text', 'children'),
    [Input('submit_val', 'n_clicks')],
    [State('input_text', "value"),
    State('slider_val', "value")]
)
def summarize_text(n_clicks, input_text, slider_val):
    # find min number of words
    if n_clicks != 0:
        text_len = int((slider_val * 0.22) + 12.7)
        stext = summarizer(input_text, min_length=5, max_length=text_len)[0]['summary_text']
        return stext

	 
if __name__ == '__main__':
    app.run_server(debug=False)



