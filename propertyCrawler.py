import requests
import tkinter as tk
from tkinter import ttk, scrolledtext
import pandas as pd




def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def on_fetch():
    base_url = 'https://api.gathern.co/v1/web/filter/map'
    check_in = check_in_entry.get()
    check_out = check_out_entry.get()
    latitude = lat_entry.get()
    longitude = lng_entry.get()
    total_rooms = total_rooms_entry.get()
    total_single_beds = total_single_beds_entry.get()
    total_master_beds = total_master_beds_entry.get()
    toilet_count = toilet_count_entry.get()
    
    params = {
        'prices[]': '0-4000+',
        'chalet_cats[]': 6,
        'city': 3,
        'total_rooms': total_rooms,
        'total_single_beds': total_single_beds,
        'total_master_beds': total_master_beds,
        'toilet_count': toilet_count,
        'has_offer': '',
        'has_no_insuranse': '',
        'has_available': '',
        'lat': latitude,
        'lng': longitude,
        'range': 30,
        'check_in': check_in,
        'check_out': check_out
    }
    full_url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in params.items() if value])}"
    response = fetch_url(full_url)
    
    if isinstance(response, str):
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, response)
        return
    
    items = response.get('items', [])
    if items:
        processed_items = []
        for item in items:
            features = item.pop('features', [])
            for idx, feature in enumerate(features):
                item[f'feature_{idx}'] = feature
            processed_items.append(item)
        
        df = pd.DataFrame(processed_items)
        df.to_csv('items_with_features.csv', index=False, encoding='utf-8-sig')
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, f"Data saved to items_with_features.csv with {len(processed_items)} items.")
    else:
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "No items found in the response.")

# Create the main window
root = tk.Tk()
root.title("URL Fetcher")

# Create and place the labels and entry widgets for check-in and check-out dates
ttk.Label(root, text="Check-in Date (YYYY-MM-DD):").grid(column=0, row=0, padx=10, pady=5)
check_in_entry = ttk.Entry(root)
check_in_entry.grid(column=1, row=0, padx=10, pady=5)

ttk.Label(root, text="Check-out Date (YYYY-MM-DD):").grid(column=0, row=1, padx=10, pady=5)
check_out_entry = ttk.Entry(root)
check_out_entry.grid(column=1, row=1, padx=10, pady=5)

# Create and place the labels and entry widgets for latitude and longitude
ttk.Label(root, text="Latitude:").grid(column=0, row=2, padx=10, pady=5)
lat_entry = ttk.Entry(root)
lat_entry.grid(column=1, row=2, padx=10, pady=5)

ttk.Label(root, text="Longitude:").grid(column=0, row=3, padx=10, pady=5)
lng_entry = ttk.Entry(root)
lng_entry.grid(column=1, row=3, padx=10, pady=5)

# Create and place the labels and entry widgets for total rooms, single beds, master beds, and toilet count
ttk.Label(root, text="Total Rooms (leave empty if not specified):").grid(column=0, row=4, padx=10, pady=5)
total_rooms_entry = ttk.Entry(root)
total_rooms_entry.grid(column=1, row=4, padx=10, pady=5)

ttk.Label(root, text="Total Single Beds (leave empty if not specified):").grid(column=0, row=5, padx=10, pady=5)
total_single_beds_entry = ttk.Entry(root)
total_single_beds_entry.grid(column=1, row=5, padx=10, pady=5)

ttk.Label(root, text="Total Master Beds (leave empty if not specified):").grid(column=0, row=6, padx=10, pady=5)
total_master_beds_entry = ttk.Entry(root)
total_master_beds_entry.grid(column=1, row=6, padx=10, pady=5)

ttk.Label(root, text="Toilet Count (leave empty if not specified):").grid(column=0, row=7, padx=10, pady=5)
toilet_count_entry = ttk.Entry(root)
toilet_count_entry.grid(column=1, row=7, padx=10, pady=5)

# Create and place the fetch button
fetch_button = ttk.Button(root, text="Fetch URL", command=on_fetch)
fetch_button.grid(column=0, row=8, columnspan=2, padx=10, pady=10)

# Create and place the text area to display the fetched content
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
text_area.grid(column=0, row=9, columnspan=2, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
