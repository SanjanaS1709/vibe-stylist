from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from routes.auth import login_required
from services.ai_service import ai_service
from supabase_client import supabase

survey_bp = Blueprint('survey', __name__)

@survey_bp.route('/survey', methods=['GET'])
@login_required
def survey_page():
    return render_template('survey.html')

@survey_bp.route('/submit-survey', methods=['POST'])
@login_required
def submit_survey():
    user_id = session.get('user_id')
    
    # Get survey data from form
    survey_data = {
        "vibe": request.form.get('vibe'),
        "archetype": request.form.get('archetype'),
        "lifestyle": request.form.get('lifestyle'),
        "accessory": request.form.get('accessory')
    }
    
    # Send to AI Service
    ai_result = ai_service.analyze_style_preferences(survey_data)
    
    if ai_result:
        try:
            # Check if preferences exist
            existing = supabase.table('user_preferences').select('*').eq('user_id', user_id).execute()
            
            pref_data = {
                "user_id": user_id,
                "style_tags": ai_result.get('style_tags'),
                "color_preferences": ai_result.get('color_direction'),
                "vibe_type": ai_result.get('vibe_type'),
                "style_archetype": ai_result.get('style_archetype') # Note: I should add this to schema or handle it
            }
            
            if existing.data:
                supabase.table('user_preferences').update(pref_data).eq('user_id', user_id).execute()
            else:
                supabase.table('user_preferences').insert(pref_data).execute()
                
            flash('Survey complete! Now for the Skin Analysis.', 'success')
            return redirect(url_for('skin.analyze_skin'))
            
        except Exception as e:
            flash(f'Error storing preferences: {str(e)}', 'error')
            return redirect(url_for('survey.survey_page'))
    else:
        flash('AI analysis failed. Please try again later.', 'error')
        return redirect(url_for('survey.survey_page'))

@survey_bp.route('/api/submit-survey', methods=['POST'])
@login_required
def submit_survey_ajax():
    # For AJAX submission if preferred by frontend
    user_id = session.get('user_id')
    data = request.json
    
    ai_result = ai_service.analyze_style_preferences(data)
    
    if ai_result:
        try:
            pref_data = {
                "user_id": user_id,
                "style_tags": ai_result.get('style_tags'),
                "color_preferences": ai_result.get('color_direction'),
                "vibe_type": ai_result.get('vibe_type'),
                "style_archetype": ai_result.get('style_archetype')
            }
            
            existing = supabase.table('user_preferences').select('*').eq('user_id', user_id).execute()
            if existing.data:
                supabase.table('user_preferences').update(pref_data).eq('user_id', user_id).execute()
            else:
                supabase.table('user_preferences').insert(pref_data).execute()
                
            return jsonify({"status": "success", "message": "Analysis complete", "result": ai_result})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "error", "message": "AI analysis failed"}), 500
