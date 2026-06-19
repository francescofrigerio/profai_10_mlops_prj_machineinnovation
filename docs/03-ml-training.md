                # MACHINE INNOVATION TRAINING  

## 1. `03-ml-training.md`
Descrizione ,comandi e note per il training del modello di Sentiment Analysis

## 2. ESECUZIONE DEL TRAINING 
```bash
# (default usato da airflow)
run_train_prod.sh --prod 
# (opzionale usato per eelocizzare il training in produzione)
run_train_prod.sh --demo 
```

Se viene passato in input l'argomento --demo
il training viene eseguito in debug nel contesto di produzione.
Questo può servire per velocizzare il training in produzione
quando serve fare test direttamente in produzione
oppure a semplice scopo dimostrativo

Il seguente comando esegue staticamente il training in DEBUG
```bash
run_train_debug.sh 
```

## 2. Esecuzione Pipeline inferenza 
Esempio di output delle script 
```bash
# inferenza con il modello di produzione
./run_pipe_prod.sh
# inferenza con il modello di debug/demo
./run_pipe_debug.sh
```

L'esempio è come il seguente:
Tweet: I love this ProfAi MLOps course! @HuggingFace http://example.com 
Risultato: [{'label': 'positive', 'score': 0.9962100982666016, 'sentiment': 'positive'}] 


## 3. Comandi docker:
```bash
docker compose up -d
docker compose down
docker system prune -a --volumes -f
```


```bash
# Per ispezionare il risultato del training in produzione
mlflow ui --backend-store-uri sqlite:///outputs-baseline-prod/mlruns-prod/mlflow.db --default-artifact-root ./outputs-baseline-prod/mlruns-prod

# ispezionare il risultato del training in debug
mlflow ui --backend-store-uri sqlite:///outputs-baseline-debug/mlruns-debug/mlflow.db --default-artifact-root ./outputs-baseline-debug/mlruns-debug
```



