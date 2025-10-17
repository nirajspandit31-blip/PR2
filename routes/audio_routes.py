from flask import Blueprint, request
from utils.response import success_response, error_response
import os
import tempfile
from google import generativeai as genai
from services.prompt_service import create_prompt_record_from_gemini
# from flask import current_app

# print("current_app:", current_app)
# print("current_app.mongo:", getattr(current_app, "mongo", None))


audio_bp = Blueprint("audio_bp", __name__)



@audio_bp.route("/audio-transcribe", methods=["POST"])
def audio_transcribe():
     
    if "audio" not in request.files:
        return error_response("No audio file uploaded", 400)
    audio = request.files["audio"]
    if audio.filename == "":
        return error_response("No selected file", 400)

    # Save audio to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        audio.save(temp_audio.name)
        audio_file_path = temp_audio.name

    # Load API key from environment variable
    my_api_key = "AIzaSyB5gJAmt7WEcLqVeW0Gs4cs5Em6Pa-sDoM"
    if not my_api_key:
        return error_response("GOOGLE_API_KEY not found in environment", 500)
    genai.configure(api_key=my_api_key)
 
    try:
        uploaded_file = genai.upload_file(audio_file_path)
    except Exception as e:
        return error_response(f"Error uploading file: {str(e)}", 500)

    # Create the model
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    extended_prompt = """
    First, generate a clean and accurate transcript of the speech in the audio file.
    Then, based on the transcript, identify any symptoms mentioned (such as fever, cough, headache, fatigue, etc.).
    List the symptoms clearly in bullet points.
    If no symptoms are detected, explicitly say "No symptoms detected."
    Also analyse the symptoms and provide the prescription to cure the symptoms.
    Provide the response in the "GEMENI PRESCRIPTION: "
    this subheading will contain all the medcines names and their brand
    if error return "No prescription found : go get a real doctor."
    """
    try:
        response = model.generate_content([extended_prompt, uploaded_file])
    except Exception as e:
        return error_response(f"Gemini API error: {str(e)}", 500)

    # Clean up temp file
    os.remove(audio_file_path)

    # Store Gemini output in DB
    record_id = create_prompt_record_from_gemini(response.text)

    return success_response({
        "output": response.text,
        "record_id": record_id
    })
