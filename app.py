from flask import Flask
from flask_pymongo import PyMongo
from routes.prompt_routes import prompt_bp
from routes.audio_routes import audio_bp
import config


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = config.MONGO_URI

    # Mongo connection
    mongo = PyMongo(app)
    app.mongo = mongo

    # Register routes
    app.register_blueprint(prompt_bp, url_prefix="/api")
    app.register_blueprint(audio_bp, url_prefix="/api")

    # Root route
    @app.route("/")
    def home():
        return {
            "message": "Flask Mongo API is running...",
            "available_endpoints": {
                "prompts": "/api/prompts",
                "audio_transcribe": "/api/audio-transcribe"
            }
        }

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)