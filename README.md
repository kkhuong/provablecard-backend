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


# Initial Launch
* Clone the repository
* Go into the directory
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `python manage.py migrate`

## Launching 
* `python manage.py runserver 0.0.0.0:8000`