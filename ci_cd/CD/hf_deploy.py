import os
from huggingface_hub import upload_folder

# Prende la cartella definita nel workflow, altrimenti usa prod di default
model_folder = os.environ.get("MODEL_OUT_DIR", "src/outputs-baseline-prod")

upload_folder(  folder_path=model_folder,
                # repo_id="MachineInnovation/twitter-sentiment-model",
                repo_id="francescofrigerio/machine-innovation-sentiment-model",
                repo_type="model",
                token=os.environ["HF_TOKEN"]
             )