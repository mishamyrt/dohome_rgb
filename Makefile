VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;

deploy:
	rm -rf ../myrt_home/bundle/home_assistant/custom_components/dohome_rgb
	cp -r custom_components/dohome_rgb ../myrt_home/bundle/home_assistant/custom_components/dohome_rgb
	cd ../myrt_home && make deploy
restart:
	ssh hass "source /etc/profile.d/homeassistant.sh && ha core restart"
configure:
	python3 -m venv $(VENV_PATH)
	$(VENV) pip install -r requirements.txt
clean:
	rm -rf venv
lint:
	$(VENV) pylint custom_components/
