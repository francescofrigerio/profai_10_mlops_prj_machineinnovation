# Progetto: Monitoraggio della reputazione online di un’azienda 

## 1. Guida alla Documentazione

Per comprendere a fondo il progetto, si consiglia di leggere la documentazione nella cartella `docs/` seguendo l'ordine logico:

1. [01 - Architettura del Sistema](docs/01-architecture.md): Visione d'insieme e flusso dati.
2. [02 - Descrizione del progetto.](docs/02-project-overview.md) Scelte progettuali, implementazioni e risultati
3. [03 - Environment](docs/03-environment.md): Setup environment del progetto.
4. [04 - ML Training](docs/04-ml-training.md): Training modello di Sentiment Analysis.
5. [05 - Model Serving](docs/05-model-serving.md): Endpoint FastAPI e Model Serving.
6. [06 - CI & test](docs/06-ci-test.md): Workflow CI di GitHub Actions e Build Template Docker.
7. [07 - CI/CD & Train](docs/07-cicd-train.md): Workflow di CI/CD GitHub Actions e Docker.
8. [08 - Monitoraggio](docs/08-monitoring.md): Dashboard Grafana e logica di alerting.
9. [09 - Schedulazione e Orchestrazione](docs/09-scheduling.md) Retrain automatico e Monitoraggio continuo
10. [10 - Specifiche iniziali del Progetto](docs/10-technical-specifications.md)
11. [11 - Risultati Scelte Future Versioni](docs/11-scores-choices-insights.md)

## 2. Accesso al workflow di Monitoraggio

[![Premere Run Workflows per avviare il monitoraggio](https://img.shields.io/badge/GitHub%20Actions-Premere%20Run%20Workflow%20per%20avviare%20il%20monitoraggio-blue?style=for-the-badge&logo=github)](https://github.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/monitoring-metrics.yml)

## 3. Grafici Monitoraggio

![Table Training](./images/dashboard_timeseries.png).


![Time Series Training](./images/dashboard_table.png).

## 4. Grafici Addestramento

![Roc Curce Training](./src/outputs-baseline-prod/roc_curve.png).


![Confusion Matrix Training](./src/outputs-baseline-prod/confusion_matrix.png).



## 5. Specifiche iniziali del Progetto

Monitoraggio della reputazione online di un’azienda
MachineInnovators Inc. è leader nello sviluppo di applicazioni di machine learning scalabili e pronte per la produzione. Il focus principale del progetto è integrare metodologie MLOps per facilitare lo sviluppo, l'implementazione, il monitoraggio continuo e il retraining dei modelli di analisi del sentiment. L'obiettivo è abilitare l'azienda a migliorare e monitorare la reputazione sui social media attraverso l'analisi automatica dei sentiment.

Le aziende si trovano spesso a fronteggiare la sfida di gestire e migliorare la propria reputazione sui social media in modo efficace e tempestivo. Monitorare manualmente i sentiment degli utenti può essere inefficiente e soggetto a errori umani, mentre la necessità di rispondere rapidamente ai cambiamenti nel sentiment degli utenti è cruciale per mantenere un'immagine positiva dell'azienda.

Benefici della Soluzione

Automazione dell'Analisi del sentiment: Implementando un modello di analisi del sentiment, MLOps Innovators Inc. automatizzerà l'elaborazione dei dati dai social media per identificare sentiment positivi, neutrali e negativi. Ciò permetterà una risposta rapida e mirata ai feedback degli utenti.
Monitoraggio Continuo della Reputazione: Utilizzando metodologie MLOps, l'azienda implementerà un sistema di monitoraggio continuo per valutare l'andamento del sentiment degli utenti nel tempo. Questo consentirà di rilevare rapidamente cambiamenti nella percezione dell'azienda e di intervenire prontamente se necessario.
Retraining del Modello: Introdurre un sistema di retraining automatico per il modello di analisi del sentiment assicurerà che l'algoritmo si adatti dinamicamente ai nuovi dati e alle variazioni nel linguaggio e nei comportamenti degli utenti sui social media. Mantenere alta l'accuratezza predittiva del modello è essenziale per una valutazione corretta del sentiment.
Dettagli del Progetto

Fase 1: Implementazione del Modello di Analisi del sentiment
Modello: Utilizzare un modello pre-addestrato per un’analisi del sentiment in grado di classificare testi dai social media in sentiment positivo, neutro o negativo. Servirsi di questo modello: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest
Dataset: Utilizzare dataset pubblici contenenti testi e le rispettive etichette di sentiment.
Fase 2: Creazione della Pipeline CI/CD
Pipeline CI/CD: Sviluppare una pipeline automatizzata per il training del modello, i test di integrazione e il deploy dell'applicazione su HuggingFace.
Fase 3: Deploy e Monitoraggio Continuo
Deploy su HuggingFace (facoltativo): Implementare il modello di analisi del sentiment, inclusi dati e applicazione, su HuggingFace per facilitare l'integrazione e la scalabilità.
Sistema di Monitoraggio: Configurare un sistema di monitoraggio per valutare continuamente le performance del modello e il sentiment rilevato.
Consegna
Codice Sorgente: Repository pubblica su GitHub con codice ben documentato per la pipeline CI/CD e l'implementazione del modello. La consegna vera e propria dovrà avvenire mediante un notebook google colab con al suo interno il link al repository GitHub.
Documentazione: Descrizione delle scelte progettuali, delle implementazioni e dei risultati ottenuti durante il progetto.
Motivazione del Progetto

L'implementazione di un modello per l'analisi del sentiment consente a MLOps Innovators Inc. di migliorare significativamente la gestione della reputazione sui social media. Automatizzando l'analisi del sentiment, l'azienda potrà rispondere più rapidamente alle esigenze degli utenti, migliorando la soddisfazione e rafforzando l'immagine dell'azienda sul mercato. Con questo progetto, MLOps Innovators Inc. promuove l'innovazione nel campo delle tecnologie AI, offrendo soluzioni avanzate e scalabili per le sfide moderne di gestione della reputazione aziendale.



