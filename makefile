$(VERBOSE).SILENT:
DAYS ?= 7
VENV=". ./venv/bin/activate"
usage:
	echo "USAGE:"
	echo "make init		Install prerequisite libs."
	echo "make auth		Authenticate aws cli with web sso."
	echo "make sync		Download/sync csv reports to ./.dataDir"
	echo "make run		Start Jupyter server"
init: venv
	eval ${VENV} && pip install --upgrade build
	eval ${VENV} && python -m build 
	eval ${VENV} && pip install .
run: venv
	eval ${VENV} && python3 -m notebook
git:
	git config http.postBuffer 524288000
sync: venv
	mkdir -p .dataDir
	eval ${VENV} && bash -c 'python -m awscliv2 s3 sync --size-only s3://securiti-cx-exports/cx/ .dataDir'
auth: venv
	mkdir -p ~/.aws
	test -f ~/.aws/config && cmp ~/.aws/config aws-data-sync/config || mv ~/.aws/config ~/.aws/config.bak
	cp aws-data-sync/config ~/.aws
	eval ${VENV} && bash -c 'python -m awscliv2 sso login --no-browser'
	test -f ~/.aws/config.bak && mv ~/.aws/config.bak ~/.aws/config
venv:
	test -d venv || python3 -m venv venv
sync-ndays:
	mkdir -p .dataDir
	echo "syncing files for days: ${DAYS}."
	eval ${VENV} && bash -c "python -m awscliv2 s3 sync --size-only `python3 util/awsExcludeStrGenerator.py ${DAYS}` s3://securiti-cx-exports/cx/ .dataDir"
