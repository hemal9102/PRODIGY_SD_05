import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import tkinter as tk
from tkinter import filedialog, messagebox


def random_user_agent():
    """
    Generates a random user agent to mimic a real user browsing the web.
    """
    ua = UserAgent()
    return ua.random


def setup_driver():
    """
    Sets up a headless Selenium WebDriver with random user agent and necessary options.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument(f"user-agent={random_user_agent()}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)


def auto_detect_selectors(soup):
    """
    Automatically detects and extracts product names, prices, and ratings from the page.
    """
    # Selectors to capture various possible elements for product names, prices, and ratings
    name_selectors = ['span', 'h2', 'a', 'div']
    price_selectors = ['span', 'div']
    rating_selectors = ['span', 'div', 'p']

    product_names, product_prices, product_ratings = [], [], []

    # Extract product names using common HTML tags
    for tag in name_selectors:
        product_names.extend([item.text.strip() for item in soup.find_all(tag)
                              if 'a-text-normal' in item.attrs.get('class', '') or
                              's-line-clamp' in item.attrs.get('class', '')])

    # Extract product prices using common HTML tags
    for tag in price_selectors:
        product_prices.extend([item.text.strip() for item in soup.find_all(tag)
                               if 'a-price-whole' in item.attrs.get('class', '')])

    # Extract product ratings using common HTML tags
    for tag in rating_selectors:
        product_ratings.extend([item.text.strip() for item in soup.find_all(tag)
                               if 'a-icon-alt' in item.attrs.get('class', '')])

    # Clean up the lists by removing empty or None values
    product_names = list(filter(None, product_names))
    product_prices = list(filter(None, product_prices))
    product_ratings = list(filter(None, product_ratings))

    # Debugging: print the extracted data
    print(f"Product names found: {product_names}")
    print(f"Product prices found: {product_prices}")
    print(f"Product ratings found: {product_ratings}")

    return product_names, product_prices, product_ratings


def scrape_with_selenium(url):
    """
    Scrapes the given URL using Selenium and returns the extracted product names, prices, and ratings.
    """
    driver = setup_driver()
    driver.get(url)

    # Wait for the products to load on the page
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".s-main-slot .s-result-item"))
    )

    time.sleep(random.uniform(5, 8))  # Add a small delay to allow content to settle

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_names, product_prices, product_ratings = auto_detect_selectors(soup)

    driver.quit()  # Close the browser
    return product_names, product_prices, product_ratings


def scrape_and_save():
    """
    Handles the scraping process and saves the data into a CSV file.
    """
    url = entry_url.get()  # Get the URL entered by the user
    output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    # Validate inputs
    if not url or not output_file:
        messagebox.showerror("Error", "Please enter a valid URL and output file name.")
        return

    # Perform the scraping
    product_names, product_prices, product_ratings = scrape_with_selenium(url)

    # Check if data was found
    if not product_names or not product_prices or not product_ratings:
        messagebox.showerror("Error", "No data found on the website.")
        return

    # Ensure all lists have the same length
    max_length = max(len(product_names), len(product_prices), len(product_ratings))
    product_names += [None] * (max_length - len(product_names))
    product_prices += [None] * (max_length - len(product_prices))
    product_ratings += [None] * (max_length - len(product_ratings))

    # Prepare the data for saving
    data = {'Name': product_names, 'Price': product_prices, 'Rating': product_ratings}
    df = pd.DataFrame(data)

    # Check if DataFrame has data
    if df.empty:
        messagebox.showerror("Error", "No data to save.")
        return

    # Save data to CSV
    df.to_csv(output_file, index=False)
    messagebox.showinfo("Success", f"Data saved to {output_file}")


# GUI Application
root = tk.Tk()
root.title("Universal Web Scraper")
root.geometry("500x300")

# URL input field
label_url = tk.Label(root, text="Enter the e-commerce website URL:")
label_url.pack(pady=10)

entry_url = tk.Entry(root, width=50)
entry_url.pack(pady=5)

# Scrape and Save button
button_scrape = tk.Button(root, text="Scrape and Save", command=scrape_and_save)
button_scrape.pack(pady=20)

root.mainloop()  # Start the GUI application
