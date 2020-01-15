# Shortcuts to common used functions

test:
	PYTHONPATH=`pwd` py.test -v --cov=dbschema/ -s $(TEST_OPTS) tests

coverage:
	$(MAKE) test TEST_OPTS="--cov-report=html --cov-report=term-missing"
