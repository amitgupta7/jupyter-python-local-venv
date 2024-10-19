fileName=support-reporting-level1.ipynb
nbupdate:
	. ../../venv/bin/activate && jupyter nbconvert --execute --to notebook --inplace ${fileName}
	. ../../venv/bin/activate && jupyter nbconvert --to python ${fileName}
	. ../../venv/bin/activate && jupyter nbconvert --to html ${fileName}
	. ../../venv/bin/activate && jupyter nbconvert --to pdf ${fileName}
