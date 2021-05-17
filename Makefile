default: test_all

.PHONY: test_all
test:
	#python -m unittest tests.test -t .
	python -m unittest discover -s tests/ -t ..
