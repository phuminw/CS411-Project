# CS411 Final Project

## Disclaimer!
This guide was created using a **Linux OS** machine!

<hr>

## Setup

1. Clone the repository from Github.
2. Current Base Flask code is hosted on branch **flask_base**. Switch to this branch and create new branches if needed.
3. Create a virtual environment and begin downloading the required libraries.
    * To begin, install virtual environment. Make sure to install using **pip3**.
        `pip3 install virtualenv`
    * Create a virtual environment. There are several ways to do this, but this is the terminal command I used: <br />
            `virtualenv -p /usr/bin/python3 venv` <br />
        You can also use: <br />
            `virtualenv -p python3 venv`
4. Enter the virtual environment with the following command:
    *   `source venv/bin/activate`
5. Install the required dependencies to run Flask with the following command:
    *   `pip3 install -r requirements.txt`
    * At the time of writing this guide, you should check if the required dependencies have been installed correctly by running the following in the terminal line:
        `pip3 freeze`
    
        certifi==2019.9.11 <br />
        chardet==3.0.4 <br />
        Click==7.0 <br />
        Django==2.2.6 <br />
        Flask==1.1.1 <br />
        idna==2.8 <br />
        itsdangerous==1.1.0 <br />
        Jinja2==2.10.3 <br />
        MarkupSafe==1.1.1 <br />
        pkg-resources==0.0.0 <br />
        pytz==2019.3 <br />
        requests==2.22.0 <br />
        sqlparse==0.3.0 <br />
        urllib3==1.25.6 <br />
        Werkzeug==0.16.0 <br />

    * Your `pip3 freeze` command should match the above.

6. To use the Spotify API, you must have a Client ID and Secret. However, you do not want to release these identifiers to the public.
    * Create a file named **config.cfg** in the same directory as **app.py, requirements.txt, LICENSE, ...**
    * Go to [Spotify Developer](https://developer.spotify.com/dashboard/applications)
    * Create your own application and look for the Client ID and Secret. You will need both of these to use the API.
    * Your **config.cfg** should resemble the following:

        [DEFAULT]

        client_id = your_id_here <br />
        client_secret = your_secret_here <br />

7. You are now ready to run the Flask application. To run the application, execute the following command in the terminal line:
    *   `python3 app.py`
