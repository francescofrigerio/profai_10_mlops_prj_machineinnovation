import os
from huggingface_hub import upload_folder

upload_folder(
    folder_path="output-baseline-debug",
    # folder_path="output-baseline-prod",
    repo_id="francescofrigerio/machine-innovation-sentiment-model",
    repo_type="model",
    token=os.environ["HF_TOKEN"]
)