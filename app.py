from streamlit_folium import st_folium
import pandas as pd
from folium import Map, Icon, PolyLine, Marker, CircleMarker
import streamlit as st
import openrouteservice
from folium.plugins import MarkerCluster, HeatMap


API_KEY = st.secrets["API_KEY"]

@st.cache_resource
def get_client():
    return openrouteservice.Client(key=API_KEY)

client = get_client()

st.title("Charging Ready")

@st.cache_data
def get_route(_client, coordinates):
    return _client.directions(coordinates=coordinates, profile='driving-car', format='geojson')

kendal = (54.3280, -2.7460)
keswick = (54.5994, -3.1340)
st_davids = (51.882916, -5.264581)
st_hywyn = (52.804869, -4.710975)
bideford = (51.014885, -4.213305)
newquay = (50.415365, -5.067994)
belfast = (54.599899, -5.944937)
londonderry = (55.019594, -7.341320)

coordinates = [kendal[::-1], keswick[::-1]]
coordinates2 = [st_davids[::-1], st_hywyn[::-1]]
coordinates3 = [bideford[::-1], newquay[::-1]]
coordinates4 = [belfast[::-1], londonderry[::-1]]

route = get_route(client, coordinates)
route2 = get_route(client, coordinates2)
route3 = get_route(client, coordinates3)
route4 = get_route(client, coordinates4)

def convert_coords(coords):
    return [[coord[1], coord[0]] for coord in coords]

route_coords = route['features'][0]['geometry']['coordinates']
route_coords2 = route2['features'][0]['geometry']['coordinates']
route_coords3 = route3['features'][0]['geometry']['coordinates']
route_coords4 = route4['features'][0]['geometry']['coordinates']

@st.cache_data
def load_data():
    noise_points = pd.read_csv("noise_points.csv")
    df_fast_uk = pd.read_csv("df_fast_food_corrected")
    df_owners = pd.read_csv("df_owners.csv")
    noise_points1 = pd.read_csv("noise_points (1).csv")
    return noise_points, df_fast_uk, df_owners, noise_points1

noise_points, df_fast_uk, df_owners, noise_points1 = load_data()

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

Marker(belfast, popup="Belfast START", icon=Icon(color='green')).add_to(map_potential_sites)
Marker(londonderry, popup="Londonderry END", icon=Icon(color='red')).add_to(map_potential_sites)

Marker(bideford, popup="Bideford START", icon=Icon(color='green')).add_to(map_potential_sites)
Marker(newquay, popup="Newquay END", icon=Icon(color='red')).add_to(map_potential_sites)

Marker(kendal, popup="Kendal START", icon=Icon(color='green')).add_to(map_potential_sites)
Marker(keswick, popup="Keswick END", icon=Icon(color='red')).add_to(map_potential_sites)

Marker(st_davids, popup="St Davids Church START", icon=Icon(color='green')).add_to(map_potential_sites)
Marker(st_hywyn, popup="St Hywyns Church END", icon=Icon(color='red')).add_to(map_potential_sites)

marker_cluster = MarkerCluster().add_to(map_potential_sites)

heat_data = [[row['latitude'], row['longitude']] for index, row in noise_points.iterrows()]

for index, row in df_fast_uk.iterrows():
    Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['restaurant_name'],
        icon=Icon(color='red', icon='cutlery')
    ).add_to(map_potential_sites)

for index, row in df_owners.iterrows():
    Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['ID'],
        icon=Icon(color='blue', icon='bolt')
    ).add_to(marker_cluster)

HeatMap(heat_data).add_to(map_potential_sites)
st_folium(map_potential_sites, key="map_1")

option = st.selectbox("Select Cluster", (-1, 2, 4, 3))

noise_subcluster = noise_points1[noise_points1['sub_cluster'] == option]

map_noise = Map(
    location=[noise_subcluster['latitude'].mean(), noise_subcluster['longitude'].mean()],
    zoom_start=10
)

for idx, row in noise_subcluster.iterrows():
    CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.6,
        popup=f"Potential Charging Location at ({row['latitude']}, {row['longitude']})"
    ).add_to(map_noise)

st_folium(map_noise, key=f"subcluster_map_{option}")
