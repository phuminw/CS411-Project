from flask import Flask, render_template, request

import configparser
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    url = "https://www.googleapis.com/youtube/v3/search"

    links = []
    picture = []

    config = configparser.ConfigParser()
    config.read("config.cfg")

    key = config.get('DEFAULT', 'key')
    postman = config.get('DEFAULT', 'postman')

    if request.method == 'POST':
        query = request.form['query']

        # User input paired with "q"
        querystring = {"q":str(query),"part":"snippet","key":str(key),"type":"video"}

        headers = {
            'User-Agent': "PostmanRuntime/7.18.0",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': str(postman),
            'Host': "www.googleapis.com",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
            }

        response = requests.get(url, headers=headers, params=querystring)
        response = response.json()

        youtube = 'https://www.youtube.com/watch?v='
        
        for data in response['items']:
            links.append(youtube + data['id']['videoId'])
            picture.append(data['snippet']['thumbnails']['medium']['url'])

        return render_template('index.html', title='Youtube API', content=zip(links, picture))

    else:
        return render_template('index.html', title='Youtube API')

if __name__ == '__main__':
    app.run(debug=True)
