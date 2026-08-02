.PHONY: install test run report dry-run

install:
	python3 -m pip install -r requirements.txt

test:
	python3 -m unittest discover -s tests -v

run:
	python3 -m opensea_mail.scripts.pipeline

report:
	python3 -m opensea_mail.scripts.pipeline --report

dry-run:
	python3 -m opensea_mail.scripts.pipeline --report --dry-run
