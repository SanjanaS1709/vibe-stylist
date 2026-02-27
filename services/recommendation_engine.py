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

    def _get_real_image(self, query):
        """
        Attempts to fetch a real product image from Myntra for high-quality visuals.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        try:
            # We search specifically for female apparel
            search_url = f"https://www.myntra.com/{query.replace(' ', '-')}"
            response = requests.get(search_url, headers=headers, timeout=5)
            if response.status_code == 200:
                # Optimized regex to find Myntra product images in the raw HTML
                import re
                images = re.findall(r'https://assets\.myntassets\.com/h_[^"\']+\.jpg', response.text)
                if images:
                    # Return the first high-quality product image found
                    return images[0]
        except:
            pass
        return None

    def get_category_suggestions(self, user_id, category, vibe, sourcing, filters=None):
        """
        Generates 5-6 items for a specific category to let user select favorites.
        Extremely strict on Vibe and Gender (Female).
        """
        import requests # Ensuring requests is available
        filters = filters or {}
        CAT_MAP = {
            "top": ["top", "shirt", "kurti", "kurta", "saree", "dress", "suit", "blouse", "tops", "shirts", "kurtis", "kurtas", "sarees", "dresses", "suits", "blouses"],
            "pant": ["pant", "trouser", "jeans", "bottom", "trousers", "pants", "denim", "leggings", "skirt", "skirts", "shorts", "bottoms"],
            "shoes": ["shoes", "sneakers", "boots", "footwear", "heels", "sandals", "slipper", "slippers"],
            "accessory": ["accessory", "jewellery", "bag", "jewelry", "belt", "scarf", "accessories", "jewelries", "bags", "belts", "scarves"]
        }
        
        wardrobe = wardrobe_service.get_user_wardrobe(user_id)
        target_cat = category.lower()
        allowed_types = CAT_MAP.get(target_cat, [target_cat, target_cat + 's'])
        
        # Filter by category
        cat_wardrobe = [item for item in wardrobe if item['item_type'].lower() in allowed_types]
        
        # ELITE VIBE FILTERING: 
        # Only suggest wardrobe items if they are tagged with the specific vibe or a related keyword
        relevant_wardrobe = []
        if vibe and vibe != 'General':
            vibe_keywords = [vibe.lower(), vibe.lower().replace(' ', '')]
            # Map vibes to broader overlapping styles (e.g. CLEAN GIRL -> Minimalist)
            VIBE_RELAX = {
                "CLEAN GIRL": ["minimalist", "basic", "white", "beige", "sleek"],
                "SOFT GIRL": ["pastel", "pink", "cute", "floral"],
                "BADDIE": ["edgy", "black", "tight", "bold"],
                "ETHNIC": ["desi", "kurta", "kurti", "saree", "traditional"],
                "OLD MONEY": ["classic", "luxury", "blazer", "formal"]
            }
            rel_keys = VIBE_RELAX.get(vibe.upper(), [])
            
            for it in cat_wardrobe:
                tag = it.get('style_tag', '').lower()
                typ = it.get('item_type', '').lower()
                desc = f"{tag} {typ}"
                if any(k in desc for k in vibe_keywords) or any(k in desc for k in rel_keys):
                    relevant_wardrobe.append(it)
        else:
            relevant_wardrobe = cat_wardrobe

        # Apply color filter
        if filters.get('color'):
            relevant_wardrobe = [it for it in relevant_wardrobe if filters['color'].lower() in it['dominant_color'].lower()]

        if sourcing == 'wardrobe':
            if not relevant_wardrobe: return []
            return [{
                "name": f"{item['dominant_color']} {item['item_type']}",
                "source": "wardrobe",
                "item_id": item['id'],
                "color": item['dominant_color'],
                "style_tag": item['style_tag'],
                "image_url": item['image_url'],
                "price": "Owned",
                "size": "My Size"
            } for item in relevant_wardrobe[:10]]
            
        from services.image_search_service import image_search_service

        prompt = f"""
        Suggest 6 elite FEMALE '{category}' items for a user with a '{vibe}' aesthetic.
        
        STRICT RULES:
        1. NO MALE CLOTHING. Only female-only apparel.
        2. Match the '{vibe}' theme exactly.
        3. REALISTIC PRICING: Provide estimated prices consistent with the Indian market (Myntra/Amazon India). 
           - Tops: ₹499 - ₹2499, Kurtas: ₹799 - ₹3999, Jeans: ₹999 - ₹3499
           - Footwear: ₹799 - ₹4999, Accessories: ₹299 - ₹1999
        4. DESCRIPTION: Provide a 1-sentence stylish description for each item.
        
        Filters: Max Budget: {filters.get('budget', 'Any')}, Color: {filters.get('color', 'Any')}, Size: {filters.get('size', 'Any')}
        Vibe-Relevant Wardrobe: {json.dumps(relevant_wardrobe[:3])}
        
        Respond ONLY with a JSON array:
        {{
          "items": [
            {{
              "name": "(creative, specific name)",
              "description": "(1-sentence description)",
              "source": "wardrobe" or "ecommerce",
              "item_id": (UUID),
              "color": "(precise color)",
              "style_tag": "{vibe}",
              "price": "(Estimated REALISTIC Price in INR)",
              "size": "{filters.get('size', 'M')}",
              "image_query": "(3-word Myntra search query, e.g. 'maroon embroidered kurta')"
            }}
          ]
        }}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"You are a professional female fashion stylist for {vibe} aesthetic."}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content)
            items = data.get('items', [])

            # Force inject wardrobe if hybrid and AI missed it
            if sourcing == 'hybrid' and relevant_wardrobe:
                picked_wardrobe = [it.get('item_id') for it in items if str(it.get('source', '')).lower() == 'wardrobe']
                if not picked_wardrobe:
                    for i in range(min(2, len(relevant_wardrobe))):
                        w = relevant_wardrobe[i]
                        items.insert(0, {"name": f"{w['dominant_color']} {w['item_type']}", "source": "wardrobe", "item_id": w['id'], "color": w['dominant_color'], "style_tag": w['style_tag'], "image_url": w['image_url'], "price": "Owned", "size": "My Size"})
                    items = items[:6]

            for item in items:
                src_val = str(item.get('source', '')).lower()
                item['source'] = src_val

                if src_val == 'ecommerce':
                    # USER PROVIDED PLACEHOLDER: Using the local project asset
                    item['image_url'] = "/statics/images/place_holder.jpg"
                    
                    shop = ecommerce_service.generate_product_suggestion(category, item.get('name', ''), item.get('color', ''), item.get('style_tag', ''))
                    item.update({"amazon": shop['amazon_link'], "myntra": shop['myntra_link'], "flipkart": shop['flipkart_link']})
                elif src_val == 'wardrobe' and not item.get('image_url'):
                    match = next((w for w in cat_wardrobe if w['id'] == item.get('item_id')), None)
                    if match: item['image_url'] = match['image_url']

            return items
        except Exception as e:
            print(f"Error in recommendation logic: {e}")
            return []

recommendation_engine = RecommendationEngine()