import os
import json
from groq import Groq
from services.swipe_learning import swipe_learning_service
from services.wardrobe_service import wardrobe_service
from services.ecommerce_service import ecommerce_service
from services.catalog_matcher import catalog_matcher
from supabase_client import supabase

class RecommendationEngine:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)

    def generate_outfit(self, user_id, context=None):
        """
        Generates a complete outfit JSON using Groq AI, 
        adaptive to user preferences, swipe history, and VIRTUAL WARDROBE.
        """
        # Fetch Phase 2 profile data
        user_response = supabase.table('users').select('skin_tone_result').eq('id', user_id).execute()
        skin_tone = user_response.data[0].get('skin_tone_result') if user_response.data else "Neutral"
        
        pref_response = supabase.table('user_preferences').select('*').eq('user_id', user_id).execute()
        prefs = pref_response.data[0] if pref_response.data else {}
        
        # Fetch Phase 3 swipe learning data
        learning = swipe_learning_service.get_user_preferences(user_id)
        
        # Fetch Phase 4 Wardrobe data
        wardrobe = wardrobe_service.get_user_wardrobe(user_id)
        wardrobe_summary = [
            {"id": item['id'], "type": item['item_type'], "color": item['dominant_color'], "tag": item['style_tag']}
            for item in wardrobe
        ]
        
        prompt = f"""
        Generate a hybrid outfit recommendation for a user.
        
        User Context: {context} (Vibe, Gender, Sourcing preference)
        
        Profile Info:
        - Skin Tone: {skin_tone}
        - Archetype: {prefs.get('style_archetype', 'Casual')}
        - Liked History: {learning.get('liked_tags', [])}
        
        User's Virtual Wardrobe:
        {json.dumps(wardrobe_summary)}
        
        Instructions:
        1. If sourcing is 'wardrobe', EXCLUSIVELY use items from the JSON list provided.
        2. If sourcing is 'other', EXCLUSIVELY suggest new items for purchase (set source to 'ecommerce').
        3. If no items in wardrobe for a part, fallback to 'ecommerce'.
        4. For 'ecommerce' items, provide a VERY DETAILED 'description' so buy links can be generated.
        
        Respond ONLY with a JSON object:
        {{
          "top": {{ "source": "wardrobe/ecommerce", "item_id": null, "description": "precise name and color", "color": "...", "style_tag": "..." }},
          "pant": {{ "source": "wardrobe/ecommerce", "item_id": null, "description": "precise name and color", "color": "...", "style_tag": "..." }},
          "shoes": {{ "source": "wardrobe/ecommerce", "item_id": null, "description": "precise name and color", "color": "...", "style_tag": "..." }},
          "accessory": {{ "source": "wardrobe/ecommerce", "item_id": null, "description": "precise name and color", "color": "...", "style_tag": "..." }}
        }}
        
        Rules:
        - item_id MUST be null if source is 'ecommerce'.
        - ONLY use the UUIDs provided in the Virtual Wardrobe list.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a hybrid fashion stylist AI that prioritizes personal wardrobe first and fills gaps with external items."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(completion.choices[0].message.content)
            
        except Exception as e:
            print(f"Error in recommendation engine: {e}")
            return None

    def get_category_suggestions(self, user_id, category, vibe, sourcing):
        """
        Generates 5-6 items for a specific category to let user select favorites.
        Strictly enforces the 'wardrobe' only rule if selected.
        """
        # Broad and inclusive category mapping for robust wardrobe syncing
        CAT_MAP = {
            "top": ["top", "shirt", "kurti", "kurta", "saree", "dress", "suit", "blouse", "tops", "shirts", "kurtis", "kurtas", "sarees", "dresses", "suits", "blouses"],
            "pant": ["pant", "trouser", "jeans", "bottom", "trousers", "pants", "denim", "leggings", "skirt", "skirts", "shorts", "bottoms"],
            "shoes": ["shoes", "sneakers", "boots", "footwear", "heels", "sandals", "slipper", "slippers"],
            "accessory": ["accessory", "jewellery", "bag", "jewelry", "belt", "scarf", "accessories", "jewelries", "bags", "belts", "scarves"]
        }
        
        wardrobe = wardrobe_service.get_user_wardrobe(user_id)
        target_cat = category.lower()
        # Fallback to the category itself if not in map, but use the mapping for broad matching
        allowed_types = CAT_MAP.get(target_cat, [target_cat, target_cat + 's'])
        
        relevant_wardrobe = [item for item in wardrobe if item['item_type'].lower() in allowed_types]
        
        # CORE FIX: If user wants only wardrobe, don't let AI filter them out!
        # Return them directly formatted as the UI expects.
        if sourcing == 'wardrobe':
            if not relevant_wardrobe:
                return []
            
            # Format wardrobe items to match the expected structure
            formatted_wardrobe = []
            for item in relevant_wardrobe[:10]: # Return more options if available
                formatted_wardrobe.append({
                    "name": f"{item['dominant_color']} {item['item_type']}",
                    "source": "wardrobe",
                    "item_id": item['id'],
                    "color": item['dominant_color'],
                    "style_tag": item['style_tag'],
                    "image_url": item['image_url']
                })
            return formatted_wardrobe
            
        # Map categories to search keywords for high-quality fashion images
        image_keywords = {
            "top": "designer shirt luxury blouse couture top",
            "pant": "high-fashion trousers tailored pants aesthetic bottom",
            "shoes": "premium sneakers luxury heels boots high-fashion footwear",
            "accessory": "luxury jewelry high-fashion accessory designer bag"
        }
        keyword = image_keywords.get(category.lower(), "fashion clothing")
        
        prompt = f"""
        Suggest 6 '{category}' items for a '{vibe}' vibe.
        
        Strict Sourcing Preference: {sourcing}
        - If sourcing is 'wardrobe', you MUST ONLY pick items from the 'User's Wardrobe Items' list. DO NOT provide ecommerce suggestions.
        - If sourcing is 'hybrid', you MUST provide a mix of items from the 'User's Wardrobe Items' list AND new 'ecommerce' suggestions that complement them.
        
        User's Wardrobe Items: {json.dumps(relevant_wardrobe)}
        
        Respond with a JSON array of 6 items. Each item must have:
        - name: (detailed name)
        - source: "wardrobe" or "ecommerce"
        - item_id: (UUID if wardrobe, else null)
        - color: (string)
        - style_tag: (string)
        - image_url: (If source is wardrobe, use item's image_url. If source is ecommerce, provide a UNIQUE ID from 100 to 999)
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content)
            items = data.get('items', data.get('suggestions', data.get('options', [])))
            
            # Post-filter to strictly enforce wardrobe injection if AI missed it in hybrid mode
            if sourcing == 'hybrid':
                wardrobe_ids_in_result = [it.get('item_id') for it in items if it.get('source') == 'wardrobe']
                # If AI ignored wardrobe, force include at least 2 if available
                if not wardrobe_ids_in_result and relevant_wardrobe:
                    for i in range(min(2, len(relevant_wardrobe))):
                        w_item = relevant_wardrobe[i]
                        items.insert(0, {
                            "name": f"{w_item['dominant_color']} {w_item['item_type']}",
                            "source": "wardrobe",
                            "item_id": w_item['id'],
                            "color": w_item['dominant_color'],
                            "style_tag": w_item['style_tag'],
                            "image_url": w_item['image_url']
                        })
                    items = items[:6] # Keep it to 6
            
            for item in items:
                if item.get('source') == 'ecommerce':
                    # Use a reliable Unsplash Source URL with keywords and the random ID for uniqueness
                    random_id = item.get('image_url', '123')
                    item['image_url'] = f"https://source.unsplash.com/featured/800x1200?{keyword.replace(' ', ',')}&sig={random_id}"
                    
                    shop = ecommerce_service.generate_product_suggestion(
                        category, item.get('name', ''), item.get('color', ''), item.get('style_tag', '')
                    )
                    item.update({
                        "amazon": shop['amazon_link'],
                        "myntra": shop['myntra_link'],
                        "flipkart": shop['flipkart_link']
                    })
                elif item.get('source') == 'wardrobe' and not item.get('image_url'):
                    # Fallback for wardrobe items if AI missed the image_url
                    match = next((w for w in relevant_wardrobe if w['id'] == item.get('item_id')), None)
                    if match:
                        item['image_url'] = match['image_url']

            return items
        except Exception as e:
            print(f"Error getting category suggestions: {e}")
            return []

recommendation_engine = RecommendationEngine()