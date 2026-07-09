                        # MACHINE INNOVATION CONTINUOS INTEGRATION 

## 1. CONTINUOUS INTEGRATION `06-ci-test.md`
Descrizione della pipeline ci-test (unit test e integration test) che può essere eseguita solo manualmente dall'interfaccia web di github.

## 2. Esecuzione dei test CI
   
   I Comandi devono essere eseguiti 
   all'interno dell'ambiente virtuale quindi

   ```bash
   source .venv/bin/activate

   ./run_test_ci.sh

   # oppure eseguire
   
   python -m pytest ci_cd/CI/test_integration
   python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short -v
   python -m pytest ci_cd/CI/test_unit_preprocess.py -v
   python -m pytest ci_cd/CI/test_unit_metrics.py -v

   python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short
   python -m pytest ci_cd/CI/test_integration_api.py -v -p no:warnings --tb=short
```

3. WORKFLOW DI AUTOMAZIONE
La pipeline esegue i controlli basandosi sulle istruzioni definite nel file di configurazione .github/workflows/ci-test-pipeline.yaml, attivabile manualmente tramite pannello GitHub Actions (workflow_dispatch).

4. ELENCO DEI TEST ESEGUITI
4.1 Unit Test (Test Unitari)
Verifica Computazione Metriche: Controlla la correttezza matematica del calcolo di Accuracy, Precision, Recall e F1-Score a fronte di array di predizioni noti.

Verifica Preprocessing: Test strutturale sulle funzioni di pulizia e tokenizzazione del testo per garantire che il testo inviato in inferenza subisca lo stesso identico trattamento di quello usato durante il training.

4.2 Integration Test (Test di Integrazione)
Integrazione Dataset: Verifica la capacità del sistema di caricare correttamente il dataset di training senza corruzioni di formato.

Integrazione di Inferenza: Testa il corretto funzionamento del motore di inferenza end-to-end sul modello.

Verifica Integrità Modello: Controlla la presenza fisica dei file locali essenziali del modello (pesi, configurazioni, vocabolario) prima di avviare l'applicazione.

Simulazione Ambiente di Produzione: Esegue test di inferenza simulando le medesime condizioni e configurazioni dell'ambiente live ospitato su Hugging Face Machine Innovation.

Validazione API: Testa gli endpoint esposti dal servizio FastAPI, verificando codici di risposta (HTTP 200) e payload di output coerenti con le specifiche di produzione di Hugging Face Machine Innovation.








 
