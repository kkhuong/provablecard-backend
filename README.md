# Envrionment Setup
## Development Server (MacBook)
**Set up PostgreSQL**:
* Get postgres installed with Homebrew and then figure out a way to create database named `provablecard`, username `provablecard` with password `provablecard`


## "Production" Server (Ubuntu 20.04 x64):
Production server is a small VPS with Python 3.8.10 installed.

**Set up PostgreSQL Database**:
* `sudo apt install postgresql postgresql-contrib`
* `sudo -i -u postgres`
* `createuser --interactive`
* Enter `provablecard` and `y`
* `createdb provablecard`
* `psql`
* `grant all privileges on database provablecard to provablecard;`

Essentially we want to create a database named `provablecard` with username `provablecard` and password `provablecard`. Yes this is a bad practice, but we want to build fast.


# First Time Setup
* Clone the repository
* Go into the directory
* Create a file named `.env` with the following content
    ```
    SERVER_IP=165.232.129.94
    SECRET_KEY='mbgw8^7%%ru00)n9lmxqdu71-w=!96o@njg)&8b9z*$p&!^xr2'
    DB_HOST='localhost'
    DB_PORT=5432
    DB_NAME='provablecard'
    DB_USER='provablecard'
    DB_PASS='provablecard'
    IS_PRODUCTION_ENVIRONMENT=False
    ```
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `python manage.py migrate`

## Launching 
* `python manage.py runserver 0.0.0.0:8000`