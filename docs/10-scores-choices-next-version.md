# MACHINE INNOVATION RISULTATI SCELTE PROSSIMA VERSIONE

## 1. `10-scores-choices-next-version.md`

## 2. RISULTATI 
In produzione (mode=prod) le prestazioni sono stabilmente sopra lo 0.70 (discrete)
su tutte le metriche (accuracy , precision , recall , f1_score).
Non sono stati raggiunti risultati migliori per l'esiguo numero di epoche = 2
definito in fase di parametrizzazione del training.
Avendo poche risorse a disposizione e considerato che le specifiche
non prevedono di ottimizzare le prestazioni del modello si è preferito
dedicare tempo e risorse alla progettazione e orchestrazione del progetto MLops
come previsto dalle specifiche. 
```bash
[{"accuracy":0.712959947899706958,
  "precision":0.719111669048697055,
  "recall":0.712959947899706958,
  "f1_score":0.711106887726644654,
  "timestamp":"2026-07-03 15:07:14","dom_name":"test-sent-analysis-prod"}]
```

## 3. SCELTE
Si è deciso di introdurre due modalità di esecuzione del train prod e demo.
La modalità prod permette di generare i dati reali ed effettivi di produzione.
La modalita demo permette di eseguire dei test in produzione ed è stato
infatti possibile testare l'orchestrazione del dag giornaliero
di monitoraggio che lancia in automatico il train tutte le volte
che l'accuracy o l'f1_score scendono sotto la soglia dello 0.7. 

## 4. PROSSIMA VERSIONE
Nelle prossime versioni vanno valutate le seguenti modifiche:

- Valuatre con maggiore attenzione il valore degli hiperparametri 
del training in particolare aumentare il numero di epoche come minimo a 3.

- Valutare se non sia il caso , sopratutto in caso
il sistema dovesse essere usato in un contesto più dinamico
con dati che siu aggiungono nel tempo se passare dalla logica "Cold Start"
(addestramento sempre con lo stesso modello baseline scaricato da internet)
ad una logica "Cold Warm" (addestramento che parte dal migliore dei modelli
in uscita dai precedenti training).

- Valutare l'aggiunta di tecniche avanzate di fine tuning come la 
Domain Adaptation (MLM) prima della classificazione.
E' una pratica utile con Twitter dove il linguaggio è poco formale.
Si tratta di Aggiungere rispetto al flusso baseline la classificazione MLM sul dominio
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
```bash

from transformers import AutoModelForMaskedLM
from transformers import DataCollatorForLanguageModeling

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

pipe = pipeline("text-classification", model=MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

"""
MASKED LANGUAGE MODELING (MLM)
serve per fare ulteriore pretraining sul dominio. <br>
ad Esempio: crypto tweets,
finance tweets , customer support , italian tweets , political tweets
"""

mlm_model = AutoModelForMaskedLM.from_pretrained("cardiffnlp/twitter-roberta-base")
# DataCollator MLM
mlm_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer,
                                              mlm=True,
                                              mlm_probability=0.15
                                              )

"""TRAINING AGGIUNTIVO MLM"""
training_args = TrainingArguments( output_dir="./twitter-roberta-mlm",
                                  per_device_train_batch_size=16,
                                  num_train_epochs=3,
                                  save_steps=1000,
                                  logging_steps=100,
                                  learning_rate=5e-5
                              )

trainer = Trainer( model=mlm_model,
                  args=training_args,
                  train_dataset=tokenized_dataset["train"],
                  data_collator=mlm_collator
              )

trainer.train()

"""SAVE MODEL
salva in memoria encoder aggiornato e nuovi pesi domain-adapted
"""
trainer.save_model("./domain-adapted-twitter-roberta")

"""
   FINE-TUNING SENTIMENT CLASSIFICATION
   Model Classification 
   LOAD MODEL ADAPTED
   A questo punto non biosgna caricare  cardiffnlp/twitter-roberta-base-sentiment-latest ma il modello appena adattato.
   Pertanto Hugging Face prima carica encoder MLM adattato <
   e poi aggiunge nuova classification head 
"""
model_finetuning = AutoModelForSequenceClassification.from_pretrained("./  domain-adapted-twitter-roberta",
                                                          num_labels=3
                                                          )

"""
   DEFINIZIONE DELLE METRICHE
   Si usano le stesse metriche della baseline
"""
accuracy_finetuning = evaluate.load("accuracy")
f1_metric_finetuning = evaluate.load("f1")
recall_metric_finetuning = evaluate.load("recall")
precision_metric_finetuning = evaluate.load("precision")

def compute_metrics_finetuning(eval_pred):

    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    acc = accuracy_finetuning.compute( predictions=predictions,
                                      references=labels
                                      )

    f1 = f1_metric_finetuning.compute( predictions=predictions,
                                      references=labels,
                                      average="weighted"
                                  )
    precision = precision_metric_finetuning.compute(predictions=predictions, references=labels, average="weighted")["precision"]
    recall = recall_metric_finetuning.compute(predictions=predictions, references=labels, average="weighted")["recall"]

    return { "accuracy_finetuning": acc,
              "f1_finetuning": f1,
              "precision_finetuning": precision,
              "recall_finetuning": recall
          }

"""
    TRAINING DEL MODELLO CON FINE TUNING
"""
data_collator = DataCollatorWithPadding( tokenizer=tokenizer)

training_args = TrainingArguments( output_dir="./sentiment-model-finetuning",
                                  learning_rate=2e-5,
                                  per_device_train_batch_size=16,
                                  per_device_eval_batch_size=16,
                                  num_train_epochs=3,
                                  weight_decay=0.01,
                                  # evaluation_strategy="epoch",
                                  eval_strategy="epoch",
                                  save_strategy="epoch",
                                  load_best_model_at_end=True
)

trainer = Trainer( model=model_finetuning,
                    args=training_args,
                    train_dataset=tokenized_dataset["train"],
                    eval_dataset=tokenized_dataset["validation"],
                    # processing_class=tokenizer,
                    # tokenizer=tokenizer,
                    data_collator=data_collator,
                    compute_metrics=compute_metrics_finetuning
                )

trainer.train()
# Una volta finito, salva manualmente 
# il tokenizer nella cartella dei risultati
tokenizer.save_pretrained(CONFIG.OUTPUT_DIR)

"""
    INFERENZA CON FINE TUNING
"""
labels = ["negative", "neutral", "positive"]

# Come il codice su hf
def predict_sentiment_finetuning(text):

    text = preprocess_tweet(text)
    inputs = tokenizer( text,
                        return_tensors="pt",
                        truncation=True,
                        max_length=CONFIG.MAX_LENGTH
                    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_finetuning.to(device) # Sposta il modello sul device corretto

    with torch.no_grad():
        outputs = model_finetuning(**inputs)

    # Se il modello è su GPU, prima chiamare .cpu(), altrimenti si ottiene un errore.
    # scores = outputs.logits[0].numpy()
    scores = outputs.logits[0].cpu().detach().numpy()
    probs = softmax(scores)
    ranking = np.argsort(probs)[::-1]
    result = []

    for rank in ranking:
        result.append({ "label": labels[rank],
                        "score": float(probs[rank])
                    })

    return result

tweet = "NVIDIA earnings are amazing!"
print(predict_sentiment_finetuning(tweet))
```