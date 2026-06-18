# Machine Innovation Training 
1.


2. Pipeline inferenza da linjea di comando
Esempio di output delle script run_pipe_debug.sh e run_pipe_prod.sh

Tweet: I love this ProfAi MLOps course! @HuggingFace http://example.com 
Risultato: [{'label': 'positive', 'score': 0.9962100982666016, 'sentiment': 'positive'}] 
----------------------------------------------------

----------------------------------------------------

2. Comandi docker:
docker compose up -d
docker compose down
docker system prune -a --volumes -f
----------------------------------------------------

ispezionare il risultato del training in produzione
mlflow ui --backend-store-uri sqlite:///outputs-baseline-prod/mlruns-prod/mlflow.db --default-artifact-root ./outputs-baseline-prod/mlruns-prod

ispezionare il risultato del training in debug
mlflow ui --backend-store-uri sqlite:///outputs-baseline-debug/mlruns-debug/mlflow.db --default-artifact-root ./outputs-baseline-debug/mlruns-debug




