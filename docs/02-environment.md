Per ricreare l'enviroment e reinstallare le lib
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install torch torchvision \
  --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python -c "import torch; print(torch.__version__)"  # deve stampare 2.x.x+cpu
python -c "import torch; print(torch.cuda.is_available())" # deve dare false
python -c "from transformers import AutoModelForSequenceClassification"