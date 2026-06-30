from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / '.env')

def create_app():
    app = Flask(__name__)
    CORS(app)

    from app.api.sources import sources_bp
    from app.api.chat import chat_bp

    app.register_blueprint(sources_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
