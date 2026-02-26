from pathlib import Path
from flask import Blueprint, render_template, request, flash, current_app, session
from routes.auth import login_required
from color_engine.analyzer import build_color_profile
from color_engine.extractor import extract_skin_lab
from color_engine.groq_generator import generate_style_package
from color_engine.shopping_links import generate_shopping_links
from werkzeug.utils import secure_filename
import uuid

main_bp = Blueprint('main', __name__)

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or not file.filename:
            flash('No selected file.', 'error')
            return render_template('dashboard.html')
        
        if file and _allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            image_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
            file.save(image_path)
            
            # Context from request
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
                profile = build_color_profile(lab_values)
                style_package = generate_style_package(profile, context=context)
                shopping_links = generate_shopping_links(profile, context)
                
                return render_template(
                    'result.html',
                    profile=profile,
                    palettes=style_package,
                    style_guidance=style_package.get("style_guidance", {}),
                    shopping_links=shopping_links
                )
            except Exception as e:
                flash(str(e), 'error')
                return render_template('dashboard.html')
        else:
            flash('Invalid file type.', 'error')
    
    return render_template('dashboard.html', user_name=session.get('user_name'))

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('dashboard.html', user_name=session.get('user_name'))
