import requests
import pprint
import time


class TokenForApi:

    URL = 'https://api.vk.com/method/'

    def __init__(self, version='5.194'):
        with open('token_vk.txt') as file, open('token_yandex.txt') as f:
            self.token_vk = file.readline()
            self.token_yandex = f.readline()

        self.params_vk = {
            'access_token': self.token_vk,
            'v': version}

        self.headers_yandex = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_yandex}'}

    def get_photos_to_vk(self, id=None):
        count = 0
        my_list = []
        index = 'smxopqryzw'
        url = TokenForApi.URL + 'photos.getAll?'
        parameters = {
            'owner_id': id ,
            'extended': 1,
            'offset': 0,
            'count': 200,
            'photo_sizes': 1}

        while True:
            response = requests.get(url, params={
                **self.params_vk, **parameters}).json()
            time.sleep(0.4)
            if 'error' in response:
                print(
                    '\nВнимание!!! Ошибка запроса: ', 
                    response['error']['error_msg'], end='\n\n')
            for i in response['response']['items']:
                my_list.append({
                    'size': i['sizes'][-1]['type'], 
                    'photo': {
                        'likes': i['likes']['count'],
                        'url': i['sizes'][-1]['url']}})
                count += 1
            if count == 200:
                parameters['offset'] += 200
                count = 0
            else:
                break
        # pprint.pprint(my_list)
        return my_list

    def save_photos_to_yandex(self, object, number=5):

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        name_folder = self.create_folder()

        for element in object:
            name_file = element['photo']['url'].split('/')[-1]
            name_path = name_folder + '/' + name_file
            parameters = {'path': name_path, 'overwrite': 'true'}

            response = requests.get(
                url, headers=self.headers_yandex, params=parameters).json()
            response = requests.put(
                response['href'], files={'file': element['photo']['url']}, 
                headers=self.headers_yandex, params=parameters)

    def create_folder(self):

        '''Создаем папку на яндекс диск'''

        url = 'https://cloud-api.yandex.net/v1/disk/resources' 
        name_folders = list(time.gmtime()[0:3])[::-1]
        name_folders = '_'.join(list(map(str, name_folders)))
        parameters = {'path': name_folders, 'overwrite': 'false'}
        response = requests.put(url, headers=self.headers_yandex, params=parameters)
        return name_folders

if __name__ == '__main__':
    id_user = 33579332
    # id_user = 1105788
    my_token = TokenForApi()
    object = my_token.get_photos_to_vk(id_user)
    # pprint.pprint(object)
    my_token.save_photos_to_yandex(object)
    