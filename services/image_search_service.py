import requests
from bs4 import BeautifulSoup
import re
import random

class ImageSearchService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def fetch_product_image(self, query):
        """
        Attempts to find a real product image from Myntra Search.
        """
        try:
            # Myntra search URL
            search_url = f"https://www.myntra.com/{query.replace(' ', '-')}"
            response = requests.get(search_url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                return None
                
            # Optimized for Myntra's response pattern
            # Myntra images are often in 'https://assets.myntassets.com/h_1440,q_90,w_1080/v1/assets/images/...'
            # We look for large product images
            img_patterns = [
                r'https://assets\.myntassets\.com/[^"\']+\.jpg',
                r'https://assets\.myntassets\.com/h_[^"\']+\.jpg'
            ]
            
            all_images = []
            for pattern in img_patterns:
                all_images.extend(re.findall(pattern, response.text))
            
            # Filter for diverse product shots, ignore logos or tiny icons
            product_images = [img for img in all_images if 'assets' in img and 'v1' in img]
            
            if product_images:
                # Return a random one from the top results for variety
                return random.choice(product_images[:5])
                
            return None
        except Exception as e:
            print(f"Image fetch error: {e}")
            return None

image_search_service = ImageSearchService()
