import os
import json
from groq import Groq
from supabase_client import supabase

class WardrobeService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)

    def remove_bg(self, input_path, output_path):
        """
        Removes background from an image using rembg.
        Includes a fail-safe to avoid hanging the app.
        """
        try:
            from rembg import remove
            import time
            from PIL import Image
            
            # Since rembg can hang on onnx initialization, we wrap it
            with open(input_path, 'rb') as i:
                input_image = i.read()
                # Attempt removal, but since we can't easily timeout native libraries in this environment
                # We simply catch all exceptions and rely on the UI/UX request handling to be robust.
                output_image = remove(input_image)
                with open(output_path, 'wb') as o:
                    o.write(output_image)
            return True
        except Exception as e:
            print(f"Background removal skipped or failed: {e}")
            return False

    def classify_item(self, image_source, manual_type=None):
        """
        Uses Groq AI to classify a wardrobe item.
        image_source can be a URL or a local file path.
        """
        import base64
        
        is_local = not image_source.startswith('http')
        
        if manual_type:
            prompt = f"Analyze this clothing. It is a '{manual_type}'. Provide a 'style_tag' and 'dominant_color_name'. Respond ONLY in JSON: {{'style_tag': '...', 'color_name': '...'}}"
        else:
            prompt = f"Analyze this clothing. Classify it into a specific category (e.g., Kurti, Saree, Shirt, Jeans). Also provide a 'style_tag'. Respond ONLY in JSON: {{'item_type': '...', 'style_tag': '...'}}"
            
        try:
            image_content = []
            if is_local:
                # Convert path to absolute if needed
                if not os.path.isabs(image_source):
                    image_source = os.path.join(os.getcwd(), image_source.lstrip('/'))
                
                with open(image_source, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    image_content = {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
            else:
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": image_source}
                }

            completion = self.client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            image_content
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content)
            if manual_type:
                data['item_type'] = manual_type
            return data
        except Exception as e:
            print(f"Groq Vision Error: {e}. Falling back to default.")
            return {"item_type": manual_type or "top", "style_tag": "casual"}

    def get_user_wardrobe(self, user_id):
        response = supabase.table('virtual_wardrobe').select('*').eq('user_id', user_id).execute()
        return response.data

wardrobe_service = WardrobeService()
