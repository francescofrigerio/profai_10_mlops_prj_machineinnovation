                # MACHINE INNOVATION TRAINING  

## 1. ADDESTRAMENTO DEL MODELLO DI ML `04-ml-training.md`
Descrizione e note per il training del modello di Sentiment Analysis

Il training viene eseguito in modalita baseline (Cold Start)
che è consigliabile quando dati sono sempre gli stessi perchè conviene ripartire sempre dallo modello scaricato
e riaddestrare da zero sull'intero dataset.(modalita prod) mentre solo ai fine dimostrativo o di test si considera solo una parte del dataset (modalità demo).

Cold Start : VANTAGGI 
Non c'è rischio di "data leakage" (contaminazione dei dati) 
o di catastrophic forgetting (il modello che dimentica la lingua generale per concentrarsi troppo sui dati).

Cold Start : SVANTAGGI 
Spreca un'immensa quantità di tempo e potenza di calcolo (GPU). Se il dataset cresce nel tempo,
ogni addestramento durerà sempre di più perché il modello deve imparare tutto da capo ogni volta
ed è per questo che si è pensato di aggiungere la modalità di esecuzione demo.

ALTERNATIVA AL Cold Start
In alternativa si dovrebbe Salvare il modello migliore e ripartire da lì ("Warm Start" / Continual Learning) caricare quel modello locale invece di scaricare quello da internet.
In questo caso la velocità del training è molto superiore al Cold Start. 
Il modello ha già imparato a fare Sentiment Analysis sullo stile di testi; quindi, se arrivano nuovi dati, ha solo bisogno di pochissime epoche di "rifinitura" (fine-tuning fine) per aggiornarsi.
Si corre però il rischio di overfitting. Se si continua ad addestrare lo stesso identico modello sugli stessi dati (o su pochi dati nuovi), il modello potrebbe "memorizzare" i testi invece di capirli,  e le metriche sui dati reali mai visti potrebbero crollare.

## 2. ESECUZIONE DEL TRAINING 
```bash
# (default usato da airflow)
run_train_prod.sh --prod 
# (opzionale usato per eelocizzare il training in produzione)
run_train_prod.sh --demo 
```

Se viene passato in input l'argomento --demo
il training viene eseguito con gli stessi hiperparametri di debug ma
nel contesto di produzione quindi salvando l'output nella dir dei files di produzione.
Questo può servire per velocizzare il training in produzione
quando serve fare test direttamente in produzione
oppure a semplice scopo dimostrativo.

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

## 4. Scelta degli Hiperparametri 

    Hiperparametri più significativi in modalita demo

    ```bash
    NUM_CLASSES: int = 3
    SMALL_TRAIN_DATASET_SIZE: int = 500
    SMALL_VAL_DATASET_SIZE: int = 100
    MAX_LENGTH: int = 48
    LEARNING_RATE: float = 2e-5
    BATCH_SIZE: int = 4
    NUM_EPOCHS: int = 1
    # er non fare un intera epoca
    # ed abbreviare il training
    MAX_STEPS: int = 20
    WEIGHT_DECAY: float = 0.01
    SAVE_TOTAL_LIMIT: int = 1
    LOGGING_STEPS: int = 5
    # le due strategie devono essere uguali
    # in caso di FLAG_LOAD_BEST_MODEL = True
    EVAL_STRATEGY_MODE: str = "steps"
    SAVE_STRATEGY_MODE: str = "steps"
    ```

    Hiperparametri più significativi in modalita prod

    ```bash
    NUM_CLASSES: int = 3
    MAX_LENGTH: int = 48
    LEARNING_RATE:float = 2e-5
    BATCH_SIZE: int= 16
    NUM_EPOCHS: int = 2
    WEIGHT_DECAY: float = 0.01
    SAVE_TOTAL_LIMIT: int = 2
    LOGGING_STEPS: int = 50
    # le due strategie devono essere uguali
    # in caso di FLAG_LOAD_BEST_MODEL = True
    EVAL_STRATEGY_MODE: str = "epoch"
    SAVE_STRATEGY_MODE: str = "epoch"
    ```
    
  In particolare il parametro MAX_LENGTH = 48 è stato
  scelto tramite il seguente codice e conseguente analisi.  

  ```bash

  # 1. Carica il dataset
  dataset = load_dataset("tweet_eval", "sentiment")

  # 2. Mappa delle etichette del dataset tweet_eval
  label_mapping = {
    0: "Negative",
    1: "Neutral",
    2: "Positive"
  }

  class_names = [label_mapping[i] for i in range(CONFIG.NUM_CLASSES)]

  MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
  tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

  train_texts = dataset["train"]["text"]
  lengths = []

  for text in train_texts:

    encoded = tokenizer(
        text,
        truncation=False,
        padding=False
    )

    lengths.append(len(encoded["input_ids"]))

  #  STATISTICHE IMPORTANTI
  print(f"Mean: {np.mean(lengths):.2f}")
  print(f"Median: {np.median(lengths):.2f}")

  print(f"90 percentile: {np.percentile(lengths, 90)}")
  print(f"95 percentile: {np.percentile(lengths, 95)}")
  print(f"98 percentile: {np.percentile(lengths, 98)}")
  print(f"99 percentile: {np.percentile(lengths, 99)}")

  print(f"Max: {np.max(lengths)}")
   ```

  Seguono l'output e l'analisi di questo snippet di codice
  che si può osservare sul notebook notebooks/twitter_roberta_base_sentiment_latest_fine_tuning.ipynb

   ```bash
      metrica	             valore 
      media	                 29.12  
      mediana	             29    
      90 percentile:         39.0
      95 percentile	         42 
      98 percentile	         46 
      99 percentile	         49
      max	                 93 

Da queste metriche si deduce che quasi tutti i tweet sono molto corti
cosa tipica di twitter / X .
Il fatto che:
99% = 49
max = 93
significa che ci sono pochissimi outlier lunghi.
Quindi il valore scelto MAX_LENGTH = 48
copre circa: 98-99% del dataset con pochissimi valori troncati 
e permette di evitare il padding quindi spreco di GPU e rallentamenti.
Il tutto si ottiene troncando ~1% dei tweet che possono anche essere 1-3 token 
ed è quindi praticamente irrilevante per la sentiment analysis.


