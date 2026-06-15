                 
                 
                 
                 ┌─────────────────────┐
                 │  TRAINING PIPELINE  │
                 │                     │
                 │ MLflow              │
                 │ SQLite              │
                 │ Grafana             │
                 └─────────┬───────────┘
                           │
                           │ produce model
                           ▼

                 ┌─────────────────────┐
                 │  GITHUB REPOSITORY  │
                 │                     │
                 │ model           │
                 │ FastAPI app         │
                 │ Dockerfile          │
                 └─────────┬───────────┘
                           │
                           │ deploy
                           ▼

                 ┌─────────────────────┐
                 │ HUGGING FACE SPACE  │
                 │                     │
                 │ FastAPI             │
                 │ Loaded Model        │
                 │ /predict API        │
                 └─────────────────────┘







                                         ┌────────────────────┐
                        │     GitHub Repo    │
                        │                    │
                        │  - source code     │
                        │  - docs            │
                        │  - Dockerfile      │
                        │  - requirements    │
                        └─────────┬──────────┘
                                  │
                                  │ Git push / CI-CD
                                  ▼


══════════════════════════════════════════════════════════════

        ┌──────────────────────────────┐
        │        APACHE AIRFLOW        │
        │                              │
        │ DAG:                         │
        │ - data ingestion             │
        │ - preprocessing              │
        │ - training                   │
        │ - testing                    │
        │ - monitoring                 │
        │ - retraining                 │
        └─────────────┬────────────────┘
                      │
                      ▼

        ┌──────────────────────────────┐
        │           MLFLOW             │
        │                              │
        │ - experiments                │
        │ - metrics                    │
        │ - params                     │
        │ - artifacts                  │
        │ - model registry             │
        └─────────────┬────────────────┘
                      │
                      ▼

        ┌──────────────────────────────┐
        │         SQLITE DB            │
        │                              │
        │ model_metrics table          │
        │ prediction_logs table        │
        │ metrics table          │
        └─────────────┬────────────────┘
                      │
                      ▼

        ┌──────────────────────────────┐
        │           GRAFANA            │
        │                              │
        │ Dashboards:                  │
        │ - accuracy                   │
        │ - latency                    │
        │ - drift                      │
        │ - prediction stats           │
        └──────────────────────────────┘








