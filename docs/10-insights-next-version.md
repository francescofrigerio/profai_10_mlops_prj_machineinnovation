# MACHINE INNOVATION RISULTATI SCELTE PROSSIMA VERSIONE

## 1. `10-insights-next-version.md`

## 4. INSIGHTS PROSSIMA VERSIONE : MLM DOMAIN ADAPTION
Nelle prossime versioni vanno valutate con attenzione le seguenti modifiche per migliorare le prestazioni da un livello discreto (accuracy/f1_score > 0.7 )
ad un livello buono (accuracy/f1_score > 0.8):

- Valutate con maggiore attenzione il valore degli iperparametri 
del training in particolare aumentare il numero di epoche come minimo a 3.

- Valutare se non sia il caso , soprattutto in caso
il sistema dovesse essere usato in un contesto più dinamico
con dati che si aggiungono nel tempo se passare dalla logica "Cold Start"
(addestramento sempre con lo stesso modello baseline scaricato da internet)
ad una logica "Cold Warm" (addestramento che parte dal migliore dei modelli
in uscita dai precedenti training).

- Valutare l'aggiunta di tecniche avanzate di fine tuning come la 
Domain Adaptation (MLM) prima della classificazione.
Il testo di Twitter/X è caratterizzato da un linguaggio poco formale per cui è una pratica comune aggiungere rispetto al flusso baseline la classificazione MLM sul dominio
e il Fine-tuning sentiment per migliorare accuracy, robustezza, gestione del sarcasmo 
e del parlare in gergo.

FLUSSO DEL FINE TUNING CON MLM ADAPTION
```text
RAW TWEETS
   ↓
PREPROCESS
   ↓
TOKENIZER
   ↓
MLM DOMAIN ADAPTATION
   ↓
SAVE DOMAIN MODEL
   ↓
LOAD DOMAIN MODEL
   ↓
SEQUENCE CLASSIFICATION FINETUNING
   ↓
INFERENCE
```

SNIPPET DI CODICE PER MLM
```python
import torch
import numpy as np
import evaluate
from scipy.special import softmax
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    AutoModelForMaskedLM, 
    DataCollatorForLanguageModeling, 
    DataCollatorWithPadding,
    TrainingArguments, 
    Trainer
)

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Caricamento del tokenizer e dei modelli core
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

"""
1. MASKED LANGUAGE MODELING (MLM)
Esegue un pre-training aggiuntivo sul dominio verticale di riferimento 
(es. crypto tweet, tweet finanziari, supporto clienti, politica, ecc.)
"""
mlm_model = AutoModelForMaskedLM.from_pretrained("cardiffnlp/twitter-roberta-base")

# Data Collator per il mascheramento casuale dei token (soglia standard 15%)
mlm_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,
    mlm_probability=0.15
)

# Configurazione del training per la fase di MLM
mlm_training_args = TrainingArguments(
    output_dir="./twitter-roberta-mlm",
    per_device_train_batch_size=16,
    num_train_epochs=3,
    save_steps=1000,
    logging_steps=100,
    learning_rate=5e-5
)

mlm_trainer = Trainer(
    model=mlm_model,
    args=mlm_training_args,
    train_dataset=tokenized_dataset["train"],
    data_collator=mlm_collator
)

# Avvio dell'adattamento al dominio
mlm_trainer.train()

# Salvataggio dell'encoder adattato al dominio dei tweet
mlm_trainer.save_model("./domain-adapted-twitter-roberta")


"""
2. FINE-TUNING PER LA CLASSIFICAZIONE DEL SENTIMENT
In questa fase non carichiamo il modello baseline, bensì l'encoder personalizzato 
sul quale Hugging Face inietterà una nuova testa di classificazione (Classification Head).
"""
model_finetuning = AutoModelForSequenceClassification.from_pretrained(
    "./domain-adapted-twitter-roberta",  # Corretto lo spazio rimosso
    num_labels=3
)

# Caricamento dei moduli di calcolo delle metriche
accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")
recall_metric = evaluate.load("recall")
precision_metric = evaluate.load("precision")

def compute_metrics_finetuning(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    # Estrazione corretta dei valori scalari dai dizionari restituiti da evaluate
    acc = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1 = f1_metric.compute(predictions=predictions, references=labels, average="weighted")["f1"]
    precision = precision_metric.compute(predictions=predictions, references=labels, average="weighted")["precision"]
    recall = recall_metric.compute(predictions=predictions, references=labels, average="weighted")["recall"]

    return {
        "accuracy_finetuning": acc,
        "f1_finetuning": f1,
        "precision_finetuning": precision,
        "recall_finetuning": recall
    }

# Configurazione del fine-tuning per la classificazione del sentiment
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

sentiment_training_args = TrainingArguments(
    output_dir="./sentiment-model-finetuning",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True
)

sentiment_trainer = Trainer(
    model=model_finetuning,
    args=sentiment_training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    data_collator=data_collator,
    compute_metrics=compute_metrics_finetuning
)

# Avvio del fine-tuning sul sentiment task
sentiment_trainer.train()

# Salvataggio definitivo del tokenizer sincronizzato
tokenizer.save_pretrained(CONFIG.OUTPUT_DIR)


"""
3. PIPELINE DI INFERENZA OTTIMIZZATA
"""
labels_mapping = ["negative", "neutral", "positive"]

def predict_sentiment_finetuning(text):
    text = preprocess_tweet(text)
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=CONFIG.MAX_LENGTH
    )

    # Allocazione dinamica sul device hardware disponibile
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_finetuning.to(device)
    
    # Spostamento dei tensori di input sullo stesso device del modello
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model_finetuning(**inputs)

    # Trasferimento sicuro su memoria CPU prima della conversione in Array NumPy
    scores = outputs.logits[0].cpu().detach().numpy()
    probs = softmax(scores)
    ranking = np.argsort(probs)[::-1]
    
    result = []
    for rank in ranking:
        result.append({
            "label": labels_mapping[rank],
            "score": float(probs[rank])
        })

    return result

# Test finale dell'inferenza
tweet_esempio = "NVIDIA earnings are amazing!"
print(predict_sentiment_finetuning(tweet_esempio))
```

## 5. INSIGHTS PROSSIMA VERSIONE : MUTUATION Testing

Il Mutation Testing si applica al codice sorgente (es. la pipeline di pre-processing o la logica del server) per verificare se gli unit test sono efficaci. Nel mondo ML, esiste anche il concetto di "Data/Model Mutation" (iniettare rumore nei dati per vedere se il modello scoppia).
Il Mutation Testing può anche essere
usato nel caso del Model Serving per unire la robustezza del codice (qualità del software) con la stabilità del rilascio di modelli predittivi.
Per esempio vediamo come strutturare una pipeline di Model Serving in Python e come testarla usando il Mutation Testing classico con Mutmut.

Cos'è il Mutation Testing.
Se i classici test misurano quanto codice copri (Code Coverage), il Mutation Testing misura quanto sono buoni i tuoi test.
Il framework introduce piccole modifiche intenzionali (chiamate mutanti) nel tuo codice sorgente (es. cambia un > in <, o un + in -). Se i tuoi unit test falliscono, il mutante viene ucciso (bene!). Se i test passano comunque, il mutante sopravvive (male, significa che i test non hanno notato il bug).

Esempio di Mutuation Testing con MLOps Model Serving
Immaginiamo di avere un microservizio FastAPI che serve un modello per decidere se approvare un mutuo (validazione o una soluzione di mutui/prestiti!).

Logica del Model serving (app.py) . 
C'è una funzione che valida l'input prima di passarlo al modello.

```python
# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LoanRequest(BaseModel):
    income: float
    loan_amount: float

def check_eligibility(income: float, loan_amount: float) -> bool:
    # Una logica di business semplice che vogliamo testare
    if income <= 0:
        return False
    ratio = loan_amount / income
    if ratio > 0.5:  # Se il mutuo supera il 50% del reddito, rifiutato
        return False
    return True

@app.post("/predict")
def predict(request: LoanRequest):
    # In un caso reale qui caricheresti il modello: model.predict(...)
    is_eligible = check_eligibility(request.income, request.loan_amount)
    return {"approved": is_eligible}
``` 
    
 Gli Unit Test

```python
# test_app.py
from app import check_eligibility

def test_eligible_loan():
    assert check_eligibility(50000, 10000) is True

def test_ineligible_loan():
    assert check_eligibility(50000, 40000) is False  
```    

Eseguendo pytest, avremo il 100% di successo. 
Ma i test sono davvero robusti?

Integrare il Mutation Testing con mutmut
In Python, lo strumento standard per il mutation testing è mutmut. 

Installazione.
```bash
pip install mutmut pytest
```

Eeseguire il mutation testing sul nostro file app.py:

```bash
mutmut run --paths-to-mutate=app.py
```

mutmut prende app.py e crea dei mutanti. 
Per esempio:

Mutante 1: Cambierà if income <= 0: in if income < 0:

Mutante 2: Cambierà if ratio > 0.5: in if ratio >= 0.5:

Se eseguiamo il comando, noteremo che alcuni mutanti potrebbero sopravvivere.
Guardando test_app.py si vede che non viene testato cosa succede esattamente quando income == 0 o quando ratio == 0.5.

Per vedere i risultati dettagliati e capire dove i test falliscono:

```bash
mutmut results
```
E per vedere esattamente cosa ha modificato un mutante sopravvissuto 
(es. il mutante #1):
```bash
mutmut show 1
```

L'obiettivo in MLOps: 

Nel model serving, un bug di logica sulle soglie (es. > invece di >=) può far passare richieste di scoring fraudolente o errate al modello ML, alterando le metriche di business. Il mutation testing ti assicura che le suite di test blocchino queste regressioni in fase di CI/CD prima del deploy in produzione.

Si possono eseguire anche la simulazione di mutazioni direttamente sui pesi del modello ML o sui dati di input.

