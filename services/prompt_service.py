from flask import current_app, has_app_context
from bson import ObjectId
import datetime
from config import DB_NAME
from models.prompt_record import PromptRecord

def get_collection():
    if not has_app_context():
        raise RuntimeError("Flask app context not active. Cannot access MongoDB.")
    
    mongo = getattr(current_app, "mongo", None)
    if mongo is None:
        raise RuntimeError("MongoDB connection not initialized. Did you forget app.mongo = PyMongo(app)?")
    
    return mongo.db[DB_NAME].prompt_records





def create_prompt_record(data):
    def create_prompt_record(data):
     with current_app.app_context():  # ensures app context
        record = PromptRecord(
            userPrompt=data["userPrompt"],
            medicinesName=data["medicinesName"],
            symptoms=data.get("symptoms", [])
        )
        collection = get_collection()
        inserted_id = collection.insert_one(record.to_dict()).inserted_id
        return str(inserted_id)
    

def get_prompt_records():
    collection = get_collection()
    return list(collection.find({}))

def get_prompt_record(record_id):
    collection = get_collection()
    return collection.find_one({"_id": ObjectId(record_id)})

def update_prompt_record(record_id, data):
    collection = get_collection()
    data["updatedAt"] = datetime.datetime.utcnow()
    result = collection.update_one({"_id": ObjectId(record_id)}, {"$set": data})
    return result.modified_count > 0

def delete_prompt_record(record_id):
    collection = get_collection()
    result = collection.delete_one({"_id": ObjectId(record_id)})
    return result.deleted_count > 0

def create_prompt_record_from_gemini(response_text):
    transcript = []
    symptoms = []
    prescription = []

    lines = response_text.splitlines()
    in_symptoms = False
    in_prescription = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "transcript" in line.lower():
            transcript.append(line)
        if "symptom" in line.lower():
            in_symptoms = True
        if in_symptoms and line.startswith("-"):
            symptoms.append(line.lstrip("- ").strip())
        if "GEMENI PRESCRIPTION:" in line:
            in_prescription = True
            prescription.append(line)
        elif in_prescription:
            prescription.append(line)
        if "No symptoms detected" in line:
            symptoms = []
            in_symptoms = False
        if "No prescription found" in line:
            prescription = ["No prescription found : go get a real doctor."]
            in_prescription = False

    data = {
        "userPrompt": " ".join(transcript) if transcript else "Audio transcription",
        "medicinesName": ", ".join(prescription) if prescription else "None",
        "symptoms": symptoms
    }

    return create_prompt_record(data)
