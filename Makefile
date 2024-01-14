VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;
PIP = pip --disable-pip-version-check

configure:
	rm -rf $(VENV_PATH)
	python3 -m venv $(VENV_PATH)
	$(VENV) $(PIP) install -r requirements.txt
clean:
	rm -rf venv

.PHONY: lint
lint:
	$(VENV) ruff check custom_components/
	$(VENV) pylint custom_components/

local-bundle:
	rm -rf ../myrt_home/services/home-assistant/bundle/custom_components/dohome_rgb/
	cp -r custom_components/dohome_rgb ../myrt_home/services/home-assistant/bundle/custom_components/
