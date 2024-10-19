init: venv
	. venv/bin/activate && pip install --upgrade build
	. venv/bin/activate && python -m build 
	. venv/bin/activate && pip install .
run: venv
	. venv/bin/activate && python3 -m notebook
git:
	git config http.postBuffer 524288000
venv:
	test -d venv || python3 -m venv venv
