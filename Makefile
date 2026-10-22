.PHONY: setup all test sql score pbi-init pbi-reset clean-outputs
PY ?= python

setup:            ## install dependencies
	$(PY) -m pip install -r requirements.txt

all:              ## rebuild everything from the raw CSV: cleaning, EDA, model, segments, SQL, notebooks
	$(PY) scripts/run_all.py

test:             ## run the unit tests
	$(PY) -m unittest discover -s tests -v

sql:              ## re-run only the SQL analysis
	$(PY) scripts/run_sql.py

score:            ## score the raw file with the saved model
	PYTHONPATH=src $(PY) -m churn.predict --input data/raw/Telco-Customer-Churn.csv --output reports/tables/scored_customers.csv

pbi-init:         ## set the Power BI RepoRoot to this clone
	$(PY) scripts/init.py

pbi-reset:        ## restore the placeholder path (run before committing)
	$(PY) scripts/init.py --reset

clean-outputs:    ## delete generated outputs (keeps raw data)
	rm -rf reports/figures/* reports/tables/* models/* data/processed/*
