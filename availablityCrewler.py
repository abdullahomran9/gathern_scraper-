import requests
import time
import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from bs4 import BeautifulSoup
import json
from datetime import datetime


def load_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path)
            populate_table(df)
            global loaded_df
            loaded_df = df
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

def populate_table(df):
    for row in table.get_children():
        table.delete(row)
    for _, row in df.iterrows():
        table.insert("", tk.END, values=list(row))

def construct_and_check_urls():
    check_in = check_in_entry.get()
    check_out = check_out_entry.get()
    if not check_in or not check_out:
        messagebox.showerror("Error", "Please enter both check-in and check-out dates.")
        return

    results = []
    text_area.delete(1.0, tk.END)  # Clear the text area at the start
    for index, row in loaded_df.iterrows():
        chalet_id = row['chalet_id']  # Assuming chalet_id is a column in the CSV
        unit_id = row['id']  # Assuming id is a column in the CSV
        url = f"https://gathern.co/view/{chalet_id}/unit/{unit_id}?check_in={check_in}&check_out={check_out}"

        response = fetch_url(url)
        if isinstance(response, dict):
            is_available = response.get('isUnitAvailable', 'N/A')
        else:
            print(f"Unexpected response for URL {url}: {response}")
            is_available = 'N/A'
        results.append({'chalet_id': chalet_id, 'unit_id': unit_id, 'isUnitAvailable': is_available})

        # Update progress in the text area after every 10 URLs
        if (index + 1) % 10 == 0:
            text_area.insert(tk.END, f"Processed {index + 1} URLs...\n")
            text_area.see(tk.END)  # Scroll to the end

        time.sleep(3)  # Wait for 3 seconds between requests

    result_df = pd.DataFrame(results)
    date_str = datetime.now().strftime('%Y-%m-%d')
    result_filename = f'unit_availability_{date_str}.csv'
    result_df.to_csv(result_filename, index=False, encoding='utf-8-sig')
    text_area.insert(tk.END, f"Results saved to {result_filename}.\n{result_df}")

def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        if script_tag:
            json_data = json.loads(script_tag.string)
            if 'props' in json_data and 'pageProps' in json_data['props'] and 'serverData' in json_data['props']['pageProps']:
                return json_data['props']['pageProps']['serverData']['data']
        return f"Invalid JSON response: {response.text}"
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for URL {url}: {http_err} - Response: {response.text}")
        return f"HTTP error: {http_err}"
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred for URL {url}: {req_err}")
        return f"Request error: {req_err}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

def start_url_check():
    threading.Thread(target=construct_and_check_urls).start()

# Create the main window
root = tk.Tk()
root.title("CSV URL Constructor and Checker")

# Create and place the button to load CSV
load_button = ttk.Button(root, text="Load CSV", command=load_csv)
load_button.grid(column=0, row=0, padx=10, pady=5)

# Create and place the table to display CSV data
table = ttk.Treeview(root, columns=("ID", "Chalet ID", "Other Columns"), show="headings")
table.heading("ID", text="ID")
table.heading("Chalet ID", text="Chalet ID")
table.heading("Other Columns", text="Other Columns")
table.grid(column=0, row=1, columnspan=2, padx=10, pady=5)

# Create and place the labels and entry widgets for check-in and check-out dates
ttk.Label(root, text="Check-in Date (YYYY-MM-DD):").grid(column=0, row=2, padx=10, pady=5)
check_in_entry = ttk.Entry(root)
check_in_entry.grid(column=1, row=2, padx=10, pady=5)

ttk.Label(root, text="Check-out Date (YYYY-MM-DD):").grid(column=0, row=3, padx=10, pady=5)
check_out_entry = ttk.Entry(root)
check_out_entry.grid(column=1, row=3, padx=10, pady=5)

# Create and place the button to construct URLs and check availability
construct_check_button = ttk.Button(root, text="Construct and Check URLs", command=start_url_check)
construct_check_button.grid(column=0, row=4, columnspan=2, padx=10, pady=10)

# Create and place the text area to display the results
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
text_area.grid(column=0, row=5, columnspan=2, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
