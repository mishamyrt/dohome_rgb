deploy:
	ssh hass "rm -rf config/custom_components/dohome_rgb"
	scp -r custom_components/dohome_rgb hass:config/custom_components/dohome_rgb
restart:
	ssh hass "source /etc/profile.d/homeassistant.sh && ha core restart"
configure:
	python3 -m venv ./venv
	. venv/bin/activate; pip3 install -r requirements.txt
clean:
	rm -rf venv
lint:
	. venv/bin/activate; pylama custom_components/
