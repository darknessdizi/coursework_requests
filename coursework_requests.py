import requests
import time
from alive_progress import alive_bar
import pprint


class TokenForApi:

    '''Класс для работы с Api VK и Api Yandex'''

    URL = 'https://api.vk.com/method/'

    def __init__(self, token, version='5.194'):

        '''Конструктор класса. На вход получает токен для работы с 
        
        Yandex, версию Api для VK (по умолчанию версия 5.194). Конструктор

        считывает токен для Api VK из файла token_vk.txt.
        
        '''

        with open('token_vk.txt') as file:
            self.token_vk = file.readline()
        self.token_yandex = token

        self.params_vk = {
            'access_token': self.token_vk,
            'v': version}

        self.headers_yandex = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_yandex}'}

    def get_list_albums(self, id=None):

        '''На вход получает id пользователя. Возвращает список
        
        альбомов, содержащий id альбома и его размер.
        
        '''

        url = TokenForApi.URL + 'photos.getAlbums?'
        parameters = {'owner_id': id}  
        list_albums = []  

        response = requests.get(url, params={
            **self.params_vk, **parameters}).json()
        time.sleep(0.33)

        for element in response['response']['items']:
            new_dict = {}
            new_dict['id'] = element['id']
            new_dict['size'] = element['size']
            list_albums.append(new_dict)
        return list_albums

    def get_photos(self, id_user, id_album, count=5):
        
        '''На вход получает id пользователя, id альбома, количество
        
        фотографий (по умолчанию 5). Возвращает список фотографий 
        
        из альбома.
        
        '''

        def _my_dict(album_id, file_name, type, url, sizes=None,):
            _dict = {}
            _dict['album_id'] = album_id
            _dict['int_sizes'] = sizes
            _dict['file_name'] = file_name
            _dict['sizes'] = type
            _dict['url'] = url
            return _dict

        url = TokenForApi.URL + 'photos.get?'
        parameters = {
            'owner_id': id_user,
            'album_id': id_album,
            'extended': 1,
            'photo_sizes': 1,
            'count': count}  
        list_photos = [] 

        response = requests.get(url, params={
            **self.params_vk, **parameters}).json()
        time.sleep(0.33)

        if 'error' in response:
            print(
                '\nВнимание!!! Ошибка запроса Api VK: ', 
                response['error']['error_msg'], end='\n\n')

        for element in response['response']['items']:
            new_dict = {}
            for i in element['sizes']:
                if i['width'] and i['height'] != 0:
                    sizes = i['width'] / i['height']
                    if 'int_sizes' in new_dict:
                        if sizes > new_dict['int_sizes']:
                            new_dict = _my_dict(
                                album_id=element['album_id'], sizes=sizes,
                                file_name=self.create_name_file(element['likes']['count'], i['url']),
                                type=i['type'], url=i['url']
                                )
                    else:
                        new_dict = _my_dict(
                                album_id=element['album_id'], sizes=sizes,
                                file_name=self.create_name_file(element['likes']['count'], i['url']),
                                type=i['type'], url=i['url']
                                )
                    del new_dict['int_sizes']
                else:
                    new_dict = _my_dict(
                        album_id=element['album_id'], type=i['type'],
                        file_name=self.create_name_file(element['likes']['count'], i['url']),
                        url=i['url']
                        )
            list_photos.append(new_dict)
        return list_photos

    def create_name_file(self, likes, url):
        name_file = url.split('/')[-1].split('?')[0]
        index = name_file.find('.')
        name_file = name_file[index:]
        name_file = str(likes) + name_file
        return name_file

    def save_photos_to_yandex(self, list_objects):

        '''Метод принимает список словарей с данными на фотографии.
        
        Осуществляет get и put запрос на Api Yandex. Загружает 
        
        фотографии по ссылкам на Yandex.
        
        '''

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        name_folder = self.create_folder()

        print("Загрузка фотографий на Yandex:")
        with alive_bar(len(list_objects), force_tty=True, dual_line=True) as bar:
            for element in list_objects:
                name_path = name_folder + '/' + element['file_name']
                parameters = {
                    'path': name_path, 
                    'url': element['url']}
                bar.text = f'Download {name_path}, please wait ...'

                response = requests.post(
                    url, headers=self.headers_yandex, params=parameters)
                bar()

    def create_folder(self):

        '''Метод класса создает папку на Yandex диск с именем текущей
        
        даты.
        
        '''

        url = 'https://cloud-api.yandex.net/v1/disk/resources' 
        name_folders = list(time.gmtime()[0:3])[::-1]
        name_folders = '.'.join(list(map(str, name_folders)))
        parameters = {'path': name_folders, 'overwrite': 'false'}
        requests.put(url, headers=self.headers_yandex, params=parameters)
        return name_folders


def input_id_and_token():

    '''Функция реализует пользовательский ввод номера ID профиля и 
    
    токена с полигона Yandex (при вводе пустого поля, токен считывается
    
    из файла token_yandex.txt.)

    '''

    id_user = input("Введите ID пользователя: ")
    if id_user == '':
        # id_user = None
        # id_user = 1105788
        id_user = 2726270
    token_yandex = input("Введите token с полигона Yandex: ")
    if token_yandex == '':
        with open('token_yandex.txt') as file:
            token_yandex = file.readline()
    return id_user, token_yandex

if __name__ == '__main__':
    id_user, token_yandex = input_id_and_token()
    object = TokenForApi(token_yandex)
    obj_1 = object.get_list_albums(id_user)
    # pprint.pprint(obj_1)
    obj_2 = object.get_photos(id_user, 275293270)
    pprint.pprint(obj_2)
    object.save_photos_to_yandex(obj_2)
    