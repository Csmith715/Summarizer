import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

all_teams_df = pd.read_csv('srcdata/dash_simple_nba_srcdata_shot_dist_compiled_data_2019_20.csv')

app = dash.Dash(__name__)
server = app.server
team_names = all_teams_df.group.unique()
team_names.sort()
app.layout = html.Div([
    html.Div([dcc.Dropdown(id='group-select', options=[{'label': i, 'value': i} for i in team_names],
                           value='TOR', style={'width': '140px'})]),
    dcc.Graph('shot-dist-graph', config={'displayModeBar': False})])

@app.callback(
    Output('shot-dist-graph', 'figure'),
    [Input('group-select', 'value')]
)
def update_graph(grpname):
    import plotly.express as px
    return px.scatter(all_teams_df[all_teams_df.group == grpname], x='min_mid', y='player', size='shots_freq', color='pl_pps')

if __name__ == '__main__':
    app.run_server(debug=False)