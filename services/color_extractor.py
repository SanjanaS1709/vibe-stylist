import cv2
import numpy as np
from PIL import Image

class ColorExtractor:
    def get_dominant_color(self, image_path):
        """
        Extracts the dominant color from an image using k-means clustering.
        Returns a human-readable color name (simple classification).
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return "Unknown"
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.reshape((img.shape[0] * img.shape[1], 3))

            # Use K-Means to find dominant color
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=1, n_init=10)
            kmeans.fit(img)
            
            dominant_rgb = kmeans.cluster_centers_[0].astype(int)
            return self._rgb_to_name(dominant_rgb)
        except Exception as e:
            print(f"Error extracting color: {e}")
            return "Unknown"

    def _rgb_to_name(self, rgb):
        r, g, b = rgb
        # Simple rule-based naming for common colors
        if r > 200 and g > 200 and b > 200: return "White"
        if r < 50 and g < 50 and b < 50: return "Black"
        if r > 150 and g < 100 and b < 100: return "Red"
        if g > 150 and r < 100 and b < 100: return "Green"
        if b > 150 and r < 100 and g < 100: return "Blue"
        if r > 150 and g > 150 and b < 100: return "Yellow"
        if r > 100 and g > 50 and b < 50: return "Brown"
        if abs(r-g) < 20 and abs(g-b) < 20: return "Grey"
        return "Multi"

color_extractor = ColorExtractor()
