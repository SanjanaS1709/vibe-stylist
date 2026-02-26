from pathlib import Path
from flask import Blueprint, render_template, request, flash, current_app, session, redirect, url_for
from routes.auth import login_required
from color_engine.analyzer import build_color_profile
from color_engine.extractor import extract_skin_lab
from color_engine.groq_generator import generate_style_package
from color_engine.shopping_links import generate_shopping_links
from werkzeug.utils import secure_filename
import uuid
from supabase_client import supabase

main_bp = Blueprint('main', __name__)

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/styling-tool')
@login_required
def index():
    return redirect(url_for('skin.analyze_skin'))
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or not file.filename:
            return render_template('index.html', error='No selected file.')
        
        if file and _allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            image_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
            file.save(image_path)
            
            context = {
                "gender": request.form.get("gender"),
                "mood": request.form.get("mood"),
                "occasion": request.form.get("occasion"),
                "campus_style": request.form.get("campus_style"),
                "budget_tier": request.form.get("budget_tier"),
                "student_year": request.form.get("student_year"),
                "season": request.form.get("season")
            }
            
            try:
                lab_values = extract_skin_lab(str(image_path))
                profile_res = build_color_profile(lab_values)
                style_package = generate_style_package(profile_res, context=context)
                shopping_links = generate_shopping_links(profile_res, context)
                
                return render_template(
                    'result.html',
                    profile=profile_res,
                    palettes=style_package,
                    style_guidance=style_package.get("style_guidance", {}),
                    shopping_links=shopping_links,
                    context=context
                )
            except Exception as e:
                return render_template('index.html', error=str(e))
    
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    from services.analytics_engine import analytics_engine
    stats = analytics_engine.get_user_stats(user_id)
    # The user didn't provide dashboard.html in template/
    # I'll create one based on their design language in a moment.
    return render_template('dashboard.html', stats=stats)

@main_bp.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    user_data = supabase.table('users').select('*').eq('id', user_id).execute().data[0]
    pref_data = supabase.table('user_preferences').select('*').eq('user_id', user_id).execute().data
    pref_data = pref_data[0] if pref_data else {}
    
    # Phase 5: Badges
    badges = supabase.table('user_badges').select('*').eq('user_id', user_id).execute().data
    
    return render_template('profile.html', user=user_data, prefs=pref_data, badges=badges)
