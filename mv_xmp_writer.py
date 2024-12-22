from modules.mediavalet_auth import get_access_token
import requests
import os
import subprocess

# Set these global variables
EXIF_TOOL_LOCATION = r"C:\Tools\exiftool.exe" # Change to the location of exiftool on your system
SUBSCRIPTION_KEY = "your_subscription_key" # Replace with your MediaValet subscription key

# Function to get asset attributes
def get_attributes(access_token):
    """
    Fetches asset attributes from the MediaValet API.
    
    Parameters:
        access_token (str): The access token for MediaValet API authentication.
    
    Returns:
        dict: A dictionary where keys are attribute IDs and values are attribute names.
    """
    url = "https://api.mediavalet.com/attributes"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "x-mv-api-version": "1.1",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
      
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        attributes = response.json()
        # Filter attributes to include only those with isSystemProperty=False
        attribute_dict = {
            attr["id"]: attr["name"]
            for attr in attributes.get("payload", [])
            if not attr.get("isSystemProperty", False)  # Default to False if the key is missing
        }
        return attribute_dict
    else:
        print(f"Failed to retrieve attributes. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return {}

def get_assets_in_category(access_token, attribute_dict):
    """
    Fetches assets within a specific category and its subcategories.

    Parameters:
        access_token (str): The access token for MediaValet API authentication.
        attribute_dict (str): Dictionary of attributes from MediaValet library.

    Returns:
        dict: JSON response containing the assets.
    """
    category_id = str(input("Enter MediaValet Category ID: "))

    url = f"https://api.mediavalet.com/assets?containerFilter=(CategoryIds/ANY(c: c EQ '{category_id}') OR CategoryAncestorIds/ANY(c: c EQ '{category_id}'))"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "x-mv-api-version": "1.1",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        assets_data = response.json()

        # Initialize a dictionary to store file names and their attributes
        assets_dict = {}
        
        # Extract file names and attributes
        for asset in assets_data.get("payload", {}).get("assets", []):
            file_name = asset.get("file", {}).get("fileName")
            attributes = asset.get("attributes", {})
            if file_name:
                 # Filter attributes to include only those with IDs in attribute_dict
                filtered_attributes = {
                    attr_id: attr_value
                    for attr_id, attr_value in attributes.items()
                    if attr_id in attribute_dict
                }

                # Convert filtered attribute IDs to attribute names
                named_attributes = {
                    attribute_dict[attr_id]: attr_value
                    for attr_id, attr_value in filtered_attributes.items()
                }

                # Add the asset to the dictionary
                assets_dict[file_name] = named_attributes
        return assets_dict
    else:
        print(f"Failed to retrieve assets. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return {}

def write_metadata_to_file(file_path, assets_dict, config_file_path="ExifTool_config"):
    """
    Writes metadata to a file using ExifTool.

    Parameters:
        file_path (str): Path to the file.
        assets_dict (dict): Dictionary where keys are file names and values are metadata dictionaries.
        config_file_path (str): Path to the ExifTool configuration file.
    """
    # Ensure the config file path is absolute
    config_file_path = os.path.abspath(config_file_path)

    # Extract the file name from the file path
    file_name = os.path.basename(file_path)

    # Check if the file name exists in assets_dict
    if file_name not in assets_dict:
        print(f"No metadata found for file: {file_name}")
        return

    # Retrieve metadata for the file
    metadata = assets_dict[file_name]

    # Construct the ExifTool command
    command = [
        EXIF_TOOL_LOCATION,
        "-config",
        f'{config_file_path}',
        "-overwrite_original",
    ]
    for key, value in metadata.items():
        # Format the key to include the custom namespace
        xmp_key = f"XMP-mv:{key.replace(' ', '')}"  # mv is the custom namespace prefix
        xmp_value = f'{str(value)}'
        command.append(f"-{xmp_key}={xmp_value}")
    command.append(f'{file_path}')

    # Print the constructed command
    #print("Executing command:", " ".join(command))

    try:
        # Execute the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check for errors
        if result.returncode != 0:
            raise Exception(f"ExifTool error: {result.stderr}")

        print(f"Metadata written to {file_name}")
    except Exception as e:
        print(f"Failed to write metadata to {file_name}. Error: {e}")

def generate_exiftool_config(attribute_dict, config_file_path="ExifTool_config"):
    """
    Generates an ExifTool configuration file to define a custom XMP namespace 'mv'
    with writable tags based on the provided attribute dictionary.

    Parameters:
        attribute_dict (dict): A dictionary where keys are attribute IDs, and values are attribute names.
        config_file_path (str): The file path where the ExifTool configuration will be written.
    """
    # Define the namespace prefix and URI
    namespace_prefix = "mv"
    namespace_uri = "http://my.custom.namespace/"

    # Initialize the configuration content
    config_content = [
        f"%Image::ExifTool::UserDefined::{namespace_prefix} = (",
        "    GROUPS        => { 0 => 'XMP', 1 => 'XMP-mv', 2 => 'Image' },",
        f"    NAMESPACE     => {{ '{namespace_prefix}' => '{namespace_uri}' }},",
        "    WRITABLE      => 'string',",
    ]

    # Add each attribute as a tag
    for _, attribute_name in attribute_dict.items():
        sanitized_name = attribute_name.replace(" ", "")
        config_content.append(f"    {sanitized_name} => {{ }},")  # Minimal tag definition

    # Close the namespace definition
    config_content.append(");")
    config_content.append("")
    
    # Link the namespace to XMP::Main
    config_content.extend([
        "%Image::ExifTool::UserDefined = (",
        "    'Image::ExifTool::XMP::Main' => {",
        f"        {namespace_prefix} => {{",
        "            SubDirectory => {",
        f"                TagTable => 'Image::ExifTool::UserDefined::{namespace_prefix}',",
        "            },",
        "        },",
        "    },",
        ");",
        "",
        "#------------------------------------------------------------------------------",
        "1;  #end",
    ])

    # Write the content to the specified file
    with open(config_file_path, "w") as config_file:
        config_file.write("\n".join(config_content))

    print(f"ExifTool configuration file successfully written to: {os.path.abspath(config_file_path)}")

def process_folder_with_metadata(assets_dict, attribute_dict):
    """
    Processes all files in a folder:
    - Generates an ExifTool config file based on the attribute dictionary.
    - Iterates over files in the folder and writes metadata to each file.

    Parameters:
        folder_path (str): The folder containing the files to process.
        assets_dict (dict): Dictionary where keys are file names and values are metadata dictionaries.
        attribute_dict (dict): Dictionary of attribute IDs and names to define the ExifTool config file.
    """
    # Generate the ExifTool config file
    config_file_path = "ExifTool_config"
    generate_exiftool_config(attribute_dict, config_file_path)
    print("ExifTool configuration file generated.")

    folder_path = input("Enter Local Folder Path: ").strip('"').strip("'")

    # Ensure the folder path exists
    if not os.path.isdir(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    # Iterate over the files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Skip directories, process only files
        if os.path.isfile(file_path):
            print(f"Processing file: {file_name}")
            write_metadata_to_file(file_path, assets_dict, config_file_path)

    print("All files in the folder have been processed.")


# Retrieve MV access token
token = get_access_token()
    
# Fetch the library's custom attributes
attributes = get_attributes(token)

# Get Assets + Metadata dictionaries in category
mv_assets = get_assets_in_category(token, attributes)

# Write custom attributes to local files as XMP metadata (with 'mv' as custom namespace)
process_folder_with_metadata(mv_assets, attributes)

