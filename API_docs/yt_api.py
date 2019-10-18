import requests, json

# q(str): Query term, n(int): number of result, thumbn(bool), thumb_size(str): choice of thumbnail (default, medium, high)
# Return list with size n. Each value is [title, description, video link, thumbnail link]
def query(q, n, thumb_size=None):
    # Input validation
    assert type(q) == str and type(n) == int and n >= 0

    url = "https://www.googleapis.com/youtube/v3/search"

    querystring = {"q":q,"part":"snippet","maxResults":n,"key":"AIzaSyCYBrdhDCD1swPx5w1PAv6Vi1yZ9c3A1Bs","type":"video"}

    headers = {
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    to_ret = []
    
    for i in range(n):
        # Title
        to_ret.append({'title': response['items'][i]['snippet']['title']})
        # Description
        to_ret[i]['description'] = response['items'][i]['snippet']['description']
        # Form video link
        to_ret[i]['link'] = 'https://youtube.com/watch?v=' + response['items'][i]['id']['videoId']

        if type(thumb_size) == str and thumb_size.lower() in ['default', 'medium', 'high']:
            to_ret[i]['thumbnail'] = response['items'][0]['snippet']['thumbnails']['high']['url']
        else:
            to_ret[i]['thumbnail'] = None
    
    return to_ret