import streamlit as st
from PIL import Image
import numpy as np
import noise
import random

st.set_page_config(page_title="MythicMap Generator", layout="centered")
st.title("🌍 Fantasy World Generator")

st.write("Generate procedural fantasy worlds with adjustable parameters.")

world_size = st.slider("World Size", 256, 1024, 512, step=128)
noise_scale = st.slider("Terrain Scale (lower = bigger continents)", 50.0, 300.0, 120.0)
island_bias = st.slider("Island Fragmentation", 0.0, 1.5, 0.8)
city_count = st.slider("Number of Cities", 0, 30, 10)
temperature_bias = st.slider("Temperature Bias (cold ↔ warm)", -0.5, 0.5, 0.0)
seed = st.number_input("World Seed", value=42)

generate_button = st.button("Generate World")


BIOMES = {
    "ocean": (54, 86, 168),
    "beach": (238, 214, 175),
    "tundra": (220, 240, 240),
    "desert": (237, 201, 175),
    "grassland": (124, 189, 107),
    "forest": (34, 139, 34),
    "mountain": (120, 120, 120)
}


def get_biome(elev, moisture, temp):
    if elev < -0.2:
        return "ocean"
    if elev < -0.15:
        return "beach"
    if elev > 0.45:
        return "mountain"

    if temp < -0.1:
        return "tundra"
    if moisture < -0.2:
        return "desert"
    if moisture < 0.2:
        return "grassland"
    return "forest"


if generate_button:

    img = Image.new("RGB", (world_size, world_size))
    pixels = img.load()

    elevation = np.zeros((world_size, world_size))
    moisture = np.zeros((world_size, world_size))

    for x in range(world_size):
        for y in range(world_size):

            nx = x / noise_scale
            ny = y / noise_scale

            elev = noise.pnoise2(nx, ny, octaves=5, base=seed)
            moist = noise.pnoise2(nx + 100, ny + 100, octaves=4, base=seed)

            # Island shaping
            dx = (x / world_size - 0.5)
            dy = (y / world_size - 0.5)
            distance = np.sqrt(dx*dx + dy*dy)
            elev -= distance * island_bias

            elevation[x][y] = elev
            moisture[x][y] = moist

    # Apply biome rules
    for x in range(world_size):
        for y in range(world_size):
            elev = elevation[x][y]
            moist = moisture[x][y]
            temp = elev + temperature_bias

            biome = get_biome(elev, moist, temp)
            pixels[x, y] = BIOMES[biome]

    # Add cities
    for _ in range(city_count):
        attempts = 0
        while attempts < 200:
            x = random.randint(0, world_size-1)
            y = random.randint(0, world_size-1)

            if pixels[x, y] != BIOMES["ocean"]:
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        if 0 <= x+dx < world_size and 0 <= y+dy < world_size:
                            pixels[x+dx, y+dy] = (178, 34, 34)
                break
            attempts += 1

    st.image(img, caption="Generated World Map", use_column_width=True)

    st.download_button(
        label="Download Map",
        data=img.tobytes(),
        file_name="mythic_map.png"
    )
