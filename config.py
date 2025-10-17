import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://niraj22311707_db_user:<NirajMongoDB31>@healthvoice-ai.qvihjni.mongodb.net/?retryWrites=true&w=majority&appName=HealthVoice-AI"
)
DB_NAME = "mydb"