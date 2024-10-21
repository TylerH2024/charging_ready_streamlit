import pandas as pd
from folium import Map, Icon, PolyLine, Marker
import streamlit as st
import openrouteservice
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
from folium.plugins import HeatMap

API_KEY=st.secrets["API_KEY"]
client=openrouteservice.Client(key=API_KEY)
st.title("Charging Ready")

kendal=(54.3280, -2.7460)
keswick=(54.5994, -3.1340)
st_davids=(51.882916, -5.264581)
st_hywyn=(52.804869, -4.710975)
bideford=(51.014885, -4.213305)
newquay=(50.415365, -5.067994)
belfast=(54.599899, -5.944937)
londonderry=(55.019594, -7.341320)

coordinates = [kendal[::-1], keswick[::-1]]

coordinates2=[st_davids[::-1], st_hywyn[::-1]]

coordinates3=[bideford[::-1], newquay[::-1]]

coordinates4=[belfast[::-1], londonderry[::-1]]

route=client.directions(coordinates=coordinates, profile='driving-car', format='geojson')

route2=client.directions(coordinates=coordinates2, profile='driving-car', format='geojson')

route3=client.directions(coordinates=coordinates3, profile='driving-car', format='geojson')

route4=client.directions(coordinates=coordinates4, profile='driving-car', format='geojson')

def convert_coords(coords):
    return [[coord[1], coord[0]] for coord in coords]
route_coords = route['features'][0]['geometry']['coordinates']
route_coords2 = route2['features'][0]['geometry']['coordinates']
route_coords3 = route3['features'][0]['geometry']['coordinates']
route_coords4 = route4['features'][0]['geometry']['coordinates']


noise_points=pd.read_csv("noise_points.csv")
df_restaurant=pd.read_csv("df_restaurant.csv")
df_owners=pd.read_csv("df_owners.csv")
df_fast_uk=df_restaurant[df_restaurant["category"] == "fast_food"]
                         


map_potential_sites = Map(location=[noise_points['latitude'].mean(), noise_points['longitude'].mean()], zoom_start=5)

PolyLine(
    locations=[(coord[1], coord[0]) for coord in route_coords],
    color='blue', weight=5, opacity=0.8,
).add_to(map_potential_sites)

PolyLine(
    locations=[(coord[1], coord[0]) for coord in route_coords2],
    color='blue', weight=5, opacity=0.8,
).add_to(map_potential_sites)

PolyLine(
    locations=[(coord[1], coord[0]) for coord in route_coords3],
    color='blue', weight=5, opacity=0.8,
).add_to(map_potential_sites)

PolyLine(
    locations=[(coord[1], coord[0]) for coord in route_coords4],
    color='blue', weight=5, opacity=0.8,
).add_to(map_potential_sites)

Marker(belfast, popup="Belfast START", icon=Icon(color='green')).add_to(map_potential_sites) #The Causeway
Marker(londonderry, popup="Londonderry END", icon=Icon(color='red')).add_to(map_potential_sites)

Marker(bideford, popup="Bideford START", icon=Icon(color='green')).add_to(map_potential_sites) #The Atlantic Highway
Marker(newquay, popup="Newquay END", icon=Icon(color='red')).add_to(map_potential_sites)

Marker(kendal, popup="Kendal START", icon=Icon(color='green')).add_to(map_potential_sites) #Kendal to Keswick
Marker(keswick, popup="Keswick END", icon=Icon(color='red')).add_to(map_potential_sites)

Marker(st_davids, popup="St Davids Church START", icon=Icon(color='green')).add_to(map_potential_sites) #The Coastal Way
Marker(st_hywyn, popup="St Hywyns Church END", icon=Icon(color='red')).add_to(map_potential_sites)

marker_cluster = MarkerCluster().add_to(map_potential_sites)
marker_cluster2 = MarkerCluster().add_to(map_potential_sites)


heat_data = [[row['latitude'], row['longitude']] for index, row in noise_points.iterrows()]


for index, row in df_fast_uk.iterrows():
    Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['restaurant_name'],
        icon=Icon(color='green', icon='cutlery')
    ).add_to(marker_cluster)

for index, row in df_owners.iterrows():
    Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['ID'],
        icon=Icon(color='blue', icon='bolt')
    ).add_to(marker_cluster2)




HeatMap(heat_data).add_to(map_potential_sites)
map_potential_sites
