from flask import Blueprint, request, session, jsonify
from routes.auth import login_required
from supabase_client import supabase

swipe_bp = Blueprint('swipe', __name__)

@swipe_bp.route('/record-swipe', methods=['POST'])
@login_required
def record_swipe():
    user_id = session.get('user_id')
    data = request.json
    
    try:
        supabase.table('swipe_history').insert({
            "user_id": user_id,
            "item_type": data.get('item_type'),
            "item_name": data.get('item_name'),
            "style_tag": data.get('style_tag'),
            "color": data.get('color'),
            "swipe_type": data.get('swipe_type'), # 'like' or 'reject'
            "source_type": data.get('source_type', 'catalog')
        }).execute()
        
        # Phase 5: Engagement
        from services.engagement_engine import engagement_engine
        from services.badge_engine import badge_engine
        engagement_engine.update_score(user_id, 1)
        badge_engine.check_and_award(user_id)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
