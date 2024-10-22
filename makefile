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
sync: preflight
	mkdir -p .dataDir
	aws s3 sync --size-only s3://securiti-cx-exports/cx/ .dataDir 
auth: preflight
	mkdir -p ~/.aws
	test -f ~/.aws/config && cmp ~/.aws/config aws-data-sync/config || mv ~/.aws/config ~/.aws/config.bak
	cp aws-data-sync/config ~/.aws
	aws sso login --no-browser 
venv:
	test -d venv || python3 -m venv venv
sync-ndays: preflight
	mkdir -p .dataDir
	echo "syncing files for days: ${DAYS}."
	aws s3 sync --size-only `python3 util/awsExcludeStrGenerator.py ${DAYS}` s3://securiti-cx-exports/cx/ .dataDir 
preflight:
	echo "checking ..."
	type aws >/dev/null 2>&1 || { echo >&2 "aws-cli is not installed.  See https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html for steps."; exit 1; }
	echo "aws-cli is installed."
