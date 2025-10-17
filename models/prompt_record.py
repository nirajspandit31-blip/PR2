from datetime import datetime

class PromptRecord:
    def __init__(self, userPrompt, medicinesName, symptoms=None):
        self.userPrompt = userPrompt
        self.medicinesName = medicinesName
        self.symptoms = symptoms if symptoms else []
        self.createdAt = datetime.utcnow()
        self.updatedAt = datetime.utcnow()

    def to_dict(self):
        return {
            "userPrompt": self.userPrompt,
            "medicinesName": self.medicinesName,
            "symptoms": self.symptoms,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
