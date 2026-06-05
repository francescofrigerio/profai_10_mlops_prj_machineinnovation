import os
from huggingface_hub import upload_folder

upload_folder(  folder_path="output",
                repo_id="MachineInnovation/twitter-sentiment-model",
                repo_type="model",
                token=os.environ["HF_TOKEN"]
             )