from dash import Dash, dcc, dash, html
from dash.dependencies import Input, Output, State
from userProfile import *
import folium, os

from itinerary_DB import Itinerary_DB as IT_DB

FOLIUM_COLORS=[
    'red','blue', 'green', 'purple', 'orange', 'darkred',
    'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
    'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray'
]

# Zoom a appliquer sur la carte
ZOOM_LVL = {
    'Voiture': 8,
    'Velo': 11,
    'Marche': 20
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(
    external_stylesheets=external_stylesheets
)

from city_names import cities

city_datalist = html.Datalist(
    id='list-suggested-cities', 
    children=[html.Option(value=city.strip("/\s /\n /\t /\"   ")) for city in cities]
)

#print(len(cities))

app.layout = html.Div([
    html.H3("Quelle catégorie d'age vous correspond le mieux ?"),
    dcc.Dropdown(
        id="age",
        options=[{"label":"18-25", "value":"18-25"},
                {"label":"25-35", "value":"25-35"},
                {"label":"35-45", "value":"35-45"},
                {"label":"45-55", "value":"45-55"},
                {"label":"55-70", "value":"55-70"},
                {"label":"70+", "value":"70+"}],
        ), 
    html.H3("Voyagez vous avec des enfants en bas age (moins de 5 ans)?"),
    dcc.Dropdown(
        id="babies",
        options=[{"label":"Oui", "value":"YES"},
                {"label":"Non", "value":"NO"}],
        ), 
    html.H3("Quel est votre budget?"),
    dcc.Dropdown(
        id="budget",
        options=[{"label":"Petit", "value":"cheap"},
                {"label":"Moyen", "value":"medium"},
                {"label":"Gros", "value":"expensive"}],
        ),
    dcc.Dropdown(
        id="transport",
        options=[{"label":"With Private cars.", "value":"car"},
                {"label":"Riding on bikes!", "value":"bike"},
                {"label":"walking...", "value":"walk"}],
        ),
    dcc.Dropdown(
        id="city_dd",
        options=[{"label":city.strip("/\s /\n /\t /\"   "), "value":city.strip("/\s /\n /\t /\"   ")} for city in cities],
        ),
    html.Br(),
    html.Button(id='Submit_form', n_clicks=0, children='Submit'),
    html.Div(id='map')
])
'''
dcc.Input(
        id='city_name',
        type='text',
        list='list-suggested-cities',
        value=''
        ),
'''


@app.callback(
    [Output('map', 'children')],
    [Input('Submit_form', 'n_clicks')],
    [State('age', 'value'),
     State('babies', 'value'),
     State('budget', 'value'),
     State('transport', 'value'),
     State('city_dd', 'value')])
def update_map(n_clicks, age, babies, budget, transport, city_dd):
    print( "n_clicks is ",str(n_clicks))
    print(age,babies,budget)

    if age and babies and budget:
        #datatourisme_df=pd.read_csv("poi.csv")
        # getting profile
        profil = genere_profil_utilisateur(age,babies,budget,categories=[],file=os.path.join(os.getcwd(), "dump/data_antoine.tsv"))
        
        # user dummy values
        #transport -> walk, bike, car
        #u_start_point=(43.76587273970739, 1.5109121106288823)
        u_nb_jour = 10
        u_moyen_mobilite = "Marche" # Marche/ Velo / Voiture
        dummy_lat = 43.76587273970739
        dummy_long = 1.5109121106288823
        #get_nearest_point(datatourisme_df,u_start_point)
        # getting db instance with ML implemented
        # TODO: send the user profile here
        it_db = IT_DB({"u_id": "u_id", "u_nb_days": u_nb_jour, "u_tr_type": transport, "u_city": city_dd, "profile": profil})
        #start_poi_uuid = it_db.nearest_POI_ID
        #start_point=get_pos(start_poi_uuid,datatourisme_df)
        #nb_pts_max = 48 # temps min de visite 30 minutes = 24H par jour
        #num_clusters=NUM_CLUSTER_BY_TRANSPORT[u_moyen_mobilite]
        
        # on génere l'itinéraire
        #clustered, path_through_clusters,global_itineraire,kmeans,predictions,G= main_func(profil,start_poi_uuid,num_clusters,u_moyen_mobilite,u_nb_jour,seed=133)
        #on crée notre carte
        # it_db.nearest_POI_ID
        itineraire_map = folium.Map(location = (dummy_lat, dummy_long) , tiles = "OpenStreetMap", zoom_start = ZOOM_LVL[u_moyen_mobilite])
        itineraire_map = plot_itineraire(it_db.it_ml.global_itineraire,it_db.it_ml.clustered,itineraire_map,color_palette=FOLIUM_COLORS,icon='star')
        #on la sauvegarde
        itineraire_map.save(os.path.join(os.getcwd(), "htmls/plot_itineraire.html"))
        # create a json to save the user profile, with a timestamp,
        # associate the aforementioned timestamp in the html file too, 4future
        return [html.Div([html.H1('Your list of stops'),html.Iframe(id='map', srcDoc=open(os.path.join(os.getcwd(), "htmls/plot_itineraire.html"), 'r').read(), width='600px', height='600px')])]
    else:
        return [html.Div([html.H1('Please fill out the neccessary information to construct your itinerary')])]


def plot_itineraire(itineraire,df,map_to_plot,color_palette=FOLIUM_COLORS,icon='star'):
    #setup first POI, otherwise it doesnt work too well. 
    first_poi=itineraire[list(itineraire.keys())[0]][0]
    nom=df[df["id"]==first_poi]["name"]
    color=color_palette[0]
    icon_color = 'dimgray' if color == 'white' else 'white'
    folium.Marker(location= get_pos(first_poi,df),
                popup= f"<h5>Jour 1, étape 1 </h5><p>{nom.item()}</p>",
                icon= folium.Icon(color= color_palette[0], icon_color= icon_color, icon=icon)
                ).add_to(map_to_plot)
    for day in range(len(itineraire.keys())):
        #on parcourt les jours
        trajet= itineraire[list(itineraire.keys())[day]]
        color_idx=day
        color = color_palette[color_idx]
        icon_color = 'dimgray' if color == 'white' else 'white'
        for idx_poi in range(1,len(trajet)):
            
            poi=trajet[idx_poi]
            nom=df[df["id"]==poi]["name"]
            folium.Marker(
                location= get_pos(poi,df),
                popup= f"<h5>Jour {day+1} , etape {idx_poi+1}</h5><p>{nom.item()}</p>",
                icon= folium.Icon(color= color, icon_color= icon_color, icon=icon)
                ).add_to(map_to_plot)
    return map_to_plot

def get_pos(POI_URI,df):
    return (df[df["id"]==POI_URI]["lat"].item(),df[df["id"]==POI_URI]["long"].item())

if __name__ == '__main__':
    app.run_server(debug=False)
