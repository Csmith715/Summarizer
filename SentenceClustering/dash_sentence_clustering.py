#### My Dash Code #####

import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
from dash.dependencies import Input, Output
from transformers import BertTokenizer, BertModel
import torch
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from scipy.cluster.hierarchy import linkage

app = dash.Dash(__name__)
server = app.server

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

pgraph = '''The Washington Nationals won the 2019 World Series.
Because of the Coronavirus, the start of the 2020 baseball season has been postponed.
Data Science and Machine Learning Algorithms make life so much easier.
The NBA was the first professional sports league to postpone their games in 2020 due to COVID19.
Sometimes, creating plots for Machine Learning problems can be very time-consuming.
'''

def sent_embeddings(sentence):
    cls_text = str('[CLS]' + sentence)
    input_ids = torch.tensor(tokenizer.encode(sentence)).unsqueeze(0)  # Batch size 1
    outputs = model(input_ids)
    last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple
    
    lhs = np.average(last_hidden_states[0].detach().numpy(), axis=0)
    
    return lhs # Returns an n x 768 sentence embedding, where n is the number of words in the sentence

app.layout = html.Div([
    html.H1('Hierarchical Text Clustering'),
    html.P('To use this tool, paste a body of text into the box below.'),
    html.P('A BERT transformer model will discover the similarity between each sentence and group them accordingly.'),
    html.Div([dcc.Textarea(id='input_text',value=pgraph,style={'width': '90%', 'height': '180px', 'color': 'blue', 'font-size': '130%'})
    	]),
    dcc.Graph(id='section-dendrogram', config={'displayModeBar': False})
    ])

@app.callback(
    Output('section-dendrogram', 'figure'),
    [Input('input_text', 'value')]
)
def update_figure(input_text):
    st = sent_tokenize(input_text)
    labs = [s[:130] for s in st]
    sent_vecs = np.array([sent_embeddings(x) for x in st])

    # calculate full dendrogram
    fig = ff.create_dendrogram(sent_vecs, orientation='left', labels=labs, linkagefun=lambda x: linkage(sent_vecs, 'complete', metric='cosine'))
    fig.update_layout(margin=dict(l=800))
    return fig



if __name__ == '__main__':
    app.run_server(debug=False)
