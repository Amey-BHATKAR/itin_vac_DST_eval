from genericpath import exists
import time
import folium
import networkx as nx
import haversine as hs
from sklearn.cluster import KMeans
import pandas as pd

ADJUSTED_TYPES = [
    "AffordableAccomodation",
    "Artistic",
    "Convenience",
    "Drinks",
    "HotelAccomodation",
    "Leisure",
    "NaturalHeritage",
    "LocalCulture",
    "Neutral",
    "SitDown",
    "SportsPlace",
    "TakeAway",
    "CulturalBuilding",
    "Tour"
]

#0-> walk, 1->bikes, 2->vehicles
#t->MAX_KM_BY_TRANSPORT, c->NUM_CLUSTER_BY_TRANSPORT, z->ZOOM_LVL
TRANSPORT_CONSTS = [
    {"t": 5, "c": 100, "z": 20}, #10 km Aller / Retour
    {"t": 15, "c": 50, "z": 11}, #30 km Aller / Retour
    {"t": 90, "c": 30, "z": 8} #180 km Aller / Retour
]

class Itinerary_ML():
    def __init__(self, df_pois, user_profile, seed=123):
        #(user_profile.lat, user_profile.long) will provide the user location
        # we need to get a POI nearest to this location
        # for now, id for the test : 63c401c21e7d3679d3d4b45c
        # test 2 : 63c4026e014aa0055131d637
        # test 3 : 63c40272014aa0055131ee64
        '''
        for the start point
        {
            "lat": "44.185174", 
            "long": "4.33038", 
            "name": "Biblioth\\u00e8que de Fons-sur-Lussan", 
            "id": "63c401c21e7d3679d3d4b45c", 
            "Artistic": 1, 
            "CulturalBuilding": 1, 
            "Neutral": 1, 
            "SportsPlace": 1
        }
        '''
        dummy_u_id = "63c40272014aa0055131ee64" if "u_id" not in user_profile else user_profile["u_id"]
        print("setting up ML")
        self.df = df_pois
        self.start_pos = self.get_pos_w_id(dummy_u_id, self.df)
        
        # calculating weights for each POI based on the user profile
        '''
        user profile interests
        {
            "Artistic": 4, 
            "CulturalBuilding": 7, 
            "Neutral": 1, 
            "SportsPlace": 3,
            "HotelAccomodation": 8,
            "LocalCulture": 6
            "Convenience": 8,
            "Drinks": 8,
            "Leisure": 7,
            "NaturalHeritage": 9,
            "SitDown": 8,
            "TakeAway": 2,
            "Tour": 6,
            "AffordableAccomodation": 9
        }
        
        dummy_u_p = {
            "Artistic": 4, 
            "CulturalBuilding": 7, 
            "Neutral": 1, 
            "SportsPlace": 3,
            "HotelAccomodation": 8,
            "LocalCulture": 6,
            "Convenience": 8,
            "Drinks": 8,
            "Leisure": 7,
            "NaturalHeritage": 9,
            "SitDown": 8,
            "TakeAway": 2,
            "Tour": 6,
            "AffordableAccomodation": 9
        }'''
        dum_u_p_vals = []
        '''for a_t in ADJUSTED_TYPES:
            dum_u_p_vals.append(int(dummy_u_p[a_t]))'''
        if "profile" in user_profile:
            dum_u_p_vals = user_profile["profile"]
        '''dum_u_p_vals = dum_u_p.values()
        user_prof_weights = np.array([1 for i in range(14)])
        dum_u_p_vals = [a * b for a, b in zip(dum_u_p_vals,user_prof_weights)]'''
        # TODO: send the user profile here
        self.df = self.weight_pois(dum_u_p_vals)
        print(self.df.head())

        # u_moyen_mobilite = "Voiture" thus TRANSPORT_CONSTS[2]
        dummy_u_t = "car" if "u_tr_type" not in user_profile else user_profile["u_tr_type"]
        t_vals = TRANSPORT_CONSTS[0 if dummy_u_t=="walk" else 1 if dummy_u_t=="bike" else 2]
        self.num_clusters = t_vals["c"]
        
        self.G, self.kmeans, self.predictions, self.clustered = self.create_graph_and_clustering(seed)

        self.score_clusters = self.get_score_clusters()

        self.start_cluster = self.get_first_cluster(dummy_u_id)
        
        dummy_u_days = 8 if "u_nb_days" not in user_profile else int(user_profile["u_nb_days"])
        self.list_of_paths = self.find_paths(self.G, self.start_cluster, dummy_u_days-1)
        
        self.path_through_clusters = self.get_best_path()

        self.global_itineraire = self.get_global_itineraire(dummy_u_id)


    def get_pos_w_id(self, id_poi, df):
        return (df[df["id"]==id_poi]["lat"].item(),df[df["id"]==id_poi]["long"].item())

    def weight_pois(self, profile_vals):
        self.df["score"] = self.df[ADJUSTED_TYPES].dot(float(profile_vals))
        return self.df

    def get_distances(self, pos, clusters):
        n = clusters.tolist().index(pos.tolist())
        '''print(n, len(clusters))
        for cluster in list(range(0, n)) + list(range(n+1, len(clusters))):
            print(pos, clusters[cluster])
            print(hs.haversine(pos, clusters[cluster]), cluster)
            break'''
        distances = [(cluster, hs.haversine(pos, clusters[cluster])) for cluster in list(range(0, n)) + list(range(n+1, len(clusters)))]
        #print(distances)
        return distances

    def get_neighbors(self, pos, clusters, nb_closest):
        distances = self.get_distances(pos, clusters)
        distances.sort(key = lambda x: x[1])
        return distances[:][:nb_closest]

    def get_clustering(self, seed):    
        kmeans = KMeans(
            n_clusters = self.num_clusters,
            random_state=seed,
            n_init=50
        )
        X = self.df[['lat','long']].values
        predictions = kmeans.fit_predict(X) 
        clustered = pd.concat(
            [
                self.df.reset_index(), 
                pd.DataFrame({'Cluster':predictions})
            ], 
            axis = 1
        )
        return kmeans, predictions, clustered

    def create_graph_and_clustering(self, seed):
        kmeans, predictions, clustered = self.get_clustering(seed)
        G = nx.Graph()
        for k in range(len(kmeans.cluster_centers_)):
            G.add_node(
                k, 
                pos = (
                    kmeans.cluster_centers_[k][0], 
                    kmeans.cluster_centers_[k][1]
                )
            )
        for k in range(len(kmeans.cluster_centers_)):
            five_closest = self.get_neighbors(
                kmeans.cluster_centers_[k], 
                kmeans.cluster_centers_, 
                5
            )
            for node in five_closest:
                G.add_edge(k, node[0])
        return G, kmeans, predictions, clustered

    def get_score_clusters(self):
        #returns the mean score of all clusters
        scores = []
        for c in range(self.num_clusters):
            cluster = self.clustered[self.clustered["Cluster"]==c]
            scores.append((c, cluster["score"].mean()))
        return scores

    def get_first_cluster(self, poi_id):
        return self.clustered[self.clustered["id"]==poi_id]["Cluster"].item()

    def find_paths(self, G, node, length):
        #findPaths : returns all the permutations of paths of specifed length from a node
        #copié de : https://stackoverflow.com/questions/28095646/finding-all-paths-walks-of-given-length-in-a-networkx-graph
        if length==0:
            return [[node]]
        paths = [[node]+path for neighbor in G.neighbors(node) for path in self.find_paths(G,neighbor,length-1) if node not in path]  #MAGIC
        return paths

    def get_score_path(self, path):
        #returns the score of a path
        return sum([self.score_clusters[node][1] for node in path])

    def get_best_path(self):
        score_max = 0
        best_path = []
        for path in self.list_of_paths:
            score_path = self.get_score_path(path)
            if score_path > score_max:
                score_max = score_path
                best_path = path
        return best_path

    def get_score_ajuste(self, score, distance):
        # returns the adjusted score for a POI . TO REMAKE
        # TODO IMPROVE this GREATLY. We had ideas with amey. A step function would be nice
        if distance < 0.01:
            return -1
        else:
            return score/distance

    def get_next_POI(self, current, current_position, df):
        df = df.copy()
        df["Coord"] = list(zip((df["lat"]), df["long"]))
        df["Distance_to_current"] = df["Coord"].apply(lambda point: hs.haversine(current_position, point))
        
        df["Score_ajuste"] = df.apply(lambda x: self.get_score_ajuste(x["score"], x["Distance_to_current"]), axis = 1)    
        next_poi_index = df["Score_ajuste"].idxmax()
        next_poi = df["id"].loc[next_poi_index]
        t_visite = 60
        return next_poi, t_visite

    def get_itineraire(self, start, start_position, df):
    
        df_iti = df.copy()
        list_POI = [start]
        t, end_time = 8.*60, 19.5*60        # on commence l'itinéraire a 8h du matin et on finit l'itineraire a 19h30 
        current, current_position = start, start_position
        to_drop = df_iti.index[df_iti["id"]==start].tolist()
        df_iti = df_iti.drop(to_drop)
        while t < end_time:
            next_POI, t_visite = self.get_next_POI(current, current_position, df_iti)
            list_POI.append(next_POI)
            t += t_visite
            to_drop = df_iti.index[df_iti["id"]==next_POI].tolist()
            df_iti = df_iti.drop(to_drop)
            #print(df_iti[df_iti["URI_ID_du_POI"]==next_POI])
        return list_POI

    def get_global_itineraire(self, poi_id):
        #input: start is the uuid of the POI 
        #       clustered is the dataset with k means 
        #       path is the path through the clusters
        
        itineraire = {}
        start_pos = self.start_pos
        # position = (datatourisme_df[ datatourisme_df["URI_ID_du_POI"] == start ][ "Latitude" ].item() , datatourisme_df[ datatourisme_df["URI_ID_du_POI"] == start]["Longitude"].item())
        start = poi_id
        for day in range(len(self.path_through_clusters)):
            itineraire["day_"+str(day)] = self.get_itineraire(start, start_pos, df = self.clustered[self.clustered["Cluster"]==self.path_through_clusters[day]])
            start = itineraire["day_"+str(day)][-1]
            start_pos = self.get_pos_w_id(start, self.clustered)
        return itineraire
