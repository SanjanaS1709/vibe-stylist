from flask import Blueprint, render_template, session, jsonify
from routes.auth import login_required
from services.analytics_engine import analytics_engine

achievements_bp = Blueprint('achievements', __name__)

@achievements_bp.route('/weekly-best', methods=['GET'])
@login_required
def weekly_best():
    user_id = session.get('user_id')
    outfit = analytics_engine.get_best_outfit(user_id, days=7)
    return render_template('achievements/best.html', title="Weekly Best", outfit=outfit)

@achievements_bp.route('/best-outfit-ever', methods=['GET'])
@login_required
def best_outfit_ever():
    user_id = session.get('user_id')
    outfit = analytics_engine.get_best_outfit(user_id, days=None)
    return render_template('achievements/best.html', title="Best Ever", outfit=outfit)
