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
    
        cachetools==3.1.1
        certifi==2019.9.11
        chardet==3.0.4
        Click==7.0
        Django==2.2.6
        Flask==1.1.1
        google-api-python-client==1.7.11
        google-auth==1.7.2
        google-auth-httplib2==0.0.3
        google-auth-oauthlib==0.4.1
        httplib2==0.14.0
        idna==2.8
        itsdangerous==1.1.0
        Jinja2==2.10.3
        MarkupSafe==1.1.1
        oauthlib==3.1.0
        pkg-resources==0.0.0
        pyasn1==0.4.8
        pyasn1-modules==0.2.7
        pymongo==3.9.0
        pytz==2019.3
        requests==2.22.0
        requests-oauthlib==1.3.0
        rsa==4.0
        six==1.13.0
        sqlparse==0.3.0
        uritemplate==3.0.0
        urllib3==1.25.6
        Werkzeug==0.16.0

    * Your `pip3 freeze` command should match the above.

6. To use the Spotify API, you must have a Client ID and Secret. However, you do not want to release these identifiers to the public.
    * Create a file named **config.cfg** in the same directory as **app.py, requirements.txt, LICENSE, ...**
    * Go to [Spotify Developer](https://developer.spotify.com/dashboard/applications)
    * Create your own application and look for the Client ID and Secret. You will need both of these to use the API.
    * You also need to set your own session secret to use Flask Sessions.
    * Your **config.cfg** should resemble the following:

        [DEFAULT]

        client_id = your_id_here <br />
        client_secret = your_secret_here <br />

7. You are now ready to run the Flask application. To run the application, execute the following command in the terminal line:
    *   `python3 app.py`

## Notes
* Spotify does not allow *POST* requests. Instead, use *PUT* to communicate with the server. 
    - Supporting documentation: [Link](https://stackoverflow.com/questions/46119001/swift-spotify-api-error-code-405-add-to-library)
* However, Python Flask HTTP requests do NOT support *PUT* requests.
    - You can get around this limitation by adding the redirected URL to Spotify's whitelist of supported websites on the Spotify Web API Application dashboard.
    - Once your URL is whitelisted, you can proceed to use *POST* requests!
* Cannot use POST or GET requests in link callback due to authorization expectations for a specific request from the Spotify server.
* Cannot use Flask session variables as they are too small to store the required user data.
