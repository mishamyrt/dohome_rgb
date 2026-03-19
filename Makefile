VENV_PATH = ./.venv
PYTHON_VERSION = 3.13

.PHONY: configure
configure:
	rm -rf $(VENV_PATH)
	uv venv --python $(PYTHON_VERSION)
	uv sync

clean:
	rm -rf venv

.PHONY: check
check:
	uv run ruff check custom_components/
	uv run pylint custom_components/
