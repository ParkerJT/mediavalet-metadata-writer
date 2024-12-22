
# MediaValet Embedded Metadata Writer

The **MediaValet Embedded Metadata Writer** is a Python-based tool that writes MediaValet custom attributes to your downloaded assets as XMP metadata. This project is ideal for users who want to enhance their asset management workflows by embedding MediaValet metadata directly into files.

## Setup

### Prerequisites
1. **Install Python:**
   - Download and install Python from [python.org](https://www.python.org/downloads/).

2. **Install Required Python Packages:**
   Run the following command to install dependencies:

   pip install requests pwinput

3. **Install EXIFTool:**
   - Download EXIFTool from [ExifTool Official Site](https://exiftool.org/) and install it on your system.

4. **Update Configuration Files:**
   - Open the `mv_xmp_writer.py` file.
     - Update the `EXIF_TOOL_LOCATION` variable (line 7) with the full file path to the EXIFTool executable. Use a raw string format (e.g., `r"C:\path\to\exiftool.exe"`).
     - Update the `SUBSCRIPTION_KEY` variable (line 8) with your MediaValet subscription key.
   - Open the `mediavalet_auth.py` file.
     - Update the `CLIENT_ID` variable (line 6) with your MediaValet client ID.
     - Update the `CLIENT_SECRET` variable (line 7) with your MediaValet client secret.

## How to Use

1. **Prepare Files in MediaValet:**
   - Add all files you want to download to a target category in MediaValet.
   - Note down the **Category ID** for the target category.

2. **Download Files:**
   - Download and extract all files from the category into a local folder.
   - Note down the folder path where the files are saved.

3. **Run the Script:**
   - Open your command-line interface (CLI) of choice.
   - Run the script and provide the following inputs when prompted:
     - MediaValet credentials (username and password)
     - Category ID
     - Folder path containing the downloaded files

## Limitations

1. **File Naming Restrictions:**
   - File names and paths must not contain spaces or special characters. (This might be handled in a future update.)

2. **Supported File Types:**
   - The script can only write metadata to file types supported by EXIFTool.

3. **Custom XMP Namespace:**
   - The script uses a custom XMP namespace. End users may not recognize the schema when viewing metadata in standard tools.

---

Feel free to contribute or report issues to help improve the MediaValet Embedded Metadata Writer!
