from itinerary_DB import Itinerary_DB as IT_DB

import dash
from dash import Dash
from dash import dcc
from dash import html
from dash import dash_table
#import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px 
from dash.dependencies import Output, Input

# for external style sheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(
    __name__, 
    external_stylesheets = external_stylesheets,
    suppress_callback_exceptions = True
)

app.layout = html.Div([
    dcc.Location(id="link_main_page", refresh=False),
    html.Div(id = "div_main_page")
])

index_page = html.Div([
    html.H1("Vacation Itinerary", style={'color' : 'aquamarine', 'textAlign': 'center'}),
    html.Form(
        children=[
            html.Button(dcc.Link('Submit', href='/')),
            dcc.Input(id='input_name', value='enter name', type='text'),
            dcc.Input(id='input_id', value='63c40272014aa0055131ee64', type='text'),
            dcc.Input(id='input_nb_of_days', value='8', type='text'),
            dcc.Input(id='input_tr_type', value='Velo', type='text')
        ],
        id="form_itin_vac",
        action="/page-1"
    )
], style={'alignItems': 'center'})

@app.callback(dash.dependencies.Output(component_id='div_layout_1', component_property='children'),
              [dash.dependencies.Input("input_name", "value"),
              dash.dependencies.Input("input_id", "value"),
              dash.dependencies.Input("input_nb_of_days", "value"),
              dash.dependencies.Input("input_tr_type", "value"),
              dash.dependencies.Input("form_itin_vac", "action")])
def update_itin(name, u_id, u_nb_days, u_tr_type, action):
    print(name, u_id, u_nb_days, u_tr_type)
    if action == '/page-1':
        it_db = IT_DB({"u_id": u_id, "u_nb_days": u_nb_days, "u_tr_type": u_tr_type})

        return get_pois_html(it_db.final_itinerary)
    else:
        return index_page

# Page 1

def get_h2(text):
    return html.H2(text, style={'textAlign': 'center', 'color': 'blue'}),

def get_h3(text):
    return html.H3(text, style={'textAlign': 'center', 'color': 'lightblue'}),

def get_h4(text):
    return html.H4(text, style={'textAlign': 'center', 'color': 'yellow'}),

def get_pois_html(pois):
    '''div_pois = []
    for day in pois.keys():
        div_pois.append(get_h2(day))
        div_poi = []
        for poi in pois[day]:
            div_poi.append(get_h3(poi["name"]))
            div_poi.append(get_h4(poi["lat"]))
            div_poi.append(get_h4(poi["long"]))'''

    #table = "Please enter values for a valid user profile"
    #if len(pois) > 0:
    #table = dash_table.DataTable(pois)

    day_tables = []
    for day in pois.keys():
        day_tables.append(dash_table.DataTable(pois[day]))

    layout_1 = html.Div([
        html.H1('Points of Interests to visit, by day', style={'textAlign': 'center', 'color': 'mediumturquoise'}),
        day_tables,
        html.Button(dcc.Link('Revenir à la page de garde', href='/'))
    ], style = {'background' : 'beige'}, id="div_layout_1")

    return layout_1


# Mise à jour de l'index

@app.callback(dash.dependencies.Output("div_main_page", "children"),
              [dash.dependencies.Input("link_main_page", "pathname")])
def display_page(pathname):
    if pathname == '/':
        return get_pois_html({})
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")


'''
html.Button(dcc.Link('Espérance de vie par PIB', href='/page-1')),
    html.Br(),
    html.Button(dcc.Link('carte du monde', href='/page-2'))


df = px.data.gapminder()
df_1 = df[df['year'] == 2002]

'''


'''@app.callback(Output(component_id='page-1-graph', component_property='figure'),
            [Input(component_id='page-1-slider', component_property='value')])
def update_graph(filter_year):
    df_2 = df[df["year"] == filter_year]
    # Création de la figure plotly
    fig = px.scatter(df_2, x="gdpPercap",
                     y = "lifeExp",
                     color="continent",
                     size="pop")
    return fig'''


# Page 2

'''layout_2 = html.Div([
  html.H1('Page 2', style={'textAlign': 'center', 'color': 'mediumturquoise'}),
  html.Div(dcc.Dropdown(id = 'page-2-dropdown',
                        options= [{'label': 'life expandency', 'value': 'lifeExp'},
                                  {'label': 'population', 'value': 'pop'}],
                        value= 'lifeExp'
  )),
  html.Div(dcc.Graph(id='page-2-graph')),
  html.Button(dcc.Link('Revenir à la page de garde', href='/'))
], style = {'background' : 'beige'})

@app.callback(Output(component_id='page-2-graph', component_property='figure'),
            [Input(component_id='page-2-dropdown', component_property='value')])
def update_graph_1(indicator):
    # Création de la figure plotly
    fig = px.scatter_geo(df_1, locations="iso_alpha", color=indicator,
                     hover_name="country", size="pop",
                     projection="natural earth")
    return fig'''


'''
    elif pathname == '/page-2':
        return layout_2'''





'''app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

form = dbc.Form(
    id="form",
    children=[
        dbc.Label("Email", className="mr-2"),
        dbc.Input(id="email", type="email", placeholder="Enter email"),
        dbc.Label("Password", className="mr-2"),
        dbc.Input(id="password", type="password", placeholder="Enter password"),
        dbc.Button("Submit", color="primary"),
    ]
)

app.layout = html.Div([form, html.Div(id="output")])


@app.callback(
    Output("output", "children"),
    Input("form", "n_submit"),
    State("email", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def handle_submit(n_submit, email, password):
    # Do stuff...
    return n_submit'''