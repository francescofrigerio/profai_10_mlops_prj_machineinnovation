           
           
           # MACHINE INNOVATION - PIPELINE CI CD TRAIN

## 1. `06-cicd-train.md`

## 2. La pipeline CI CD (continuos integration e continuos deployment) 
viene eseguita con il workflow cicd-train-pipeline.yaml
solo solo nel branch main 


## 3. Pipeline CI/CD 
GitHub Push
      ¦
GitHub Action
      ¦
test integrazione ci 
      ¦
Se i test sono andati bene  
           -> python upload_folder Hugging Face Model Repository
                        ¦
                Hugging Face Model Repo
                        ¦
                Hugging Face Space

## 4. L'account Hugging Face di Machine Innovation  è configurato in questo modo
            Repository modello -> contiene solo pesi (model.safetensors, tokenizer, config)
            Repository Space   -> contiene app.py, Dockerfile, requirements.txt

            Lo Space scarica automaticamente l'ultima versione del modello dal repository modello tramite la libreria huggingface_hub. 
            
            Questo pattern MLOps evita di copiare i file del modello dentro lo Space a ogni deploy.

