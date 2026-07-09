           
           
           # MACHINE INNOVATION - PIPELINE CI CD TRAIN

## 1. CONTINUOUS INTEGRATION / CONTINUOUS DEPLOYMENT `07-cicd-train.md`
Descrizione della pipeline cicd-train

## 2. La pipeline CICD (continuos integration e continuos deployment) 
viene eseguita con il workflow cicd-train-pipeline.yaml
solo nel branch main .
Sono eseguiti due job distinti : test e deploy

```text
 [CI(continuous integration) : job test]
          │
          ▼
      [GitHub Push]
          │
          ▼ 
     [GitHub Action]
          │
          ▼ 
     [test integrazione ci]
          │
          ▼ 
[Solo se tutti i test sono andati bene]
          │
          ▼ 
[CD(continuos deployment) : job deploy]
          │
          ▼ 
[python upload_folder Hugging Face Model Repository]
          │
          ▼ 
[Hugging Face Model Repo]
          │
          ▼ 
[Hugging Face Space]
```

## 3. dettagli del CI : job test.
Sono eseguiti gli stessi Unit Test e Integration Test del workfloe ci-test.
            
            

## 4. dettagli del CD : job deploy.
L'account Hugging Face di Machine Innovation  è configurato in questo modo:

Repository modello -> contiene solo pesi (model.safetensors, tokenizer, config)

Repository Space   -> contiene app.py, Dockerfile, requirements.txt

Lo Space scarica automaticamente l'ultima versione del modello dal repository modello tramite la libreria huggingface_hub. 
            
Questo pattern MLOps evita di copiare i file del modello dentro lo Space a ogni deploy.

