"""
    train_baseline.py
    Modulo per la Pipeline di MLOps / Training Workflow: 
    processo automatizzato che scarica i dati, 
    pulisce il testo, addestra, valuta (ROC, Confusion Matrix) 
    e salva su SQLite.

    Program entrypoint
    python train.train_baseline.py DEBUG
    python train.train_baseline.py PROD
"""
import argparse
import os
# Configuration and Parametrization
import random
import logging
import shutil

# Preprocess text (username and link placeholders)
# import re

# Export dati su db sqlite
import sqlite3
from datetime import datetime

# metrics definitions
import numpy as np

# Load dataset
from datasets import load_dataset

# tokenizer definitions
# model and pipeline definitions
from transformers import (  AutoModelForSequenceClassification,
                            AutoTokenizer,
                            DataCollatorWithPadding,
                            Trainer,
                            TrainingArguments,
                            set_seed )

# Inferenza
import torch
from scipy.special import softmax

# fine tuning
# from transformers import AutoModelForMaskedLM
# from transformers import DataCollatorForLanguageModeling

# mflow for tracking
import mlflow
import mlflow.transformers

# predictions
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc


from utils.login_mlops_hf import Login
from utils.const_baseline import ConfigDebugConstants,ConfigProdConstants
from utils.utils import preprocess_tweet , print_counter,init_debug_logger,test_debug_division

from train.metrics import compute_metrics

# abilita mflow alla scrittura su file disco
# os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

# Init global logger
logger = init_debug_logger()

# Init global Maps dataset labels
label_mapping = { 0: "Negative",
                  1: "Neutral",
                  2: "Positive"
                }

# model and tokenizer
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def create_project_dirs(config):

    config.OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True )

    config.MLFLOW_DIR.mkdir(
        parents=True,
        exist_ok=True )

    config.LOG_DIR.mkdir(
        parents=True,
        exist_ok=True )

    config.MODEL_WEIGHTS_DIR.mkdir(
        parents=True,
        exist_ok=True )

def set_all_seeds(seed=42):
    """
        Riproducibilità dei risultati
    """
    random.seed(seed)
    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    # determinismo CUDA
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # HuggingFace
    set_seed(seed)



def preprocess_function(examples):
    """
        funzione di preprocessing usando il tokenizer 
    """
    texts = [preprocess_tweet(t) for t in examples["text"]]

    return tokenizer( texts,
                      truncation=True,
                      # padding in fase di ttrainig per velocizzare
                      # l'analisi statistica ha evidenziato
                      # che il 99% dei tweet è sotto i 128 token
                      # padding="max_length",
                      max_length=CONFIG.MAX_LENGTH
                    )

def test_baseline(trainer_,
                  tokenized_dataset_):
    """
        run test on tokenized_dataset
    """
    # valutazione sui dati di test
    test_metrics = trainer_.evaluate( eval_dataset=tokenized_dataset_["test"])

    logger.info("\nTEST METRICS")
    for key, value in test_metrics.items():
        logger.info("%s: %s", key, value)

    # Logging MLflow
    mlflow.log_metrics({ "test_accuracy": test_metrics.get("eval_accuracy"),
                         "test_loss": test_metrics.get("eval_loss"),
                         "test_precision": test_metrics.get("eval_precision"),
                         "test_recall": test_metrics.get("eval_recall"),
                         "test_f1": test_metrics.get("eval_f1")
                        })
    return test_metrics

def plot_confusion_matrix(trainer_,
                          tokenized_dataset_,
                          config,
                          file_png="confusion_matrix.png"):
    """
        plot confusion matrix on test data
    """
    predictions = trainer_.predict(tokenized_dataset_["test"])

    y_true = predictions.label_ids
    y_pred = np.argmax(predictions.predictions, axis=1)

    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(6,6))
    sns.heatmap(cm, annot=True, fmt="d")
    plt.title("Confusion Matrix")

    # Salvataggio dentro la cartella unificata di output
    save_path = os.path.join(config.OUTPUT_DIR, file_png)
    plt.savefig(save_path)
    plt.close()
    mlflow.log_artifact(save_path)


def plot_roc_curve(trainer_,
                   tokenized_dataset_,
                   config,
                   file_png="roc_curve.png"):
    """
        Ripassare la logica e le definizioni
        ROC richiede score/probabilità continue
        NON classi discrete
    """

    # define class names for sentyment analysy
    class_names = [label_mapping[i] for i in range(config.NUM_CLASSES)]

    predictions = trainer_.predict(tokenized_dataset_["test"])
    # labels reali
    y_true = predictions.label_ids
    # KO sono valori discreti
    # y_pred = np.argmax(predictions.predictions, axis=1)
    # logits del modello
    logits = predictions.predictions

    # probabilità softmax
    y_scores = softmax(logits, axis=1)

    # Binarizza labels/target (es: la classe 2 diventa [0, 0, 1, 0...])
    n_classes = config.NUM_CLASSES
    y_true_bin = label_binarize(y_true, classes=range(n_classes))

    # Inizializza dizionari per memorizzare FPR, TPR e AUC per ogni classe
    # fpr = dict()
    # tpr = dict()
    # roc_auc = dict()
    fpr = {}
    tpr = {}
    roc_auc = {}

    # 2. Calcola la curva ROC per ogni singola classe (One-vs-Rest)
    for i in range(n_classes):
        # y_scores sono le probabilità (output softmax)
        # devo essere convertite in array numpy dal chiamante o nel train
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_scores[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # 3. Calcola la Micro-Average ROC curve (opzionale, aggrega tutto)
    fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_scores.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    # 4. Plotting
    plt.figure(figsize=(10, 8))

    # Plot della curva Micro-Average
    plt.plot(fpr["micro"], tpr["micro"],
                  label=f'micro-average ROC curve (area = {roc_auc["micro"]:0.2f})',
                  color='deeppink', linestyle=':', linewidth=4)

    # Plot delle curve per alcune classi specifiche (o tutte, ma 37 sono tante!)
    colors = ['aqua', 'darkorange', 'cornflowerblue']

    # utilizzo il numero reale di classi calcolate, accoppiandolo dinamicamente con i colori:
    for i, color in zip(range(len(fpr)), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=2,
            label=f'ROC curve class {class_names[i]} (area = {roc_auc[i]:0.2f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Multiclass')
    plt.legend(loc="lower right")
    plt.grid(True)

    # FIX: Salvataggio strutturato
    save_path = os.path.join(config.OUTPUT_DIR,file_png)
    plt.savefig(save_path)
    plt.close()
    mlflow.log_artifact(save_path)
    # plt.show()

def create_table_baseline(path_connect="metrics.db",
                          config=None):
    """
        Creazione tabella SQLite
        path_connect="metrics.db"
        path_connect="/content/drive/MyDrive/my_project/metrics.db"
    """

    conn = sqlite3.connect(path_connect)
    # End Creazione del db se non esiste crea il file

    # Start Creazione una tabella model_metrics_baseline
    cursor = conn.cursor()

    if config.FLAG_DROP_EXPORT_TABLE:
        cursor.execute("DROP TABLE IF EXISTS model_metrics_baseline")

    if config.FLAG_CREATE_EXPORT_TABLE:
        cursor.execute("""CREATE TABLE IF NOT EXISTS model_metrics_baseline (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  dom_name TEXT,
                  exp_id TEXT,
                  accuracy REAL,
                  precision REAL,
                  recall REAL,
                  f1_score REAL
                  )
                  """)

    conn.commit()
    conn.close()
    # End Creazione una tabella model_metrics_baseline

def insert_table_baseline(metrics,
                          exp_obj,
                          path_connect="metrics.db",
                          config=None):
    """
        Inserisci i dati in tabella a partire
        dalle metriche ritornate dal training/test
        e dall'experimenti id determinato
        a partire dal nome dell'esperimento di MLflow
    """
    # Estrae i dati dal dizionario metrics del trainer
    # le chiavi devono corrispondere a quelle calcolate in compute_metrics
    acc = metrics.get("eval_accuracy", 0)
    prec = metrics.get("eval_precision", 0)
    rec = metrics.get("eval_recall", 0)
    f1 = metrics.get("eval_f1", 0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dom_name = config.MLFLOW_RUN_NAME
    # Recupera l'ID di MLflow
    # exp_obj = mlflow.get_experiment_by_name(experiment_name)
    if exp_obj is not None:
        exp_id = exp_obj.experiment_id
    else:
        exp_id = "N/A"

    conn = sqlite3.connect(path_connect)
    cursor = conn.cursor()

    # Inserimento manuale
    cursor.execute("""INSERT INTO model_metrics_baseline
                      (timestamp, dom_name,exp_id,accuracy, precision, recall, f1_score)
                      VALUES (?,?,?,?,?,?,?)
                   """,
                   (timestamp,dom_name,exp_id, acc, prec, rec, f1))

    conn.commit()
    conn.close()

def train_baseline( model_ ,
                    train_dataset_,
                    val_dataset_,
                    tokenized_dataset_,
                    config_ ):
    """
        esegue train e test del modello , grafici ed export data 
    """

    db_path = os.path.join(config_.OUTPUT_DIR, config_.METRICS_DB_PATH)
    model_weights_dir = config_.MODEL_WEIGHTS_DIR

    # CONFIGURAZIONE DI MlFlow
    # mlflow.set_tracking_uri("file:./mlruns")
    # mlflow.set_tracking_uri(f"file:{config_.MLFLOW_DIR}")
    
    # Configurazione con backend SQLite locale
    db_mlflow_path = os.path.join(config_.MLFLOW_DIR, "mlflow.db")
    mlflow.set_tracking_uri(f"sqlite:///{db_mlflow_path}")

    # 2. DEFINISCI IL NOME DELL'ESPERIMENTO
    experiment_name = "machine_innovation_sentiment_analisys"

    # 3. RECUPERA O CREA L'ESPERIMENTO IN MODO SICURO
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id

    # 4. IMPOSTA L'ESPERIMENTO ATTIVO TRAMITE IL SUO ID REALE
    mlflow.set_experiment(experiment_id=experiment_id)

    # MFlow Logging
    data_collator = DataCollatorWithPadding( tokenizer=tokenizer)
    
    # Raggruppo i metadati in un unico dizionario (1 sola variabile invece di 3)
    run_metadata = {
        "run_name": config_.MLFLOW_RUN_NAME,
        "mode_run": config_.MLFLOW_MODE_RUN,
        "dataset_type": config_.MLFLOW_DATASET_TYPE
    }


    data_collator = DataCollatorWithPadding( tokenizer=tokenizer)

    # raise ValueError(f"Eccezione!! Mi fermo per debug {config_.OUTPUT_DIR}")

    if config_.FLAG_DEBUG_MODE:
        # debug mode con max_steps
        logger.info("RUN TRAINING WITH DEBUG MODE")
        training_args = TrainingArguments(
                                             # output_dir=CONFIG.OUTPUT_DIR ,
                                             output_dir=model_weights_dir,
                                             learning_rate=config_.LEARNING_RATE,
                                             per_device_train_batch_size=config_.BATCH_SIZE,
                                             per_device_eval_batch_size=config_.BATCH_SIZE,
                                             num_train_epochs=config_.NUM_EPOCHS ,
                                             weight_decay=config_.WEIGHT_DECAY,
                                             eval_strategy=config_.EVAL_STRATEGY_MODE,
                                             # save_strategy="epoch",
                                             save_strategy=config_.SAVE_STRATEGY_MODE,
                                             metric_for_best_model="f1",
                                             load_best_model_at_end=config_.FLAG_LOAD_BEST_MODEL,
                                             save_total_limit=config_.SAVE_TOTAL_LIMIT,
                                             seed=config_.SEED,
                                             data_seed=config_.SEED,
                                             # MLflow
                                             report_to=config_.REPORT_TO_MODE,
                                             logging_steps=config_.LOGGING_STEPS,
                                             use_cpu=config_.FLAG_USE_CPU,
                                             max_steps=config_.MAX_STEPS
                                          )

        trainer = Trainer( model=model_,
                            args=training_args,
                            train_dataset=train_dataset_,
                            eval_dataset=val_dataset_,
                            # processing_class=tokenizer,
                            # tokenizer=tokenizer,
                            data_collator=data_collator,
                            compute_metrics=compute_metrics )



    else:
        logger.info("RUN TRAINING WITH PROD MODE")
        training_args = TrainingArguments(
                                    # output_dir=config_.OUTPUT_DIR ,
                                    output_dir=model_weights_dir,
                                    learning_rate=config_.LEARNING_RATE,
                                    per_device_train_batch_size=config_.BATCH_SIZE,
                                    per_device_eval_batch_size=config_.BATCH_SIZE,
                                    num_train_epochs=config_.NUM_EPOCHS ,
                                    weight_decay=config_.WEIGHT_DECAY,
                                    eval_strategy=config_.EVAL_STRATEGY_MODE,
                                    save_strategy=config_.SAVE_STRATEGY_MODE,
                                    metric_for_best_model="f1",
                                    load_best_model_at_end=config_.FLAG_LOAD_BEST_MODEL,
                                    save_total_limit=config_.SAVE_TOTAL_LIMIT,
                                    seed=config_.SEED,
                                    data_seed=config_.SEED,
                                    # MLflow
                                    report_to=config_.REPORT_TO_MODE,
                                    logging_steps=config_.LOGGING_STEPS,
                                    use_cpu=config_.FLAG_USE_CPU
                                    )
        trainer = Trainer( model=model_,
                            args=training_args,
                            train_dataset=train_dataset_,
                            eval_dataset=val_dataset_,
                            # processing_class=tokenizer,
                            # tokenizer=tokenizer,
                            data_collator=data_collator,
                            compute_metrics=compute_metrics )

    logger.info(f"start metrics OUTPUT_DIR {config_.OUTPUT_DIR}")
    logger.info(f"start metrics MLFLOW_ARTIFACT_PATH {config_.MLFLOW_ARTIFACT_PATH}")
    logger.info(f"start metrics MLFLOW_DIR {config_.MLFLOW_DIR}")
    logger.info(f"start metrics MODEL_WEIGHTS_DIR {config_.MODEL_WEIGHTS_DIR}")
    
    with mlflow.start_run(run_name=run_metadata["run_name"]):
        mlflow.set_tags({
            "mode": run_metadata["mode_run"],
            "dataset_type": run_metadata["dataset_type"],
            "project": "twitter_sentiment",
            "framework": "huggingface",
            "model_family": "roberta"
        })

        # log parametri custom
        mlflow.log_param("model_name", MODEL_NAME)
        mlflow.log_param("dataset", "tweet_eval")
        # l'analisi statistica ha evidenziato
        # che il 99% dei tweet è sotto i 128 token
        mlflow.log_param("max_length", config_.MAX_LENGTH)

        # Aggiunta per CI_CD
        fine_checkpoint_test = False
        if os.path.exists(model_weights_dir):
            subdirs = [d for d in os.listdir(model_weights_dir) if d.startswith("checkpoint-")]
            if len(subdirs) > 0:
                fine_checkpoint_test = True

        if fine_checkpoint_test:
            trainer.train(resume_from_checkpoint=True)
        else:
            trainer.train()     
        # valutazione sul validation
        train_metrics = trainer.evaluate()







        # Seleziona solo le metriche che ti interessano per il monitoraggio:
        monitoring_metrics = { "eval_accuracy": train_metrics.get("eval_accuracy"),
                               "eval_precision": train_metrics.get("eval_precision"),
                               "eval_recall": train_metrics.get("eval_recall"),
                               "eval_f1": train_metrics.get("eval_f1"),
                               "eval_loss": train_metrics.get("eval_loss")
                              }
        # log metriche finali
        if config_.FLAG_MONITOR_METRICS:
            mlflow.log_metrics(monitoring_metrics)
        else:
            mlflow.log_metrics(train_metrics)

        # salva modello HuggingFace
        # artifact_path=OUTPUT_DIR è un percorso fisico sul tuo computer
        # Invece, artifact_path è solo il nome della cartella virtuale
        # che MLflow creerà dentro la directory ./mlruns)
        # per catalogare i pesi del modello.
        try:
            mlflow.transformers.log_model( transformers_model={ "model": trainer.model,
                                                            "tokenizer": tokenizer },
                                        # artifact_path=config_.MLFLOW_ARTIFACT_PATH
                                        artifact_path = config_.MLFLOW_DIR
                                    )
        except Exception as e:
            logger.warning(f"Salvataggio su MLflow fallito : {e}")
        

    logger.info(f"start graph and db custom db_path {db_path}")
    # grafici sui dati di test
    plot_confusion_matrix(trainer,tokenized_dataset_,config_,"confusion_matrix.png")
    plot_roc_curve(trainer,tokenized_dataset_,config_,"roc_curve.png")

    test_metrics = test_baseline(trainer,
                                 tokenized_dataset_)

    create_table_baseline(path_connect=db_path,
                          config=config_)

    insert_table_baseline(train_metrics,
                          mlflow.get_experiment_by_name(experiment_name),
                          path_connect=db_path,
                          config=config_)

    insert_table_baseline(test_metrics,
                          mlflow.get_experiment_by_name(experiment_name),
                          path_connect=db_path,
                          config=config_)
    # end export to sqllite
    trainer.save_model(config_.OUTPUT_DIR)
    tokenizer.save_pretrained(config_.OUTPUT_DIR)

    # --- Estrazione locale degli artefatti a fine addestramento ---
    logger.info(f"Esporto gli artefatti da MLflow alla cartella locale: {config_.OUTPUT_DIR}")
    
    # 1. Recupera l'ID dell'ultima run appena completata
    current_run = mlflow.active_run() or mlflow.last_active_run()
    if current_run:
        run_id = current_run.info.run_id
        from mlflow.tracking import MlflowClient
        client = MlflowClient()

        # 2. Scarica i grafici registrati su MLflow direttamente dentro OUTPUT_DIR
        # Questo scaricherà "confusion_matrix.png" e "roc_curve.png"
        client.download_artifacts(run_id, "confusion_matrix.png", config_.OUTPUT_DIR)
        client.download_artifacts(run_id, "roc_curve.png", config_.OUTPUT_DIR)
        # client.download_artifacts(run_id, config_.METRICS_DB_PATH, config_.OUTPUT_DIR)
        
        # 3. Scarica i pesi del modello formattati per HuggingFace nella sottocartella locale
        local_model_dir = os.path.join(config_.OUTPUT_DIR, "final_model")
        client.download_artifacts(run_id, config_.OUTPUT_DIR, local_model_dir)
        
        

        logger.info(f"Esportazione completata con successo in {config_.OUTPUT_DIR}")

    # Dopo trainer.train() e il logging su mlflow
    # libero i GB occupati dai checkpoint temporanei.
    if os.path.exists(model_weights_dir):
        shutil.rmtree(model_weights_dir)

if __name__ == '__main__':

    # Inizializza il parser
    parser = argparse.ArgumentParser(description="Pipeline di Training per Sentiment Analysis")

    # Definisci l'argomento (es. --mode, accettando solo DEBUG o PROD)
    parser.add_argument( '--mode',
                        type=str,
                        choices=['DEBUG', 'PROD'],
                        default='DEBUG',
                        help="Modalità di esecuzione dell'addestramento (default: DEBUG)"
                    )

    parser.add_argument("--model-source",
                        type=str,
                        choices=["base", "local", "hf"],
                        default="base"
                        )

    # Effettua il parse degli argomenti lanciati da terminale
    args = parser.parse_args()

    # Assegna la configurazione globale corretta in base all'input
    if args.mode == 'PROD':
        CONFIG = ConfigProdConstants()
        print("Training avviato in modalità: PRODUCTION")
    else:
        CONFIG = ConfigDebugConstants()
        print("Training avviato in modalità: DEBUG")

    # definizione/creazione dir e file di di output
    # os.makedirs(CONFIG.OUTPUT_DIR, exist_ok=True)
    create_project_dirs(CONFIG)
    # db_path = os.path.join(CONFIG.OUTPUT_DIR, CONFIG.METRICS_DB_PATH)
    # model_weights_dir = os.path.join(CONFIG.OUTPUT_DIR, "model_weights")

    obj_login = Login("MachineInnovation")
    obj_login.login_hf()
    print(f"lunghezza auth token {len(obj_login.get_token())}")
    
    set_all_seeds(CONFIG.SEED)

    # Test trace levels
    print("--- Inizio Test Logging ---")
    
    logger.setLevel(logging.INFO)
    if args.mode == 'PROD':
        logging.FileHandler(CONFIG.LOG_DIR / "train-prod.log")
    else:
        logging.FileHandler(CONFIG.LOG_DIR / "train-debug.log")

    # model and tokenizer
    # Load model directly
    # Aggiunta per CI_CD
    if args.model_source == "base": # default
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

    elif args.model_source == "local":
        model = AutoModelForSequenceClassification.from_pretrained(CONFIG.OUTPUT_DIR)

    elif args.model_source == "hf":
        model = AutoModelForSequenceClassification.from_pretrained("MachineInnovation/twitter-sentiment-model")

    # load dataset
    # dataset = load_dataset("tweet_eval", "sentiment")
    dataset = load_dataset("cardiffnlp/tweet_eval", "sentiment")

    print_counter(dataset["train"]["label"],label_mapping,"TRAIN")
    print_counter(dataset["validation"]["label"],label_mapping,"VAL")
    print_counter(dataset["test"]["label"],label_mapping,"TEST")

    logger.info("%s:",dataset['train'])
    logger.info("%s:",dataset['test'])
    logger.info("%s:",dataset['validation'])

    tokenized_dataset = dataset.map(preprocess_function,
                                    batched=True)

    if CONFIG.FLAG_DEBUG_MODE:
        # debug mode con max_steps
        logger.info("START RUN TRAIN WITH DEBUG MODE")
        small_train_dataset = tokenized_dataset["train"].shuffle(
                                                            seed=CONFIG.SEED
                                                            ).select (
                                                            range(CONFIG.SMALL_TRAIN_DATASET_SIZE)
                                                            )

        small_val_dataset = tokenized_dataset["validation"].shuffle (
                                                        seed=CONFIG.SEED
                                                        ).select (
                                                             range(CONFIG.SMALL_VAL_DATASET_SIZE)
                                                            )

        train_baseline(model,
                       small_train_dataset,
                       small_val_dataset,
                       tokenized_dataset,
                        CONFIG )
        logger.info("END RUN TRAIN WITH DEBUG MODE")
    else:
        logger.info("RUN TRAIN WITH PROD MODE")
        train_baseline(model,
                       tokenized_dataset["train"],
                       tokenized_dataset["validation"],
                       tokenized_dataset,
                       CONFIG )
        logger.info("END TRAIN WITH PROD MODE")
