from flask import Blueprint, render_template, request, session, jsonify
from routes.auth import login_required
from services.recommendation_engine import recommendation_engine
from services.ai_service import ai_service
from supabase_client import supabase

outfit_bp = Blueprint('outfit', __name__)

@outfit_bp.route('/recommend', endpoint='choose_outfit')
@login_required
def recommend_page():
    return render_template('outfit/generate.html')

@outfit_bp.route('/get-category-options', methods=['POST'])
@login_required
def get_category_options():
    user_id = session.get('user_id')
    data = request.json
    category = data.get('category', 'top')
    vibe = data.get('vibe', 'General')
    sourcing = data.get('sourcing', 'wardrobe')
    
    # Logic to fetch items based on category and sourcing
    # This will blend wardrobe items and ecommerce suggestions
    try:
        options = recommendation_engine.get_category_suggestions(user_id, category, vibe, sourcing)
        return jsonify({"status": "success", "options": options})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@outfit_bp.route('/chatbot-interaction', methods=['POST'])
@login_required
def chatbot_interaction():
    data = request.json
    message = data.get('message')
    persona = data.get('persona', 'female')
    outfit_context = data.get('outfit_context', {})
    
    try:
        response = ai_service.get_persona_response(message, persona, outfit_context)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
