import cv2
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, flash
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
INPUT_FOLDER = "downloaded_images"
OUTPUT_FOLDER = "cleaned_images"
STATIC_FOLDER = "static"

for folder in [INPUT_FOLDER, OUTPUT_FOLDER, STATIC_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def download_images(url):
    """Download images from a webpage."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []

        for img_tag in soup.find_all("img"):
            img_url = img_tag.get("src") or img_tag.get("data-src")
            if not img_url:
                continue
            
            img_url = urljoin(url, img_url)
            filename = os.path.basename(img_url).split('?')[0]
            filepath = os.path.join(INPUT_FOLDER, filename)

            try:
                img_response = requests.get(img_url, headers=headers, timeout=15)
                img_response.raise_for_status()
                
                with open(filepath, "wb") as f:
                    f.write(img_response.content)
                images.append((filepath, img_url))
            except Exception as e:
                print(f"Error downloading {img_url}: {e}")

        return images, soup, response.text
    except Exception as e:
        print(f"Error processing URL: {e}")
        return [], None, None

def remove_watermark(input_path, output_path):
    """
    Remove watermark using proven techniques that preserve image quality.
    Based on research papers and proven implementations.
    """
    try:
        # Read the image
        image = cv2.imread(input_path)
        if image is None:
            return False

        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create a background model
        background = gray.copy()
        
        # Apply carefully tuned morphological operations
        for i in range(3):  # Reduced iterations for less distortion
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * i + 1, 2 * i + 1))
            background = cv2.morphologyEx(background, cv2.MORPH_CLOSE, kernel)
        
        # Calculate the difference
        diff = cv2.subtract(background, gray)
        
        # Apply adaptive thresholding
        binary_mask = cv2.adaptiveThreshold(
            diff,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )
        
        # Refined mask processing
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        
        # Apply inpainting with minimal radius
        result = cv2.inpaint(image, binary_mask, 3, cv2.INPAINT_NS)
        
        # Save with optimal quality
        cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
        return True

    except Exception as e:
        print(f"Error processing image: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    url = request.form.get('url', '').strip()
    if not url:
        flash('Please enter a URL')
        return redirect(url_for('home'))

    # Download images
    images, soup, original_html = download_images(url)
    if not images:
        flash('No images found')
        return redirect(url_for('home'))

    # Process each image
    image_mapping = {}
    for img_path, img_url in images:
        output_filename = os.path.basename(img_path)
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        static_path = os.path.join(STATIC_FOLDER, output_filename)

        if remove_watermark(img_path, output_path):
            if os.path.exists(static_path):
                os.remove(static_path)
            os.replace(output_path, static_path)
            image_mapping[img_url] = f"/static/{output_filename}"

    if not image_mapping:
        flash('Failed to process images')
        return redirect(url_for('home'))

    # Create new soup from original HTML
    new_soup = BeautifulSoup(original_html, 'html.parser')
    
    # Update image sources
    for img_tag in new_soup.find_all("img"):
        src = img_tag.get("src")
        if src in image_mapping:
            img_tag["src"] = image_mapping[src]

    # Save processed page
    cleaned_html_path = os.path.join(STATIC_FOLDER, "cleaned_page.html")
    with open(cleaned_html_path, "w", encoding="utf-8") as f:
        f.write(str(new_soup))

    return redirect('/static/cleaned_page.html')

if __name__ == '__main__':
    app.run(debug=True)
