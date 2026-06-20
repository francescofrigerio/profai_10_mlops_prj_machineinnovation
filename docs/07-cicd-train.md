           
           
           # MACHINE INNOVATION - PIPELINE CI CD TRAIN

## 1. `06-cicd-train.md`
Descrizione della pipeline cicd-train

## 2. La pipeline CICD (continuos integration e continuos deployment) 
viene eseguita con il workflow cicd-train-pipeline.yaml
solo solo nel branch main .
Sono eseguiti due jobs distinti : test e deploy

CI(continuos integration) : job test 
GitHub Push
      ¦
GitHub Action
      ¦
test integrazione ci 
      ¦
Se i test sono andati bene  
           CI(continuos deployment) : job deploy
           -> python upload_folder Hugging Face Model Repository
                        ¦
                Hugging Face Model Repo
                        ¦
                Hugging Face Space

## 3. dettagli del CI : job test.

            
            

## 4. dettagli del CD : job deploy.
L'account Hugging Face di Machine Innovation  è configurato in questo modo
            Repository modello -> contiene solo pesi (model.safetensors, tokenizer, config)
            Repository Space   -> contiene app.py, Dockerfile, requirements.txt

            Lo Space scarica automaticamente l'ultima versione del modello dal repository modello tramite la libreria huggingface_hub. 
            
            Questo pattern MLOps evita di copiare i file del modello dentro lo Space a ogni deploy.

