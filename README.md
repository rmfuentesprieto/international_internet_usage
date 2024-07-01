# International Internet Usage API

## Introduction

After the interview I took a better look at the data and took some assumptions on my own

- Only the rows where the information belongs to a country will be used.
- The pair country year is unique.

The api implements 4 handlers:

- get all entries: GET /internet-usage
    - contains 2 parameters with can be use alone or combines:
        - country: the name of the country to filter the result by
        - year: only the records of that year will be used
- add a new record: POST /internet-usage
    - body: all fields are required
  ```
  {
    Country: str
    Year: int
    UsagePercentage: float
    Source: str
  }
  ```
- delete one record: DELETE /internet-usage/{Country}/{Year}
- update one record: PUT /internet-usage/{Country}/{Year}
    - the body contains the keys that will be updated, the valid
      keys are the same as in the add request

## How to run the api

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


The commands where intended to run on Windows. 
If another OS is being used change how the virtual env is activated. 
The same applies in the test section.

## How to test

Use the following commands to run all tests

```
python -m venv ENV
.\ENV\Scripts\activate
pip install -r .\requirements.txt
pip install -r .\requirements_test.txt
pytest
```
