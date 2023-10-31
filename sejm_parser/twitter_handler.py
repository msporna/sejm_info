import requests


class TwitterHandler:

    def __init__(self):
        import requests

        # Replace these variables with your own Twitter API credentials
        self.API_KEY = 'YOUR_API_KEY'
        self.API_SECRET_KEY = 'YOUR_API_SECRET_KEY'
        self.BEARER_TOKEN = 'YOUR_BEARER_TOKEN'
        self.ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
        self.ACCESS_TOKEN_SECRET = 'YOUR_ACCESS_TOKEN_SECRET'

        # URL for posting a tweet
        self.url = 'https://api.twitter.com/2/tweets'

    def tweet_summaries(self):
        pass  # todo

    def send_tweet(self):

        # Tweet text you want to post
        tweet_text = 'Hello, Twitter API v2.0!'

        # Set up the authorization headers
        headers = {
            'Authorization': f'Bearer {self.BEARER_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Create a JSON payload with the tweet text
        tweet_payload = {
            'status': tweet_text
        }

        # Make a POST request to post the tweet
        response = requests.post(self.url, headers=headers, json=tweet_payload)

        # Check the response status
        if response.status_code == 201:
            print('Tweet posted successfully!')
        else:
            print(f'Error posting tweet! Status code: {response.status_code}')
            print(response.json())
