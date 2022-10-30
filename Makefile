VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;

deploy:
	ssh hass "rm -rf config/custom_components/dohome_rgb"
	rsync -r custom_components/dohome_rgb hass:config/custom_components/dohome_rgb
restart:
	ssh hass "source /etc/profile.d/homeassistant.sh && ha core restart"
configure:
	python3 -m venv $(VENV_PATH)
	$(VENV) pip3 install -r requirements.txt
clean:
	rm -rf venv
lint:
	. venv/bin/activate; pylama custom_components/
