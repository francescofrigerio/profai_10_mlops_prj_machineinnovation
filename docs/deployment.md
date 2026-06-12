python -m pytest ci_cd/CI/test_integration

python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short.py -v
python -m pytest ci_cd/CI/test_unit_preprocess.py -v
python -m pytest ci_cd/CI/test_unit_metrics.py -v

python -m pytest ci_cd/CI/test_unit_metrics.py -v

python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short

python -m pytest ci_cd/CI/test_integration_api.py -v -p no:warnings --tb=short


[![Premere Run Workflows per avviare il deployment](https://img.shields.io/badge/GitHub%20Actions-Premere%20Run%20Workflow%20per%20avviare%20il%20monitoraggio-blue?style=for-the-badge&logo=github)](https://github.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/update-graphs.yml)



Architettura CI/CD Machine Innovation
GitHub Push
      ¦
      ?
GitHub Action
      ¦
      ?
test integrazione ci 
      ¦
I test sono andati bene  ? 
(parte solo se i test passano) e con una condizione tipo 
if: github.ref == 'refs/heads/main'.
     run_train_prod.sh
      ¦
il Train è andato bene  ? 
python upload_folder 
      ¦
      ?
Hugging Face Model Repo
      ¦
      ?
Hugging Face Space

Su Hugging Face Machine Innovation è configurato in questo modo
Repository modello -> contiene solo pesi (model.safetensors, tokenizer, config)
Repository Space   -> contiene app.py, Dockerfile, requirements.txt

Lo Space scarica automaticamente l'ultima versione del modello dal repository modello tramite la libreria huggingface_hub. 
Questo pattern MLOps evita di copiare i file del modello dentro lo Space a ogni deploy.