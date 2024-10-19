fileName=support-reporting-level1.ipynb
VENV=". ../../venv/bin/activate"
nbupdate:
	eval ${VENV} && jupyter nbconvert --execute --to notebook --inplace ${fileName}
	eval ${VENV} && jupyter nbconvert --to python ${fileName}
	eval ${VENV} && jupyter nbconvert --to html ${fileName}
	eval ${VENV} && jupyter nbconvert --to pdf ${fileName}
