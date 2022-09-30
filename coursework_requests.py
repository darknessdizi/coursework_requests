import requests
import pprint
import time


class TokenForApi:

    URL = 'https://api.vk.com/method/'

    def __init__(self, token, version='5.194', number=5):
        with open('token_vk.txt') as file:
            self.token_vk = file.readline()
        self.token_yandex = token
        self.number = number

        self.params_vk = {
            'access_token': self.token_vk,
            'v': version}

        self.headers_yandex = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_yandex}'}

    def get_photos_to_vk(self, id=None):
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

            my_list = self._add_photo_to_list(response) 

            if len(my_list) == 200:
                parameters['offset'] += 200
            else:
                break
        pprint.pprint(my_list)
        return my_list

    def _add_photo_to_list(self, response):
        my_list = []
        count = 0
        for i in response['response']['items']:
                name_file = i['sizes'][-1]['url'].split('/')[-1].split('?')[0]
                index = name_file.find('.')
                name_file = name_file[index:]
                name_file = f'{i["likes"]["count"]}{name_file}'

                my_list.append({
                    'size': i['sizes'][-1]['type'], 
                    'file_name': name_file,
                    'photo': {
                        'likes': i['likes']['count'],
                        'url': i['sizes'][-1]['url']}})
                count += 1
                
                if self.number == 'all':
                    pass
                elif count == self.number:
                    break
        return my_list

    def save_photos_to_yandex(self, object_list):

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        name_folder = self.create_folder()

        for element in object_list:
            # name_file = element['photo']['url'].split('/')[-1]
            # name_path = name_folder + '/' + name_file
            name_path = name_folder + '/' + element['file_name']
            parameters = {'path': name_path, 'overwrite': 'true', 'templated': True}

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
        requests.put(url, headers=self.headers_yandex, params=parameters)
        return name_folders

def input_id_and_token():
    id_user = input("Введите ID пользователя: ")
    if id_user == '':
        id_user = 33579332
        # id_user = 1105788
    token_yandex = input("Введите token с полигона Yandex: ")
    if token_yandex == '':
        with open('token_yandex.txt') as file:
            token_yandex = file.readline()
    return id_user, token_yandex

if __name__ == '__main__':
    id_user, token_yandex = input_id_and_token()
    my_token = TokenForApi(token_yandex, number=3)
    object = my_token.get_photos_to_vk(id_user)
    # pprint.pprint(object)
    my_token.save_photos_to_yandex(object)
    