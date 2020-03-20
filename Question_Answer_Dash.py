#### My Dash Code #####

import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table as dt

import os

import torch
import torch.nn.functional as F
from transformers import BertForQuestionAnswering, BertTokenizer


app = dash.Dash(__name__)
server = app.server

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

# For GPU processing
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  
model.to(device)

sample_title = 'What will you learn?'
sample_pgraph = '''Becoming a Test Automation Engineer: An Introduction to Python
James Jeffers will host this webinar intended for testers who want to become test automation engineers. During this webinar you'll learn a few of the basics of the Python programming language, get resources, code examples, and advice about how best to learn the Python programming language.
Get ready to dive into Python. Don't wait, register now!'''

app.layout = html.Div([
    html.H1('Answering Questions from Sections of Text'),
    html.P('To use this tool, write a question into the first box. Then paste a body of text into the second box. Each section/section in the body portion should be sperated by a new line.'),
    html.P('A BERT transformer model will find and score the best answer in each section of the text provided.'),
    html.Br(),
    html.Div([dcc.Dropdown(
        id='question-dropdown',
        options=[
            {'label': 'Who is the presenter?', 'value': 'Who is the presenter?'},
            {'label': 'Who are the presenters?', 'value': 'Who are the presenters?'},
            {'label': 'Who are the hosts?', 'value': 'Who are the hosts?'},
            {'label': 'Who should attend?', 'value': 'Who should attend?'},
            {'label': 'What will I learn?', 'value': 'What will I learn?'},
            {'label': 'What are the key points?', 'value': 'What are the key points?'},
            {'label': 'What are the major topics?', 'value': 'What are the major topics?'},
            {'label': 'When is the webinar?', 'value': 'When is the webinar?'},
            {'label': 'How long is the webinar?', 'value': 'How long is the webinar?'}
        ],
        clearable=False,
        value='Who are the presenters?',
        style={'width': '60%', 'color': 'red', 'font-size': '110%'}
    )
        ]),
    html.Div([dcc.Textarea(id='input_body',value=sample_pgraph,style={'width': '90%', 'height': '180px', 'color': 'blue', 'font-size': '130%'})
    	]),
    html.Br(),
    html.Div(id="table1", style={'width': '80%', 'font-size': '110%'})
    ])

@app.callback(
    Output('table1','children'),
    [Input('question-dropdown', 'value'),
     Input('input_body', 'value')]
)
def answer_question(input_question, input_body):
    body_split = input_body.split('\n')
    d = {'question': np.repeat(input_question, len(body_split)), 'context': body_split}
    question_df = pd.DataFrame(data = d)
    
    question_df["encoded"] = question_df.apply(
        lambda row: tokenizer.encode("[CLS] " + row["question"] + " [SEP] " + row["context"] + " [SEP]", add_special_tokens=False), axis=1)
    question_df["tok_type"] = question_df.apply(
        lambda row: [0 if i <= row["encoded"].index(102) else 1 for i in range(len(row["encoded"]))], axis=1)   
    with torch.no_grad():
        X = torch.nn.utils.rnn.pad_sequence([torch.tensor(row) for row in question_df["encoded"]],batch_first=True).to(device)
        T = torch.nn.utils.rnn.pad_sequence([torch.tensor(row) for row in question_df["tok_type"]],batch_first=True).to(device)
        start_scores, end_scores = model(X, token_type_ids=T)
        max_score, max_start = torch.max(start_scores, axis=1)
        soft_max = F.softmax(max_score, dim=0)
    
    answer_df = question_df[["context", "encoded"]].copy()
    answer_df["answer_score"] = max_score.cpu().numpy()
    answer_df["answer_start"] = max_start.cpu().numpy()
    answer_df["answer_softmax"] = soft_max.cpu().numpy()
    max_len = torch.zeros_like(max_start)
    for i in range(max_start.shape[0]):
        max_len[i] = torch.argmax(end_scores[i,max_start[i]:]) + 1

    answer_df["answer_length"] = max_len.cpu().numpy()
    answer_df = answer_df[answer_df.answer_score > 1.0].sort_values(by="answer_score", ascending=False)
    def decode_answer(row):
        input_ids = row.encoded
        offset = row.answer_start
        length = np.clip(row.answer_length, 0, 20)
        return tokenizer.decode(input_ids[offset:][:length])
    answer_df["answer"] = answer_df.apply(decode_answer, axis=1)
    df = answer_df[["answer_softmax","answer"]]
    data = df.to_dict('rows')
    columns =  [{"name": i, "id": i} for i in (df.columns)]

    return dt.DataTable(style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
    },data=data, columns=columns,
    style_cell_conditional=[
        {'if': {'column_id': 'Answer Score'},
         'width': '40%'},
        {'if': {'column_id': 'Answer'},
         'width': '30%'},
    ],
    style_cell={'textAlign': 'left'})


if __name__ == '__main__':
    app.run_server(debug=False)