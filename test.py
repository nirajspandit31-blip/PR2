import os

model_path = r"F:\Desktop\app - Copy\models\vosk-model-small-en-us-0.15"

print("Model path exists? ", os.path.exists(model_path))
if os.path.exists(model_path):
    print("Contents:", os.listdir(model_path))
