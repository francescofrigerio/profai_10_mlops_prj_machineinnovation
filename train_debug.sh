cd src
python -m train.train_baseline --mode DEBUG 2>&1 | tee train_debug.log
# PYTHONPATH=. python train/train_baseline.py --mode DEBUG 2>&1 | tee train_debug.log
