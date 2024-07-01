# International Iinternet Usage API

## intro

## How to deploy

With the following commands set up the environment
and leave the api running in localhost:5000

```
python -m venv ENV
.\ENV\Scripts\activate
pip install -r .\requirements.txt
python .\load_data.py
python .\api.py
flask --app api run
```

## How to test

Use the following commands to run all tests

```
python -m venv ENV
.\ENV\Scripts\activate
pip install -r .\requirements.txt
pip install -r .\requirements_test.txt
pytest
```
