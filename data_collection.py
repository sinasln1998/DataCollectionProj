import requests
import pandas as pd
import logging
import yaml
import os
folder_name = 'Outputs'

# Create a directory if it doesn't already exist for the outputs
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"Directory '{folder_name}' created.")
else:
    print(f"Directory '{folder_name}' already exists.")
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch data from USDA ERS data source
def fetch_usda_ers_data(url, api_key, params):
    try:
        params['api_key'] = api_key
        response = requests.get(url, params=params)
        response.raise_for_status()  
        data = response.json()
        # Here I had to check the data format
        if 'data' in data and isinstance(data['data'], list):
            df = pd.json_normalize(data['data'])  
            return df
        else:
            logging.warning(f"No data found in {url} response.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return pd.DataFrame()

# Function to fetch data from World Bank data source
def fetch_world_bank_data(url, api_key, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        data = response.json()
        
        if len(data) > 1 and len(data[1]) > 0:
            df = pd.json_normalize(data[1])
            df = df[['country.value', 'date', 'value']]  
            return df
        else:
            logging.warning(f"No data found in {url} response.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return pd.DataFrame()

# Function to save DataFrame to CSV
def save_to_csv(df, filename):
    output_path = os.path.join(folder_name, filename)  
    if not df.empty:
        try:
            df.to_csv(output_path, index=False)
            logging.info(f"Data saved to {output_path}")
        except Exception as e:
            logging.error(f"Error saving data to {output_path}: {e}")
    else:
        logging.warning("No data to save.")

# Main function to do the data collection
def main():
    # Load configuration from config.yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Iterate through each data source and fetch data
    for source, info in config['data_sources'].items():
        logging.info(f"Fetching data from {source}...")
        fetch_function = globals().get(info['fetch_function'])  
        if fetch_function:
            data = fetch_function(info['url'], info.get('api_key'), info.get('params', {}))
            filename = f"{source}_data.csv"  
            save_to_csv(data, filename)
        else:
            logging.error(f"Fetch function {info['fetch_function']} not found for {source}")

if __name__ == "__main__":
    main()
