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
    filters = data.get('filters', {})
    
    try:
        options = recommendation_engine.get_category_suggestions(user_id, category, vibe, sourcing, filters)
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

@outfit_bp.route('/save-look', methods=['POST'])
@login_required
def save_look():
    user_id = session.get('user_id')
    data = request.json
    outfit_data = data.get('outfit_data')
    vibe = data.get('vibe')
    
    if not outfit_data:
        return jsonify({"status": "error", "message": "No outfit data provided"}), 400
        
    try:
        # Check if table exists by doing a simple insert
        supabase.table('saved_looks').insert({
            'user_id': user_id,
            'outfit_data': outfit_data,
            'vibe': vibe
        }).execute()
        return jsonify({"status": "success", "message": "Look saved successfully!"})
    except Exception as e:
        error_msg = str(e)
        if "relation \"public.saved_looks\" does not exist" in error_msg:
            return jsonify({
                "status": "error", 
                "message": "Database table 'saved_looks' is missing. Please run the SQL migration I provided in the Supabase SQL Editor."
            }), 400
        print(f"Error saving look: {e}")
        return jsonify({"status": "error", "message": error_msg}), 500

@outfit_bp.route('/get-my-looks', methods=['GET'])
@login_required
def get_my_looks():
    user_id = session.get('user_id')
    try:
        res = supabase.table('saved_looks')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        return jsonify({"status": "success", "looks": res.data})
    except Exception as e:
        print(f"Error fetching looks: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500