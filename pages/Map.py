import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import requests
from urllib.parse import unquote
import math

# Get query parameters and session state
query_params = st.query_params
focused_location = st.session_state.get("focus_location", "").lower()
focused_type = st.session_state.get("focus_type", "")
focused_severity = st.session_state.get("focus_severity", "")
focused_status = st.session_state.get("focus_status", "")
focused_time = st.session_state.get("focus_time", "")

st.set_page_config(layout="wide")
st.title("🗺️ EarlyGuard: Live Disaster Map")

# Show focused alert info if available
if focused_location and focused_type:
    st.info(f"📍 **Focused Alert:** {focused_type} - {focused_severity} severity at {focused_location} ({focused_time})")

# Sidebar filters
st.sidebar.header("Filter Alerts")

# Confidence score from session or default
default_confidence = st.session_state.get("focus_confidence", 50)
confidence = st.sidebar.slider("Community Confidence Score (%)", 0, 100, default_confidence)

# Severity mapping
severity_map = {
    "Severe": "High",
    "Moderate": "Medium", 
    "Mild": "Low"
}
raw_severity = st.session_state.get("focus_severity", "Low")
converted_severity = severity_map.get(raw_severity, raw_severity)  # Use raw if not in mapping

# Handle unknown or invalid severity values
valid_severities = ["Low", "Medium", "High"]
if converted_severity not in valid_severities:
    converted_severity = "Low"  # Default to Low if unknown
default_severity = [converted_severity]

# Disaster type mapping
type_map = {
    "Flood Warning": "Flood",
    "Heavy Rain Alert": "Rain",
    "Landslide Risk": "Landslide"
}
raw_type = st.session_state.get("focus_type", "Flood")
converted_type = type_map.get(raw_type, raw_type)  # Use raw if not in mapping

# Handle unknown or invalid disaster types
valid_types = ["Flood", "Fire", "Earthquake", "Rain", "Landslide"]
if converted_type not in valid_types:
    converted_type = "Flood"  # Default to Flood if unknown
default_type = [converted_type]

# Multiselects
selected_severity = st.sidebar.multiselect(
    "Select Severity Level:",
    options=["Low", "Medium", "High"],
    default=default_severity
)

selected_type = st.sidebar.multiselect(
    "Select Disaster Type:",
    options=["Flood", "Fire", "Earthquake", "Rain", "Landslide"],
    default=default_type
)

# Mock data with extended locations for better mapping
data = pd.DataFrame([
    {'latitude': 9.4981, 'longitude': 76.3388, 'severity': 'High', 'type': 'Flood', 'name': 'Alappuzha'},
    {'latitude': 11.685, 'longitude': 76.131, 'severity': 'Medium', 'type': 'Rain', 'name': 'Wayanad'},
    {'latitude': 9.849, 'longitude': 77.099, 'severity': 'Low', 'type': 'Landslide', 'name': 'Idukki'},
    {'latitude': 8.5241, 'longitude': 76.9366, 'severity': 'High', 'type': 'Flood', 'name': 'Thiruvananthapuram'},
    {'latitude': 9.9312, 'longitude': 76.2673, 'severity': 'Medium', 'type': 'Fire', 'name': 'Kochi'},
])

# Emergency services data
shelters = pd.DataFrame({
    'latitude': [9.500, 11.685, 9.850, 8.525, 9.932],
    'longitude': [76.339, 76.130, 77.100, 76.937, 76.268],
    'name': ['Alappuzha Relief Shelter', 'Wayanad Hills Shelter', 'Idukki Camp', 'TVM Central Shelter', 'Kochi Relief Center'],
    'contact': ['+91-477-8881000', '+91-4936-123456', '+91-4868-223344', '+91-471-112233', '+91-484-556677'],
    'address': ['Alappuzha Central', 'Wayanad Hilltop', 'Cheruthoni, Idukki', 'Pattom, TVM', 'MG Road, Kochi'],
    'gmaps': [
        'https://maps.google.com/?q=9.500,76.339',
        'https://maps.google.com/?q=11.685,76.130', 
        'https://maps.google.com/?q=9.850,77.100',
        'https://maps.google.com/?q=8.525,76.937',
        'https://maps.google.com/?q=9.932,76.268'
    ]
})

hospitals = pd.DataFrame({
    'latitude': [9.497, 11.684, 9.848, 8.522, 9.930],
    'longitude': [76.337, 76.132, 77.098, 76.935, 76.265],
    'name': ['Alappuzha Govt Hospital', 'Wayanad Medical Center', 'Idukki District Hospital', 'TVM Medical College', 'Kochi General Hospital'],
    'contact': ['+91-477-2223334', '+91-4936-555666', '+91-4868-445566', '+91-471-223344', '+91-484-778899'],
    'address': ['Hospital Rd, Alappuzha', 'Main Rd, Wayanad', 'Painavu, Idukki', 'Medical College, TVM', 'Ernakulam, Kochi'],
    'gmaps': [
        'https://maps.google.com/?q=9.497,76.337',
        'https://maps.google.com/?q=11.684,76.132',
        'https://maps.google.com/?q=9.848,77.098',
        'https://maps.google.com/?q=8.522,76.935',
        'https://maps.google.com/?q=9.930,76.265'
    ]
})

emergency_services = pd.DataFrame({
    'latitude': [9.499, 9.501, 11.686, 9.849, 8.520, 8.527, 9.928, 9.934],
    'longitude': [76.340, 76.337, 76.129, 77.101, 76.933, 76.940, 76.262, 76.270],
    'type': ['Fire Station', 'Police Station', 'Police Station', 'Fire Station', 'Fire Station', 'Police Station', 'Police Station', 'Fire Station'],
    'name': ['Alappuzha Fire HQ', 'Alappuzha Police Station', 'Wayanad Police HQ', 'Idukki Fire Dept', 'TVM Fire Station', 'TVM Police HQ', 'Kochi Police Station', 'Kochi Fire Dept'],
    'contact': ['+91-477-1122334', '+91-477-5566778', '+91-4936-112200', '+91-4868-998877', '+91-471-334455', '+91-471-667788', '+91-484-990011', '+91-484-223344'],
    'address': ['Fire Station Rd, Alappuzha', 'Police Quarters, Alappuzha', 'Kalpetta, Wayanad', 'Cheruthoni, Idukki', 'Pattom, TVM', 'Museum, TVM', 'MG Road, Kochi', 'Kaloor, Kochi'],
    'gmaps': [
        'https://maps.google.com/?q=9.499,76.340',
        'https://maps.google.com/?q=9.501,76.337',
        'https://maps.google.com/?q=11.686,76.129',
        'https://maps.google.com/?q=9.849,77.101',
        'https://maps.google.com/?q=8.520,76.933',
        'https://maps.google.com/?q=8.527,76.940',
        'https://maps.google.com/?q=9.928,76.262',
        'https://maps.google.com/?q=9.934,76.270'
    ]
})

# Function to compute distance in km between two lat/lon pairs
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))

# Filter disaster data
filtered_data = data[
    data['severity'].isin(selected_severity) &
    data['type'].isin(selected_type)
]

# Handle empty data
if filtered_data.empty:
    st.warning("⚠️ No alerts match your current filters.")
    st.stop()

def get_color(sev):
    return {
        'Low': 'green',
        'Medium': 'orange', 
        'High': 'red'
    }.get(sev, 'blue')

# Center map around focused location or default
map_center = [10.02, 76.35]  # Default center (Kerala)
focus_coords = None

if focused_location:
    # Try to find the focused location in data
    for _, row in data.iterrows():
        if (focused_location.lower() in row['name'].lower() or 
            focused_location.lower() in row['type'].lower()):
            map_center = [row['latitude'], row['longitude']]
            focus_coords = (row['latitude'], row['longitude'])
            break

# Create map
m = folium.Map(location=map_center, zoom_start=13 if focus_coords else 8)

# Create feature groups
disaster_layer = folium.FeatureGroup(name="🚨 Disaster Alerts", show=True)
shelter_layer = folium.FeatureGroup(name="🏚️ Shelters", show=True)
hospital_layer = folium.FeatureGroup(name="🏥 Hospitals", show=True)
emergency_layer = folium.FeatureGroup(name="🚒🚓 Emergency Services", show=True)

# Add disaster alerts
for _, row in filtered_data.iterrows():
    # Check if this is the focused alert
    is_focused = (focus_coords and 
                 abs(row['latitude'] - focus_coords[0]) < 0.01 and 
                 abs(row['longitude'] - focus_coords[1]) < 0.01)
    
    popup_text = f"""
        <div style='font-size:13px; width:220px;'>
            <b>⚠️ {row['type']}</b><br>
            Severity: <span style='color:{get_color(row['severity'])}'><b>{row['severity']}</b></span><br>
            Zone: <b>{row['name']}</b><br>
            Status: {"✅ Alert Active" if confidence >= 60 else "🕵️ Monitoring Only"}<br>
            {f"<span style='color:blue;'><b>📍 FOCUSED ALERT</b></span><br>" if is_focused else ""}
        </div>
    """
    
    # Use larger marker for focused alert
    radius = 12 if is_focused else 8
    
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=radius,
        color=get_color(row['severity']) if confidence >= 60 else 'gray',
        fill=True,
        fill_color=get_color(row['severity']) if confidence >= 60 else 'gray',
        popup=popup_text,
        weight=3 if is_focused else 1
    ).add_to(disaster_layer)

    # Add danger zone circle
    if confidence >= 60:
        folium.Circle(
            location=[row['latitude'], row['longitude']],
            radius=500 if is_focused else 300,
            color='#FF5733',
            fill=True,
            fill_color='#FF5733',
            fill_opacity=0.2 if is_focused else 0.15,
            weight=3 if is_focused else 2,
            dash_array="5,5"
        ).add_to(m)

# Helper function to add nearby emergency services
def add_nearby_markers(df, group, icon_color, icon_name, service_type):
    nearby_count = 0
    for _, row in df.iterrows():
        show_marker = True
        distance_info = ""
        
        if focus_coords:
            dist = haversine(focus_coords[0], focus_coords[1], row['latitude'], row['longitude'])
            if dist <= 15:  # Within 15km
                distance_info = f"📏 {dist:.1f} km away<br>"
                nearby_count += 1
            else:
                show_marker = False
        
        if show_marker:
            popup_html = f"""
            <div style='font-size:13px; width:250px; line-height:1.5;'>
                <b>{service_type} {row['name']}</b><br>
                {distance_info}
                📍 {row['address']}<br>
                📞 <a href='tel:{row['contact']}'>{row['contact']}</a><br>
                🗺️ <a href='{row['gmaps']}' target='_blank'>Open in Google Maps</a>
            </div>
            """
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup_html,
                icon=folium.Icon(color=icon_color, icon=icon_name)
            ).add_to(group)
    
    return nearby_count

# Add emergency services
shelter_count = add_nearby_markers(shelters, shelter_layer, 'green', 'home', '🏚️')
hospital_count = add_nearby_markers(hospitals, hospital_layer, 'blue', 'plus-sign', '🏥')

# Add emergency services (fire and police)
emergency_count = 0
for _, row in emergency_services.iterrows():
    show_marker = True
    distance_info = ""
    
    if focus_coords:
        dist = haversine(focus_coords[0], focus_coords[1], row['latitude'], row['longitude'])
        if dist <= 15:  # Within 15km
            distance_info = f"📏 {dist:.1f} km away<br>"
            emergency_count += 1
        else:
            show_marker = False
    
    if show_marker:
        service_icon = '🚒' if row['type'] == 'Fire Station' else '🚓'
        popup_html = f"""
        <div style='font-size:13px; width:250px; line-height:1.5;'>
            <b>{service_icon} {row['name']}</b><br>
            {distance_info}
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

# Add all layers to map
disaster_layer.add_to(m)
shelter_layer.add_to(m)
hospital_layer.add_to(m)
emergency_layer.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Add legend
legend_html = '''
<div style="
    position: fixed;
    bottom: 80px;
    right: 120px;
    width: 200px;
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
⬜ <span style="color:gray;">Monitoring</span><br>
<hr>
<b>📍 Emergency Services</b><br>
🏚️ Shelters<br>
🏥 Hospitals<br>
🚒 Fire Stations<br>
🚓 Police Stations
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Show nearby services summary
if focus_coords:
    st.sidebar.markdown("### 🚨 Nearby Emergency Services")
    st.sidebar.info(f"""
    **Within 15km of alert:**
    - 🏚️ {shelter_count} Shelters
    - 🏥 {hospital_count} Hospitals  
    - 🚒🚓 {emergency_count} Emergency Services
    """)

# Display the map
st_folium(m, width=1200, height=700)

# Clear focus button
if focused_location:
    if st.button("🔄 Clear Focus & Show All Alerts"):
        # Clear session state
        for key in ['focus_location', 'focus_type', 'focus_severity', 'focus_status', 'focus_time', 'focus_confidence']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()