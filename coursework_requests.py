import requests
import pprint
import time



class TokenForApi:

    URL = 'https://api.vk.com/method/'

    def __init__(self, version='5.135'):
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
            count += response['response']['count']
            if response['response']['count'] == 200:
                parameters['offset'] += 200
            else:
                break
        return response

    def save_photos_to_yandex(self, file_path: str):

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        name_folder = self.create_folder()
        name_path = name_folder + '/' + file_path
        parameters = {'path': name_path, 'overwrite': 'true'}
        print(parameters)

        response = requests.get(
            url, headers=self.headers_yandex, params=parameters).json()
        print(response)
        with open(file_path, 'rb') as file:
            response = requests.put(
                response['href'], files={'file': file}, 
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
    # object = my_token.get_photos_to_vk(id_user)
    # pprint.pprint(object)
    # my_token.save_photos_to_yandex('31.jpg')
    