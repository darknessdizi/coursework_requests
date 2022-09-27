import requests
import pprint
import time


class TokenForApi:

    URL = 'https://api.vk.com/method/'

    def __init__(self, version):
        with open('token_vk.txt') as file, open('token_yandex.txt') as f:
            self.token_vk = file.readline()
            self.token_yandex = f.readline()
        self.params = {
            'access_token': self.token_vk,
            'v': version
        }

    def get_photos_to_vk(self, id=None):
        url = TokenForApi.URL + 'photos.getAll?'
        parameters = {
            'owner_id': id ,
            'extended': 1,
            'offset': 0,
            'count': 200,
            'photo_sizes': 1
        }
        count = 0
        while True:
            response = requests.get(url, params={**self.params, **parameters}).json()
            time.sleep(0.4)
            count += response['response']['count']
            if response['response']['count'] == 200:
                parameters['offset'] += 200
            else:
                break
        print(count)
        return response

if __name__ == '__main__':
    # id_user = 33579332
    id_user = 1105788
    my_token = TokenForApi('5.135')
    object = my_token.get_photos_to_vk(id_user)
    # pprint.pprint(object)
    