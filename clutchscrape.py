import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import timedelta

# Base URL for vehicle listings
BASE_URL = "https://www.clutch.ca/vehicles/"

# Function to extract data from a single vehicle page
def extract_vehicle_data(vehicle_id):
    vehicle_url = f"{BASE_URL}{vehicle_id}"
    print(f"Testing URL: {vehicle_url}")  # Log the URL being tested

    response = requests.get(vehicle_url)
    
    if response.status_code != 200:
        return None  # Skip if the page doesn't load properly

    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Extract Year, Make, Model, and Trim
        title = soup.select_one('h1.vehicle-details__title').text.strip()
        year, make, model = title.split(" ", 2)
        
        trim_element = soup.find('span', text='Trim:')
        trim = trim_element.find_next('span').text.strip() if trim_element else "N/A"
        
        # Extract VIN
        vin_element = soup.find('span', text='VIN:')
        vin = vin_element.find_next('span').text.strip() if vin_element else "N/A"

        print(f"Found vehicle: {year} {make} {model}, Trim: {trim}, VIN: {vin}")  # Log the found data

        return {
            "Year": year,
            "Make": make,
            "Model": model,
            "Trim": trim,
            "VIN": vin,
            "URL": vehicle_url
        }
    except Exception as e:
        print(f"Error extracting data for vehicle ID {vehicle_id}: {e}")
        return None

# Function to scrape data for a range of vehicle IDs
def scrape_clutch_data(start_id, end_id, output_file):
    total_ids = end_id - start_id + 1
    processed_count = 0
    start_time = time.time()

    # Initialize the CSV file with headers if it doesn't exist
    try:
        open(output_file, 'x').write("Year,Make,Model,Trim,VIN,URL\n")
    except FileExistsError:
        pass  # File already exists, so we'll just append to it

    for vehicle_id in range(start_id, end_id + 1):
        data = extract_vehicle_data(vehicle_id)
        if data:
            # Append data to the CSV file
            with open(output_file, 'a') as f:
                f.write(f'{data["Year"]},{data["Make"]},{data["Model"]},{data["Trim"]},{data["VIN"]},{data["URL"]}\n')
        
        processed_count += 1
        remaining = total_ids - processed_count
        elapsed_time = time.time() - start_time
        estimated_time_remaining = elapsed_time / processed_count * remaining if processed_count > 0 else 0

        print(f"Processed: {processed_count}/{total_ids} | Remaining: {remaining} | "
              f"Estimated Time Left: {str(timedelta(seconds=int(estimated_time_remaining)))}")
        
        time.sleep(5)  # Wait 5 seconds between requests to avoid triggering bans

# Main entry point
if __name__ == "__main__":
    print("Welcome to the Clutch.ca Web Scraper!")
    start_id = int(input("Enter the starting vehicle ID: "))
    end_id = int(input("Enter the ending vehicle ID: "))
    output_file = "clutch_vehicle_listings.csv"

    print(f"Starting scraper from ID {start_id} to {end_id}. Results will be saved to {output_file}.")
    scrape_clutch_data(start_id, end_id, output_file)
    print("Scraping complete!")
