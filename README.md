# Progetto: Monitoraggio della reputazione online di un’azienda 

## Guida alla Documentazione

Per comprendere a fondo il progetto, si consiglia di leggere la documentazione nella cartella `docs/` seguendo l'ordine logico:

1. [01 - Architettura del Sistema](docs/01-architecture.md): Visione d'insieme e flusso dati.
2. [02 - Environment](docs/02-environment.md): Setup environment del progetto.
3. [03 - ML Pipeline](docs/02-ml_training.md]: Training modello di Sentiment Analysis.
4. [04 - Model Serving](docs/04-model-serving.md): Endpoint FastAPI e Model Serving.
5. [05 - CI & test](docs/05-test.md): Workflow CI di GitHub Actions e Build Template Docker.
6. [06 - CI/CD & Train](docs/06-cicd-train.md): Workflow di CI/CD GitHub Actions e Docker.
7. [07 - Monitoraggio](docs/07-monitoring.md): Dashboard Grafana e logica di alerting.
8. [08 - Schedulazione](docs/08-scheduling.md) Schedulazione Retrain e Monitoraggio con Airflow

[![Premere Run Workflows per avviare il monitoraggio](https://img.shields.io/badge/GitHub%20Actions-Premere%20Run%20Workflow%20per%20avviare%20il%20monitoraggio-blue?style=for-the-badge&logo=github)](https://github.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/update-graphs.yml)

![Table Training](./images/dashboard_timeseries.png).
![Time Series Training](./images/dashboard_table.png).







