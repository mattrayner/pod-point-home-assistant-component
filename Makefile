.PHONY: setup setup-debian update-pip install-deps test

setup-debian:
	sudo apt-get update
	sudo apt-get install python3-dev -y
	# Sometimes installing raumel.yaml fails and the fix is to purge gcc. No idea why
	# sudo apt-get purge gcc -y

setup: update-pip install-deps test
	echo "Done"

update-pip:
	python3 -m pip install -U pip
	pip3 install -U setuptools wheel

install-deps:
	pip3 install ruamel.yaml
	pip3 install -r requirements.txt -r requirements_dev.txt -r requirements_test.txt

test:
	python3 -m pytest