import streamlit as st
import pandas as pd
import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from bs4 import BeautifulSoup
import re

# Define folders
RAW_FILES_FOLDER = "raw_files"
OUTPUT_FOLDER = "processed_data"
os.makedirs(RAW_FILES_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to get the latest file from a folder
def get_latest_file(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    if not files:
        return None
    return max([os.path.join(folder_path, f) for f in files], key=os.path.getctime)

# Function to extract unique code from filename
def extract_unique_code(filename):
    code = filename.split("-")[-1].split(".")[0]
    return code if code.isdigit() and 2 <= len(code) <= 10 else None

# Preprocess function for Item Name
def preprocess_item_name(name):
    if not isinstance(name, str):
        name = str(name) if pd.notna(name) else ""
    
    match = re.match(r"^(\d+\*?)[-\s]*(.*)", name)
    if match:
        number, remaining_name = match.groups()
        name = f"{remaining_name} ({number})"
    name = re.sub(r"^\.", "", name.replace("-", ""))
    name = re.sub(r"(\d+)\*(\d+)", r"\1\2 (*)", name)
    
    return name.strip()

# Function to load and preprocess Excel data
def load_and_preprocess_data(file_path, unique_code):
    data = pd.read_excel(file_path)
    data = data[data["Item Name"].notna() & (data["Item Name"] != "")]
    data["Item Name"] = data["Item Name"].apply(preprocess_item_name)
    data["Department"].replace([None, 0], "Other", inplace=True)
    data.sort_values(by=["Department", "Item Code"], inplace=True)
    data["Code"] = unique_code
    return data

# Function to search for images on Google
def search_image(query):
    try:
        search_url = f"https://www.google.com/search?tbm=isch&q={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            images = soup.find_all("img")
            for img in images:
                img_url = img.get("src")
                if img_url and "http" in img_url:
                    return img_url
    except requests.ConnectionError:
        st.warning("Could not connect to the internet. Using placeholder images.")
    return None

# Function to download and process an image
def download_and_process_image(img_url, file_name, output_folder, max_size_kb=50):
    if not file_name:
        return False
    safe_file_name = re.sub(r'[\\/*?:"<>|]', "_", str(file_name))
    response = requests.get(img_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image = image.resize((400, 400), Image.LANCZOS)
        filtered_image = image.filter(ImageFilter.SHARPEN)
        temp_path = os.path.join(output_folder, f"{safe_file_name}_temp.webp")
        filtered_image.save(temp_path, format='WEBP', optimize=True, quality=85)
        file_size_kb = os.path.getsize(temp_path) / 1024
        quality = 85
        while file_size_kb > max_size_kb and quality > 10:
            filtered_image.save(temp_path, format='WEBP', optimize=True, quality=quality)
            file_size_kb = os.path.getsize(temp_path) / 1024
            quality -= 5
        final_path = os.path.join(output_folder, f"{safe_file_name}.webp")
        if os.path.exists(final_path):
            os.remove(final_path)
        os.rename(temp_path, final_path)
        return True
    return False

# Function to create a placeholder image
def create_placeholder_image(file_name, output_folder):
    placeholder = Image.new("RGB", (400, 400), color="white")
    draw = ImageDraw.Draw(placeholder)
    font = ImageFont.load_default()
    text = "No Image Found"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_x = (400 - (text_bbox[2] - text_bbox[0])) // 2
    text_y = (400 - (text_bbox[3] - text_bbox[1])) // 2
    draw.text((text_x, text_y), text, fill="Black", font=font)
    safe_file_name = re.sub(r'[\\/*?:"<>|]', "_", str(file_name))
    placeholder_path = os.path.join(output_folder, f"{safe_file_name}.webp")
    placeholder.save(placeholder_path, format="WEBP", optimize=True, quality=85)
    return placeholder_path

# Streamlit UI
st.title("Automated Inventory Image Processor")
st.write("This app continuously monitors the 'raw_files' folder, processes new files, and saves outputs with unique codes.")

# Processing loop
while True:
    latest_file_path = get_latest_file(RAW_FILES_FOLDER)
    if latest_file_path:
        filename = os.path.basename(latest_file_path)
        unique_code = extract_unique_code(filename)
        
        if unique_code:
            st.write(f"Processing file: {filename} with unique code: {unique_code}")
            unique_code_folder = os.path.join(OUTPUT_FOLDER, unique_code)
            os.makedirs(unique_code_folder, exist_ok=True)

            # Create "Department" folder for images of items in the Department column only
            department_folder = os.path.join(unique_code_folder, "Department")
            os.makedirs(department_folder, exist_ok=True)

            # Load and preprocess data
            data = load_and_preprocess_data(latest_file_path, unique_code)
            processed_file_path = os.path.join(unique_code_folder, f"processed_data_{unique_code}.xlsx")
            data.to_excel(processed_file_path, index=False)
            st.write(f"**Processed Excel file saved as:** {processed_file_path}")

            # Download one image per unique department and save it in the Department folder
            departments = data["Department"].unique()
            for dept in departments:
                dept_img_url = search_image(dept)
                if dept_img_url:
                    download_and_process_image(dept_img_url, dept, department_folder)
                else:
                    create_placeholder_image(dept, department_folder)

            # Process each row for Item Name images
            for _, row in data.iterrows():
                item_name = row["Item Name"]
                item_code = str(row.get("Item Code", "N/A"))
                img_url = search_image(item_name)

                # Save Item Name images directly in unique_code_folder
                if img_url:
                    download_and_process_image(img_url, item_code, unique_code_folder)
                else:
                    create_placeholder_image(item_code, unique_code_folder)

            st.success(f"Processing for file {filename} complete.")
            os.remove(latest_file_path)  # Delete the file after processing

    # Pause before checking for new files again
    time.sleep(10)
