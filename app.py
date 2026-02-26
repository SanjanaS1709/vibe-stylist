import os
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from config import Config
from routes.auth import auth_bp
from routes.main import main_bp
from routes.skin import skin_bp
from routes.survey import survey_bp
from routes.outfit import outfit_bp
from routes.swipe import swipe_bp
from routes.wardrobe import wardrobe_bp
from routes.achievements import achievements_bp

def create_app():
    app = Flask(__name__, template_folder='template', static_folder='statics')
    app.config.from_object(Config)

    # Initialize extensions
    bcrypt = Bcrypt(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(skin_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(outfit_bp)
    app.register_blueprint(swipe_bp)
    app.register_blueprint(wardrobe_bp)
    app.register_blueprint(achievements_bp)

    @app.errorhandler(413)
    def file_too_large(error):
        return render_template('index.html', error="File too large."), 413

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])
