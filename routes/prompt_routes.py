from flask import Blueprint, request
from services import prompt_service
from utils.response import success_response, error_response

prompt_bp = Blueprint("prompt_bp", __name__)

@prompt_bp.route("/prompts", methods=["POST"])
def create_prompt():
    data = request.json
    if not data.get("userPrompt") or not data.get("medicinesName"):
        return error_response("userPrompt and medicinesName are required", 400)

    record_id = prompt_service.create_prompt_record(data)
    return success_response({"id": record_id}, 201)

@prompt_bp.route("/prompts", methods=["GET"])
def get_all_prompts():
    records = prompt_service.get_prompt_records()
    for r in records:
        r["_id"] = str(r["_id"])
    return success_response(records)

@prompt_bp.route("/prompts/<record_id>", methods=["GET"])
def get_prompt(record_id):
    record = prompt_service.get_prompt_record(record_id)
    if not record:
        return error_response("Record not found", 404)
    record["_id"] = str(record["_id"])
    return success_response(record)

@prompt_bp.route("/prompts/<record_id>", methods=["PUT"])
def update_prompt(record_id):
    data = request.json
    updated = prompt_service.update_prompt_record(record_id, data)
    if not updated:
        return error_response("Update failed or record not found", 400)
    return success_response({"updated": True})

@prompt_bp.route("/prompts/<record_id>", methods=["DELETE"])
def delete_prompt(record_id):
    deleted = prompt_service.delete_prompt_record(record_id)
    if not deleted:
        return error_response("Delete failed or record not found", 400)
    return success_response({"deleted": True})
