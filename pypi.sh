rm -fr dist/*
py setup.py sdist bdist_wheel
py -m twine upload dist/*