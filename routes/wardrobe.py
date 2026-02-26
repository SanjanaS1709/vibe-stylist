import os, uuid
from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from routes.auth import login_required
from services.wardrobe_service import wardrobe_service
from services.color_extractor import color_extractor
from supabase_client import supabase

wardrobe_bp = Blueprint('wardrobe', __name__)

@wardrobe_bp.route('/wardrobe', endpoint='wardrobe')
@login_required
def wardrobe_page():
    user_id = session.get('user_id')
    items = wardrobe_service.get_user_wardrobe(user_id)
    
    # Fetch user gender for dynamic categories
    user_res = supabase.table('users').select('gender').eq('id', user_id).single().execute()
    gender = user_res.data.get('gender', 'Female') if user_res.data else 'Female'
    
    return render_template('wardrobe.html', items=items, user_gender=gender)

@wardrobe_bp.route('/upload-wardrobe-item', methods=['POST'])
@login_required
def upload_item():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"}), 400
    
    file = request.files['image']
    item_type = request.form.get('item_type', 'top') # From the new dropdown
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    user_id = session.get('user_id')
    upload_dir = current_app.config['UPLOAD_FOLDER']
    
    # Ensure directory exists
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    raw_filename = secure_filename(f"raw_{user_id}_{uuid.uuid4().hex[:8]}_{file.filename}")
    raw_path = os.path.join(upload_dir, raw_filename)
    processed_filename = f"wardrobe_{user_id}_{uuid.uuid4().hex[:8]}.png"
    processed_path = os.path.join(upload_dir, processed_filename)
    
    # Save original raw image
    file.save(raw_path)
    
    # 1. AI BACKGROUND REMOVAL (Optional/Fail-safe)
    # If the environment is slow, we allow it to be skipped
    bg_removed = False
    try:
        # We only attempt removal but with the understanding it might return False 
        # instantly if it previously detected a hang, or we can simply comment it out
        # if the user wants to prioritize the upload itself.
        # bg_removed = wardrobe_service.remove_bg(raw_path, processed_path)
        pass 
    except:
        pass

    final_filename = processed_filename if bg_removed else raw_filename
    final_path = processed_path if bg_removed else raw_path
    
    # This URL is for browser display
    image_url = f"/statics/uploads/{final_filename}"
    
    # 2. Extract color from bg-removed image
    dominant_color = color_extractor.get_dominant_color(final_path)
    
    # 3. Classify/Refine - Pass the local path for AI to read via base64
    classification = wardrobe_service.classify_item(final_path, manual_type=item_type)
    
    try:
        supabase.table('virtual_wardrobe').insert({
            "user_id": user_id,
            "item_type": item_type,
            "image_url": image_url,
            "dominant_color": dominant_color,
            "style_tag": classification.get('style_tag', 'casual')
        }).execute()
        
        # Engagement & Badges
        try:
            from services.engagement_engine import engagement_engine
            from services.badge_engine import badge_engine
            engagement_engine.update_score(user_id, 3)
            badge_engine.check_and_award(user_id)
        except ImportError:
            pass # Engine might not be ready yet
        
        return jsonify({
            "status": "success", 
            "color": dominant_color, 
            "type": item_type,
            "image_url": image_url
        })
    except Exception as e:
        print(f"UPLOAD ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
