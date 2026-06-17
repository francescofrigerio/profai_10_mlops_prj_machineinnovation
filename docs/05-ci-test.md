1. Comandi manuali per l'esecuzione dei test CI
   
   I Comando devono essere eseguiti 
   all'interno dell'ambiente virtuale quindi
   source .venv\bin\activate

   ./run_test_ci.sh

   oppure eseguire
   
   python -m pytest ci_cd/CI/test_integration
   python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short.py -v
   python -m pytest ci_cd/CI/test_unit_preprocess.py -v
   python -m pytest ci_cd/CI/test_unit_metrics.py -v

   python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short
   python -m pytest ci_cd/CI/test_integration_api.py -v -p no:warnings --tb=short

2. La pipeline CI di test viene eseguita con il workflow pipeline-test-ci.yaml
   solo nel branch dev-ci-cd

3. La pipeline CICD di test viene eseguita con il workflow pipeline-deploymebt-cicd.yaml
   solo sia nel branch main sia nel branch dev-ci-cd
 
