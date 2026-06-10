python -m pytest ci_cd/CI/test_integration

python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short.py -v
python -m pytest ci_cd/CI/test_unit_preprocess.py -v
python -m pytest ci_cd/CI/test_unit_metrics.py -v

python -m pytest ci_cd/CI/test_unit_metrics.py -v

python -m pytest ci_cd/CI/test_unit_metrics.py -v -p no:warnings --tb=short

python -m pytest ci_cd/CI/test_integration_api.py -v -p no:warnings --tb=short