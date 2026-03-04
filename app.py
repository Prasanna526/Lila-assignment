Semester 4 - Project

import streamlit as st
import pandas as pd
import glob
import plotly.express as px
from PIL import Image

# 1. Map Configuration (Directly from README)
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900, "origin_x": -370, "origin_z": -473, "img": "minimaps/AmbroseValley_Minimap.png"},
    "GrandRift": {"scale": 581, "origin_x": -290, "origin_z": -290, "img": "minimaps/GrandRift_Minimap.png"},
    "Lockdown": {"scale": 1000, "origin_x": -500, "origin_z": -500, "img": "minimaps/Lockdown_Minimap.jpg"}
}

# 2. Conversion Formula
def get_pixel_coords(x, z, config):
    u = (x - config['origin_x']) / config['scale']
    v = (z - config['origin_z']) / config['scale']
    pixel_x = u * 1024
    pixel_y = (1 - v) * 1024 # Flip Y for image space
    return pixel_x, pixel_y

# 3. App UI
st.title("LILA Games: Level Design Analytics")
selected_map = st.sidebar.selectbox("Select Map", list(MAP_CONFIG.keys()))

# 4. Data Loading Logic
@st.cache_data
def load_all_data(map_name):
    files = glob.glob(f"player_data/*/*")
    data_frames = []
    for f in files:
        df = pd.read_parquet(f)
        if df['map_id'].iloc[0] == map_name:
            # Human vs Bot logic: UUID vs Numeric ID
            df['is_bot'] = df['user_id'].str.len() < 10 
            data_frames.append(df)
    return pd.concat(data_frames)

df = load_all_data(selected_map)
df['event'] = df['event'].str.decode('utf-8') # Decode bytes to string

# Apply conversion
conf = MAP_CONFIG[selected_map]
df['pixel_x'], df['pixel_y'] = get_pixel_coords(df['x'], df['z'], conf)

# 5. The Visualization
fig = px.scatter(df, x="pixel_x", y="pixel_y", color="event", 
                 symbol="is_bot", hover_data=["user_id"])

# Overlay on top of the map image
img = Image.open(conf['img'])
fig.add_layout_image(
    dict(source=img, xref="x", yref="y", x=0, y=0, sizex=1024, sizey=1024, 
         sizing="stretch", layer="below")
)
fig.update_layout(width=900, height=900, xaxis_visible=False, yaxis_visible=False)
st.plotly_chart(fig)