import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        self.client = Groq(api_key=self.api_key)

    def analyze_style_preferences(self, survey_data):
        """
        Sends survey raw responses to Groq API to determine fashion archetype.
        """
        prompt = f"""
        Based on the following survey answers, classify the user's fashion archetype, generate style tags, color direction, and vibe type.
        
        Survey Responses:
        {json.dumps(survey_data, indent=2)}
        
        Return the response strictly in JSON format with the following keys:
        - style_archetype: (string)
        - style_tags: (list of strings)
        - color_direction: (list of strings)
        - vibe_type: (string)
        
        Do not include any other text in your response.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Using a common Groq model
                messages=[
                    {"role": "system", "content": "You are a fashion expert AI."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            response_content = completion.choices[0].message.content
            return json.loads(response_content)
            
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return None

    def get_persona_response(self, message, persona, context=None):
        """
        Generates a conversational response from a chosen fashion persona.
        """
        personas = {
            "female": "You are 'Sia', a chic and sophisticated female fashion stylist. Your tone is elegant, encouraging, and detail-oriented. You give advice like a best friend who has a perfect eye for luxury and trends.",
            "male": "You are 'Leo', a sharp and confident male fashion consultant. Your tone is direct, modern, and energetic. You focus on structure, bold statements, and urban sophistication."
        }
        
        system_prompt = personas.get(persona, personas['female'])
        full_msg = f"User says: {message}\n\nContext of current outfit: {json.dumps(context) if context else 'None'}"
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_msg}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Chatbot Error: {e}")
            return "Fashion is an art, and you are the canvas! How can I help you style today's look?"

ai_service = AIService()
