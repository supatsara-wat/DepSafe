class Api:

    def __init__(self, url):
        self.url = url

    def crawl_data(self, json_data):
        headers = {
            'accept': '*/*'
        }

        response = r.post(self.url, headers=headers, json=json_data)
        data = response.json()

        if 'message' in data:
            if data['message'] == 'Bad Request':
                Exception('Query for Shop Karte API is incorrect.')
            else:
                Exception(
                    'Cannot get data due to some errors in Shop Karte API.')

        if data['data'] is None or 'transition' not in data['data']:
            return pd.DataFrame(data['data'])
            # print(data['data'])
        else:
            return pd.DataFrame(data['data']['transition'])
            # print(data['data']['transition'])

