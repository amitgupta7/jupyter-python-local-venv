# jupyter-python-local-venv
## Provided as-is (w/o support)
Setup local venv with dependencies to run jupyter notebooks. 
* Require `python >= 3.5`.
* Tested with `3.9.20`. 

## Usage

```shell
git clone https://github.com/amitgupta7/jupyter-python-local-venv
cd jupyter-python-local-venv
## Print usage.
make
# USAGE:
# make init               Install prerequisite libs.
# make auth               Authenticate aws cli with web sso.
# make sync               Download/sync csv reports to ./.dataDir
# make run                Start Jupyter server
make init
## Authenticate with aws sso (browser link). 
make auth 
## Call sync. Data will be downloaded to .dataDir
make sync
## Start Jupyter server
make run
## Opens browser with localhost url.
## press ctrl+c twice to exit.
```

### Run on commandline (for generating offline html / pdf files)
```shell
## Run statistical analysis example
cd examples/statistical\ analysis/
make nbupdate
## This will run the updated notebook and generate the python, html and pdf files for offline consumption.

## Run timeseries reporting example
cd examples/timeseries\ reporting/
make nbupdate
## This will run the updated notebook and generate the python, html and pdf files for offline consumption.
```

## Troubleshooting

The below error will be thrown if the csv files location is not found. Change the `root` location to point to correct location of csv data.
```shell
dataframeLoader.py:46: UserWarning: No matching file found in ../../dataDir for regex: STRUCTURED-*.csv. Empty dataframe will be returned.
  warnings.warn("No matching file found in "+root+" for regex: "+regex+". Empty dataframe will be returned." )
...
NameError: name 'pd' is not defined
```

## Adding dependencies
* DO NOT install dependencies with `pip install ..`
* Dependencies are installed by updating `pyproject.toml`file. 
    * Run `make init` after updating `pyproject.toml`file.
```shell
## update dependencies pyproject.toml
# dependencies = [
#     "pandas==2.2.2"
#     ,"plotly==5.22.0"
#     ,"ipykernel==6.29.5"
#     ,"notebook==7.2.2"
#     ,"matplotlib==3.9.2"
# ] 

## Run make init after.
make init
```