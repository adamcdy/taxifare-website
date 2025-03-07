import streamlit as st
import requests
import datetime
import pydeck as pdk

MAPBOX_TOKEN =  "pk.eyJ1Ijoia3Jva3JvYiIsImEiOiJja2YzcmcyNDkwNXVpMnRtZGwxb2MzNWtvIn0.69leM_6Roh26Ju7Lqb2pwQ"




st.markdown("Welcome Passengers!")

st.markdown("Please fill in the following information to get your fare prediction")
mapbox_directions_url = "https://api.mapbox.com/directions/v5/mapbox/driving"


url = 'https://taxifare.lewagon.ai/predict'

# if url == 'https://taxifare.lewagon.ai/predict':

#     st.markdown('Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...')

# Date and time input
date = st.date_input("Select the ride date", datetime.date.today())
time = st.time_input("Select the ride time", datetime.datetime.now().time())

# Numeric inputs for coordinates
pickup_longitude = st.number_input("Pickup Longitude", value=-73.985428, format="%.6f")
pickup_latitude = st.number_input("Pickup Latitude", value=40.748817, format="%.6f")
dropoff_longitude = st.number_input("Dropoff Longitude", value=-73.985428, format="%.6f")
dropoff_latitude = st.number_input("Dropoff Latitude", value=40.748817, format="%.6f")

# Passenger count input
passenger_count = st.number_input("Passenger Count", min_value=1, max_value=6, step=1, value=1)
pickup_datetime = f"{date} {time}"

st.markdown("### Route Visualization")
# map_data = [
#     {"lat": pickup_latitude, "lon": pickup_longitude, "name": "Pickup"},
#     {"lat": dropoff_latitude, "lon": dropoff_longitude, "name": "Dropoff"}
# ]

route_coords = []
directions_request = f"{mapbox_directions_url}/{pickup_longitude},{pickup_latitude};{dropoff_longitude},{dropoff_latitude}?geometries=geojson&access_token={MAPBOX_TOKEN}"

try:
    response = requests.get(directions_request)
    data = response.json()

    # st.write("API Response:", data)  # Debugging line

    if "routes" in data and len(data["routes"]) > 0:
        route_coords = data["routes"][0]["geometry"]["coordinates"]  # Extract real road route
    else:
        st.error("No route found. Check coordinates!")
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching route from Mapbox: {e}")


# Convert route_coords to PyDeck format (swap lon/lat to lat/lon)
route_data = [{"lat": coord[1], "lon": coord[0]} for coord in route_coords]

# Create PyDeck layers
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=[
        {"lat": pickup_latitude, "lon": pickup_longitude, "name": "Pickup"},
        {"lat": dropoff_latitude, "lon": dropoff_longitude, "name": "Dropoff"}
    ],
    get_position=["lon", "lat"],
    get_color=[0, 255, 0, 200],  # Green for pickup, Red for dropoff
    get_radius=100,
    pickable=True
)

# 🚀 **FIXED:** Use actual route geometry from Mapbox, not a straight line!
route_layer = pdk.Layer(
    "PathLayer",  # 🔹 Use PathLayer for multi-point routes!
    data=[{"path": [[coord[0], coord[1]] for coord in route_coords]}],  # Convert to PyDeck path format
    get_path="path",
    get_color=[0, 0, 255, 200],  # Blue for route
    width_scale=5,
    width_min_pixels=3
)


# Define PyDeck map
view_state = pdk.ViewState(
    latitude=(pickup_latitude + dropoff_latitude) / 2,
    longitude=(pickup_longitude + dropoff_longitude) / 2,
    zoom=12,
    pitch=0
)

r = pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v11",
    layers=[scatter_layer, route_layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}"}
)

# Display the map in Streamlit
st.pydeck_chart(r)




params = {
    "pickup_datetime": pickup_datetime,
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}





if st.button("Get Fare Prediction"):
    try:
        response = requests.get(url, params=params)
        data = response.json()  # Convert response to JSON

        if "fare" in data:
            fare_prediction = data["fare"]
            st.success(f"Estimated Fare: ${fare_prediction:.2f}")
        else:
            st.error("API response did not contain a fare prediction.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}")
