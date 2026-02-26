from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
from routes.auth import login_required
from services.skin_analysis import analyze_skin_tone
from supabase_client import supabase

skin_bp = Blueprint('skin', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@skin_bp.route('/analyze-skin', methods=['GET', 'POST'])
@login_required
def analyze_skin():
    user_id = session.get('user_id')
    
    # Check if user already has a result
    user_res = supabase.table('users').select('*').eq('id', user_id).execute()
    user_data = user_res.data[0] if user_res.data else None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        hair_color = request.form.get('hair_color')
        eye_color = request.form.get('eye_color')

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Run analysis
            result = analyze_skin_tone(file_path)
            
            if result == "No face detected":
                flash('No face detected. Try a clearer selfie!', 'error')
                return redirect(request.url)
            
            if result:
                # Store in Supabase
                try:
                    update_data = {'skin_tone_result': result}
                    # Add traits only if they were provided (safe fallback)
                    if hair_color: update_data['hair_color'] = hair_color
                    if eye_color: update_data['eye_color'] = eye_color

                    supabase.table('users').update(update_data).eq('id', user_id).execute()
                    flash('Analysis complete! Here is your Skin DNA.', 'success')
                    return redirect(url_for('skin.analyze_skin'))
                except Exception as e:
                    error_msg = str(e)
                    if "eye_color" in error_msg or "hair_color" in error_msg:
                        flash("Database Setup Required: Please run the SQL snippet I provided in your Supabase SQL Editor to enable these traits!", "error")
                    else:
                        flash(f'Database error: {error_msg}', 'error')
                    return redirect(request.url)
            else:
                flash('Analysis failed. Try again!', 'error')
                return redirect(request.url)
                
    return render_template('skin_analysis.html', user=user_data)

@skin_bp.route('/retake-analysis')
@login_required
def retake_analysis():
    user_id = session.get('user_id')
    supabase.table('users').update({
        'skin_tone_result': None,
        'hair_color': None,
        'eye_color': None
    }).eq('id', user_id).execute()
    return redirect(url_for('skin.analyze_skin'))
