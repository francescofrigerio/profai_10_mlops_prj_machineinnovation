                        # MACHINE INNOVATION CONTINUOS INTEGRATION 

## 1. `05-ci-test.md`
Descrizione , comandi ed elenco test (unit test e integration test)

## 2. Esecuzione dei test CI
   
   I Comando devono essere eseguiti 
   all'interno dell'ambiente virtuale quindi

   ```bash
   source .venv\bin\activate

   ./run_test_ci.sh

   # oppure eseguire
   
   python -m pytest ci_cd/CI/test_integration
   python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short.py -v
   python -m pytest ci_cd/CI/test_unit_preprocess.py -v
   python -m pytest ci_cd/CI/test_unit_metrics.py -v

   python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short
   python -m pytest ci_cd/CI/test_integration_api.py -v -p no:warnings --tb=short
```
## 3. La pipeline CI di test viene eseguita con il workflow ci-test-pipeline.yaml
   eseguito solo manualmente dall'interfaccia github.

## 4. Elenco dei test eseguiti:

4.1  Unit Test
    - Test di computazione delle metriche (accuracy precision recall f1_score)
    - Test sullo stesso preprocessing del testo durante il train

4.2  Integration Test
    - caricamento del dataset usato nel train
    - test d'inferenza
    - test esistenza dei files del modello
    - test d'inferenza con le stesse modalità della produzione (Hugging Face achine Innovation)
    - test funzionamento dell'api con le stesse modalità della produzione (Hugging Face achine Innovation)





 
