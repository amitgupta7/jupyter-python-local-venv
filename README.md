# jupyter-python-local-venv
## Provided as-is (w/o support)
Setup local venv with dependencies to run jupyter notebooks. Tested with `python3.12.4`. 

## Adding dependencies
* Dependencies are installed in `pyproject.toml`file. 
* Run `make init` after updating `pyproject.toml`file.

## Usage
```shell
git clone https://github.com/amitgupta7/jupyter-python-local-venv
cd jupyter-python-local-venv
make init
make run
```