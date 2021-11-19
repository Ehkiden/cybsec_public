Had to remove run.py from git so we didnt have to remove the debug varaible from the production enviorment every time we commit a change

Code for dev:

#!./.venv/bin/python
from cybsec import app

if __name__ == "__main__":
    app.run(debug=True)

Code for prod:

#!./.venv/bin/python
from cybsec import app

if __name__ == "__main__":
    app.run()
