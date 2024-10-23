import streamlit as st
import pandas as pd
from folium import Map, Icon, PolyLine, Marker, CircleMarker
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import openrouteservice

API_KEY = st.secrets["API_KEY"]

@st.cache_resource
def get_client():
    return openrouteservice.Client(key=API_KEY)

client = get_client()

@st.cache_data
def load_data():
    noise_points = pd.read_csv("noise_points.csv")
    df_fast_uk = pd.read_csv("df_fast_food_combined.csv")
    df_owners = pd.read_csv("df_owners_new.csv")
    noise_points1 = pd.read_csv("noise_points (1).csv")
    return noise_points, df_fast_uk, df_owners, noise_points1

def create_route_map(df_fast_uk, df_owners, noise_points):
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

   
    route = client.directions(coordinates=coordinates, profile='driving-car', format='geojson')
    route2 = client.directions(coordinates=coordinates2, profile='driving-car', format='geojson')
    route3 = client.directions(coordinates=coordinates3, profile='driving-car', format='geojson')
    route4 = client.directions(coordinates=coordinates4, profile='driving-car', format='geojson')

    
    map_potential_sites = Map(location=[noise_points['latitude'].mean(), noise_points['longitude'].mean()], zoom_start=5)

    
    for route in [route, route2, route3, route4]:
        route_coords = route['features'][0]['geometry']['coordinates']
        PolyLine(
            locations=[(coord[1], coord[0]) for coord in route_coords],
            color='blue', weight=5, opacity=0.8,
        ).add_to(map_potential_sites)

    
    start_end_points = [
        (belfast, "Belfast START", 'green'),
        (londonderry, "Londonderry END", 'red'),
        (bideford, "Bideford START", 'green'),
        (newquay, "Newquay END", 'red'),
        (kendal, "Kendal START", 'green'),
        (keswick, "Keswick END", 'red'),
        (st_davids, "St Davids Church START", 'green'),
        (st_hywyn, "St Hywyns Church END", 'red')
    ]

    for point in start_end_points:
        Marker(point[0], popup=point[1], icon=Icon(color=point[2])).add_to(map_potential_sites)

    
    marker_cluster = MarkerCluster().add_to(map_potential_sites)

    
    for index, row in df_fast_uk.iterrows():
        Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['restaurant_name'],
            icon=Icon(color='green', icon='cutlery')
        ).add_to(map_potential_sites)

    
    for index, row in df_owners.iterrows():
        Marker(
            location=[row['latitude'], row['longitude']],
            icon=Icon(color='blue', icon='car', prefix="fa")
        ).add_to(marker_cluster)

    
    heat_data = [[row['latitude'], row['longitude']] for index, row in noise_points.iterrows()]
    HeatMap(heat_data).add_to(map_potential_sites)

    return map_potential_sites

   

noise_points1 = pd.read_csv("noise_points (1).csv")
df_owners=pd.read_csv("df_owners_new")
df_fast_uk = pd.read_csv("df_fast_food_combined.csv")
def create_noise_map(noise_points1):
    option = st.selectbox("Select Cluster", (-1, 2, 4, 3))
    noise_subcluster = noise_points1[noise_points1['sub_cluster'] == option]
    
    map_noise = Map(
        location=[noise_subcluster['latitude'].mean(), noise_subcluster['longitude'].mean()],
        zoom_start=10
    )

    for index, row in df_owners.iterrows():
        Marker(
            location=[row['latitude'], row['longitude']],
            icon=Icon(color='blue', icon='car', prefix="fa")
        ).add_to(marker_cluster)
    for index, row in df_fast_uk.iterrows():
        Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['restaurant_name'],
            icon=Icon(color='green', icon='cutlery')
        ).add_to(map_potential_sites)
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

    return map_noise


st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ("Potential Charging Locations", "Clustered Charging Locations"))

if page == "Potential Charging Locations":
    st.title("Potential Charging Locations")
    noise_points, df_fast_uk, df_owners, noise_points1 = load_data()
    map_potential_sites = create_route_map(df_fast_uk, df_owners, noise_points)
    st_folium(map_potential_sites, key="map_1")

elif page == "Clustered Charging Locations":
    st.title("Potential Charging Locations - Scotland, Northern Ireland, Isle of Man")
    _, _, _, noise_points1 = load_data() 
    map_noise = create_noise_map(noise_points1)
    st_folium(map_noise, key="map_noise")
