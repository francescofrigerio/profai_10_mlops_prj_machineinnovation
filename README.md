# Progetto: Monitoraggio della reputazione online di un’azienda 

## Guida alla Documentazione

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

[![Premere Run Workflows per avviare il monitoraggio](https://img.shields.io/badge/GitHub%20Actions-Premere%20Run%20Workflow%20per%20avviare%20il%20monitoraggio-blue?style=for-the-badge&logo=github)](https://github.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/monitoring-metrics.yml)

![Table Training](./images/dashboard_timeseries.png).
![Time Series Training](./images/dashboard_table.png).







