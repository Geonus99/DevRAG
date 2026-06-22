from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    from api.sources import sources_bp
    app.register_blueprint(sources_bp, url_prefix='/api')

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)