import cv2
import numpy as np
from PIL import Image
import os

def analyze_skin_tone(image_path):
    """
    Detects face, extracts cheek/face region, and classifies skin tone based on RGB values.
    Returns: classification (Warm, Cool, Neutral, Deep) or None if no face detected.
    """
    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return "No face detected"
        
        # Take the first face detected
        (x, y, w, h) = faces[0]
        
        # Extract a region of interest (ROI) - usually around the center of the face/cheeks
        # We'll take a small patch in the middle of the lower half of the face discovery
        roi_x = x + int(w * 0.25)
        roi_y = y + int(h * 0.35)
        roi_w = int(w * 0.5)
        roi_h = int(h * 0.3)
        
        roi = img[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        
        # Compute average RGB values
        # OpenCV uses BGR, so we reverse it
        avg_bgr = cv2.mean(roi)[:3]
        avg_rgb = (avg_bgr[2], avg_bgr[1], avg_bgr[0])
        
        r, g, b = avg_rgb
        
        # Simple rule-based classification
        # Note: These are simplified thresholds for demonstration as requested
        
        # Convert to HSL for better tone analysis if needed, but rule-based RGB dominance was requested
        
        # Warm: R > G and G > B (Yellow/Golden undertones)
        # Cool: B is relatively higher or R is close to B (Pink/Blue undertones)
        # Deep: Low overall brightness
        # Neutral: Balanced RGB
        
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        
        if luma < 80:
            return "Deep & Mysterious (Autumn/Winter Palette)"
        
        if abs(r - g) < 10 and abs(g - b) < 10:
            return "Earthly Neutral (Universal Palette)"
            
        if r > g and g > b:
            return "Radiant Warm (Spring/Summer Palette)"
        
        if b > g or abs(r - b) < 15:
            return "Vibrant Cool (Winter Palette)"
            
        return "Balanced Neutral"

    except Exception as e:
        print(f"Error in skin analysis: {e}")
        return None
