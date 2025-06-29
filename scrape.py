import os
import time
import requests
import concurrent.futures
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def download_image(args):
    """Download an image from URL to the specified folder"""
    url, folder_path, filename = args
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    
    attempt = 0
    while True:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return f"Downloaded: {filename}"
            elif response.status_code == 429:
                wait_time = random.uniform(10, 30) + (attempt * random.uniform(5, 15))
                print(f"Rate limited, waiting {wait_time:.1f}s for {filename}")
                time.sleep(wait_time)
                attempt += 1
                continue
            else:
                wait_time = random.uniform(2, 8)
                time.sleep(wait_time)
                attempt += 1
                if attempt > 10:
                    return f"Failed to download: {url} (Status code: {response.status_code})"
                continue
        except Exception as e:
            wait_time = random.uniform(3, 10)
            time.sleep(wait_time)
            attempt += 1
            if attempt > 10:
                return f"Error downloading {url}: {str(e)}"

def scrape_flickr_album(album_url, output_folder="downloaded_images", max_workers=10):
    """Scrape all images from a Flickr album"""
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the album URL
        print(f"Navigating to {album_url}")
        driver.get(album_url)
        
        # Wait for the page to load
        time.sleep(5)
        
        image_count = 0
        page_num = 1
        has_next_page = True
        
        # Create a thread pool executor
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            while has_next_page:
                print(f"Processing page {page_num}...")
                
                # Scroll down to load all images on current page
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    # Scroll down
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Wait for new images to load
                    time.sleep(2)
                    
                    # Calculate new scroll height and compare with last scroll height
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    print("Scrolling to load more images...")
                
                # Find all image elements on current page
                images = driver.find_elements(By.CSS_SELECTOR, "div.photo img")
                
                print(f"Found {len(images)} images on page {page_num}")
                
                # Prepare download tasks
                download_tasks = []
                for i, img in enumerate(images):
                    img_url = img.get_attribute("src")
                    
                    # Convert thumbnail URL to larger version if needed
                    img_url = img_url.replace("_c.jpg", "_b.jpg").replace("_z.jpg", "_b.jpg")
                    
                    # Extract filename from URL or use index
                    filename = f"flickr_image_{image_count + i + 1}.jpg"
                    
                    # Add to download tasks
                    download_tasks.append((img_url, output_folder, filename))
                
                # Submit all download tasks to the thread pool
                futures = [executor.submit(download_image, task) for task in download_tasks]
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    print(future.result())
                
                image_count += len(images)
                
                # Try to find and click the "Next" button
                try:
                    # Look for the next button using the correct selector
                    next_button = driver.find_element(By.CSS_SELECTOR, "i.page-arrow.right")
                    
                    if next_button and next_button.is_displayed():
                        print("Clicking 'Next' button...")
                        next_button.click()
                        time.sleep(5)  # Wait for the next page to load
                        page_num += 1
                    else:
                        print("Next button not visible. Reached the last page.")
                        has_next_page = False
                except NoSuchElementException:
                    print("No 'Next' button found. Reached the last page.")
                    has_next_page = False
        
        print(f"All images downloaded to {output_folder} folder. Total: {image_count} images.")
            
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    # Replace with your Flickr album URL
    album_url = input("Enter the Flickr album URL: ")
    output_folder = input("Enter output folder name (default: downloaded_images): ") or "downloaded_images"
    max_workers = input("Enter maximum number of download threads (default: 10): ")
    max_workers = int(max_workers) if max_workers.isdigit() else 10
    
    scrape_flickr_album(album_url, output_folder, max_workers)