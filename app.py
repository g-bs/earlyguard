import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap


st.set_page_config(layout="wide")
st.title("🗺️ EarlyGuard: Live Disaster Map")

# Sidebar filters
st.sidebar.header("Filter Alerts")
confidence = st.sidebar.slider("Community Confidence Score (%)", 0, 100, 50)
selected_severity = st.sidebar.multiselect(
    "Select Severity Level:",
    options=["Low", "Medium", "High"],
   # default=["Low", "Medium", "High"]
)

selected_type = st.sidebar.multiselect(
    "Select Disaster Type:",
    options=["Flood", "Fire", "Earthquake"],
    #default=["Flood", "Fire", "Earthquake"]
)

# Mock data
data = pd.DataFrame({
    'latitude': [10.015, 10.025, 10.035],
    'longitude': [76.345, 76.355, 76.365],
    'severity': ['Low', 'Medium', 'High'],
    'type': ['Flood', 'Fire', 'Earthquake'],
    'name': ['Flood - Zone 1', 'Fire - Zone 2', 'Quake - Zone 3']
})


shelters = pd.DataFrame({
    'latitude': [10.017, 10.028],
    'longitude': [76.342, 76.353],
    'name': ['Shelter A', 'Shelter B']
})

hospitals = pd.DataFrame({
    'latitude': [10.022, 10.030, 10.028],
    'longitude': [76.347, 76.360, 76.357],
    'name': ['Hospital X', 'Hospital Y', 'City General Hospital'],
    'contact': ['+91-484-4441111', '+91-484-4442222', '+91-484-5558888'],
    'address': ['Kadavanthra, Kochi', 'Panampilly Nagar, Kochi', 'Marine Drive'],
    'gmaps': [
        'https://maps.google.com/?q=10.022,76.347',
        'https://maps.google.com/?q=10.030,76.360',
        'https://maps.google.com/?q=10.028,76.357'
    ]
})

emergency_services = pd.DataFrame({
    'latitude': [10.019, 10.033],
    'longitude': [76.348, 76.362],
    'type': ['Police Station', 'Fire Station'],
    'name': ['Kochi Police HQ', 'Ernakulam Fire Dept'],
    'contact': ['+91-484-1234567', '+91-484-7654321'],
    'address': ['MG Road, Kochi', 'Market Rd, Ernakulam'],
    'gmaps': [
        'https://maps.google.com/?q=10.019,76.348',
        'https://maps.google.com/?q=10.033,76.362'
    ]
})

# Filter data
filtered_data = data[
    data['severity'].isin(selected_severity) &
    data['type'].isin(selected_type)
]

# Severity color
def get_color(sev):
    return {
        'Low': 'green',
        'Medium': 'orange',
        'High': 'red'
    }.get(sev, 'blue')

# Create base map
m = folium.Map(location=[10.02, 76.35], zoom_start=13)

# Create feature groups
disaster_layer = folium.FeatureGroup(name="Disaster Alerts", show=True)
shelter_layer = folium.FeatureGroup(name="Shelters", show=True)
hospital_layer = folium.FeatureGroup(name="Hospitals", show=True)

for _, row in filtered_data.iterrows():
    popup_text = (
    f"""
    <div style='font-size:13px; width:200px;'>
        <b>⚠️ {row['type']}</b><br>
        Severity: <span style='color:{get_color(row['severity'])}'>{row['severity']}</span><br>
        Zone: {row['name']}<br>
        Status: {"✅ Alert Active" if confidence >= 60 else "🕵️ Monitoring Only"}
    </div>
    """
)


    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=8,
        color=get_color(row['severity']) if confidence >= 60 else 'gray',
        fill=True,
        fill_color=get_color(row['severity']) if confidence >= 60 else 'gray',
        popup=popup_text
    ).add_to(disaster_layer)


    if confidence >= 60:
        folium.Circle(
            location=[row['latitude'], row['longitude']],
            radius=300,
            color='#FF5733',
            fill=True,
            fill_color='#FF5733',
            fill_opacity=0.15,
            weight=2,
            dash_array="5,5"
        ).add_to(m)

    # Add hospitals
    hospital_layer = folium.FeatureGroup(name="Hospitals", show=True)

for _, row in hospitals.iterrows():
    popup_html = f"""
    <div style='font-size:13px; width:230px; line-height:1.5;'>
        <b>🏥 {row['name']}</b><br>
        📍 {row['address']}<br>
        📞 <a href='tel:{row['contact']}'>{row['contact']}</a><br>
        🗺️ <a href='{row['gmaps']}' target='_blank'>Open in Google Maps</a>
    </div>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup_html,
        icon=folium.Icon(color='blue', icon='plus-sign')
    ).add_to(hospital_layer)

hospital_layer.add_to(m)
emergency_layer = folium.FeatureGroup(name="Emergency Services", show=True)
for _, row in emergency_services.iterrows():
    popup_html = f"""
    <div style='font-size:13px; width:230px; line-height:1.5;'>
        <b>🏢 {row['type']}</b><br>
        <b>{row['name']}</b><br>
        📍 {row['address']}<br>
        📞 <a href='tel:{row['contact']}'>{row['contact']}</a><br>
        🗺️ <a href='{row['gmaps']}' target='_blank'>Open in Google Maps</a>
    </div>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup_html,
        icon=folium.Icon(color='darkred', icon='info-sign')
    ).add_to(emergency_layer)
emergency_layer.add_to(m)

# Add layers to map
disaster_layer.add_to(m)
# Heatmap of filtered disasters
heat_data = [[row['latitude'], row['longitude']] for _, row in filtered_data.iterrows()]
#HeatMap(heat_data).add_to(m)
shelter_layer.add_to(m)
hospital_layer.add_to(m)
folium.LayerControl().add_to(m)
legend_html = '''
<div style="
    position: fixed;
    top: 80px;
    right: 40px;
    width: 180px;
    background-color: white;
    border:2px solid grey;
    z-index:9999;
    font-size:14px;
    padding: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
">
<b>🗺️ Severity Legend</b><br>
🟥 <span style="color:red;">High</span><br>
🟧 <span style="color:orange;">Medium</span><br>
🟩 <span style="color:green;">Low</span><br>
⬜ <span style="color:gray;">Monitoring</span>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Show map
st_folium(m, width=1200, height=700)
