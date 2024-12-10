# rodaydata

## Run

Start with 

    gunicorn -w 4 -b 0.0.0.0:10000 app:app

## Develpment

https://flask.palletsprojects.com/en/stable/quickstart/

Develop with

    flask --app hello run --debug


Get the latest FX-rates from `wget https://www.bnro.ro/files/xml/years/nbrfxrates2024.xml`

## Generate static site

Generate in /build

    python3 freeze.py

