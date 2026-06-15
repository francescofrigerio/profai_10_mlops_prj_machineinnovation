python -m pytest ci_cd/CI/test_integration

python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short.py -v
python -m pytest ci_cd/CI/test_unit_preprocess.py -v
python -m pytest ci_cd/CI/test_unit_metrics.py -v

python -m pytest ci_cd/CI/test_unit_metrics.py -v

python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short

python -m pytest ci_cd/CI/test_integration_api.py -v -p no:warnings --tb=short


[![Premere Run Workflows per avviare il test](https://img.shields.io/badge/GitHub%20Actions-Premere%20Run%20Workflow%20per%20avviare%20il%20monitoraggio-blue?style=for-the-badge&logo=github)](https://github.com/francescofrigerio/profai_10_mlops_prj_machineinnovation/actions/workflows/update-graphs.yml)