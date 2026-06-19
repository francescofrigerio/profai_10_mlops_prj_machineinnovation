                # MACHINE INNOVATION TRAINING  

## 1. `03-ml-training.md`

## 2. ESECUZIONE DEL TRAINING 
run_train_prod.sh --prod (default usato da airflow)
run_train_prod.sh --demo 

Se viene passato in input l'argomento --demo
il training viene eseguito in debug nel contesto di produzione.
Questo può servire per velocizzare il training in produzione
quando serve fare test direttamente in produzione
oppure a semplice scopo dimostrativo

run_train_debug.sh esegue staticamente il training in DEBUG

## 2. Esecuzione Pipeline inferenza 
Esempio di output delle script run_pipe_debug.sh e run_pipe_prod.sh

Tweet: I love this ProfAi MLOps course! @HuggingFace http://example.com 
Risultato: [{'label': 'positive', 'score': 0.9962100982666016, 'sentiment': 'positive'}] 
----------------------------------------------------

----------------------------------------------------

## 3. Comandi docker:
docker compose up -d
docker compose down
docker system prune -a --volumes -f
----------------------------------------------------

ispezionare il risultato del training in produzione
mlflow ui --backend-store-uri sqlite:///outputs-baseline-prod/mlruns-prod/mlflow.db --default-artifact-root ./outputs-baseline-prod/mlruns-prod

ispezionare il risultato del training in debug
mlflow ui --backend-store-uri sqlite:///outputs-baseline-debug/mlruns-debug/mlflow.db --default-artifact-root ./outputs-baseline-debug/mlruns-debug




