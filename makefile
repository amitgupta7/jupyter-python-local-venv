$(VERBOSE).SILENT:
usage:
	echo "USAGE:"
	echo "make init		Install prerequisite libs."
	echo "make auth		Authenticate aws cli with web sso."
	echo "make sync		Download/sync csv reports to ./.dataDir"
	echo "make run		Start Jupyter server"
init: venv
	. venv/bin/activate && pip install --upgrade build
	. venv/bin/activate && python -m build 
	. venv/bin/activate && pip install .
run: venv
	. venv/bin/activate && python3 -m notebook
git:
	git config http.postBuffer 524288000
sync: venv
	mkdir -p .dataDir
	. venv/bin/activate && bash -c 'awscliv2 s3 sync --size-only s3://securiti-cx-exports/cx/ .dataDir'
auth: venv
	. venv/bin/activate && AWS_CONFIG_FILE=aws-data-sync/config  bash -c 'awscliv2 sso login --no-browser'
venv:
	test -d venv || python3 -m venv venv