---
# Automated Inventory Image Processor

This project is a Streamlit-based application designed to automate the processing of inventory data and associated images. It continuously monitors a folder for new Excel files, preprocesses the data, and retrieves images for each item and department from Google. The processed outputs are saved in organized folders with unique codes.

## Features
- **Automated File Monitoring**: Watches the `raw_files` folder for new Excel files.
- **Data Preprocessing**:
  - Cleans and formats inventory data.
  - Adds unique codes to processed files.
- **Image Processing**:
  - Searches Google for images of item names and departments.
  - Downloads and resizes images to optimized formats.
  - Creates placeholder images if no relevant images are found.
- **Streamlit Interface**:
  - Displays the processing status and results in a web-based UI.

## Folder Structure
- `raw_files/`: Folder for unprocessed Excel files.
- `processed_data/`: Folder for processed data and images.

## Requirements
- **Python Libraries**:
  - `streamlit`
  - `pandas`
  - `Pillow`
  - `requests`
  - `bs4` (BeautifulSoup)
  - `openpyxl`
  - `re`

Install them using:
```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/automated-inventory-processor.git
   cd automated-inventory-processor
   ```

2. Create the required folders:
   ```bash
   mkdir raw_files processed_data
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run ap.py
   ```

2. Upload Excel files to the `raw_files` folder.

3. The app will:
   - Process the uploaded file.
   - Preprocess the data and generate an Excel output in the `processed_data` folder.
   - Retrieve and save images for departments and items.

4. View the status and results in the Streamlit interface.

## Customization

- **Image Search**: Modify the `search_image` function to use a different search API or logic.
- **Preprocessing Logic**: Update the `preprocess_item_name` function to suit your data formatting needs.
- **Folder Names**: Change `RAW_FILES_FOLDER` and `OUTPUT_FOLDER` constants as needed.

## Notes
- Ensure an active internet connection for image search functionality.
- Placeholder images will be created if the app cannot find relevant images.

## Limitations
- Limited to `.xlsx` files for input data.
- Image search depends on Google, which may return limited results or fail under network issues.
- The app processes one file at a time in a loop with a delay of 10 seconds.

## Future Enhancements
- Add support for more file types.
- Integrate advanced image search APIs.
- Implement batch processing for multiple files simultaneously.

## License
This project is licensed under the MIT License.

--- 
