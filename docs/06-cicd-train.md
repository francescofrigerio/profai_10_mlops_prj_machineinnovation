
1. La pipeline CICD di test viene eseguita con il workflow cicd-train-pipeline.yaml
   solo sia nel branch main sia nel branch dev-ci-cd


Architettura CI/CD Machine Innovation
GitHub Push
      ¦
GitHub Action
      ¦
test integrazione ci 
      ¦
I test sono andati bene  ? 
python upload_folder Hugging Face Model Repository
      ¦
Hugging Face Model Repo
      ¦
Hugging Face Space

Hugging Face Machine Innovation è configurato in questo modo
Repository modello -> contiene solo pesi (model.safetensors, tokenizer, config)
Repository Space   -> contiene app.py, Dockerfile, requirements.txt

Lo Space scarica automaticamente l'ultima versione del modello dal repository modello tramite la libreria huggingface_hub. 
Questo pattern MLOps evita di copiare i file del modello dentro lo Space a ogni deploy.

