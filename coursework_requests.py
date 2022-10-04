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

    def get_list_albums(self, id_user=None):

        '''На вход получает id пользователя. Возвращает список
        
        альбомов, содержащий id альбома и его размер.
        
        '''

        url = TokenForApi.URL + 'photos.getAlbums?'
        parameters = {'owner_id': id_user}  
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

    def get_photos(self, id_user, id_album='profile', count=5):
        
        '''На вход получает id пользователя, id альбома, количество
        
        фотографий (по умолчанию 5). Возвращает список словарей по
        
        каждой фотографии из альбома (json объект).
        
        '''

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
            
            new_dict['sizes'] = element['sizes'][-1]['type']
            new_dict['url'] = element['sizes'][-1]['url']
            new_dict['likes'] = element['likes']['count']
            new_dict['album_id'] = element['album_id']
                
            list_photos.append(new_dict)
        return list_photos

    def create_name_file(self, dict_photo, list_names):

        '''На вход получает словарь с данными на фотографию и список

        уже занятых имен. Создает уникальное имя файла и добавляет его
        
        в список занятых имен. Возвращает уникальное имя для файла.
        
        '''
        name_file = dict_photo['url'].split('/')[-1].split('?')[0]
        index = name_file.find('.')
        name_file = name_file[index:]
        name_file = str(dict_photo['likes']) + name_file

        if name_file in list_names:
            name = name_file.split('.')
            local_time = f'_({time.time()})'
            name[0] += local_time
            name_file = '.'.join(name)
        
        list_names.append(name_file)
        return name_file

    def save_photos_to_yandex(self, list_photos):

        '''Метод принимает список словарей с данными на фотографии.
        
        Осуществляет post запрос на Api Yandex. Создает имена файлов
        
        и загружает фотографии по ссылкам из списка словарей на Yandex.

        Возвращает json объект (имя файла и его размер). Реализован 

        прогресс бар.
        
        '''

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        list_names = []

        print("Загрузка фотографий из альбома на Yandex:")
        with alive_bar(len(list_photos), force_tty=True, dual_line=True) as bar:
            for element in list_photos:
                name_folder = self.create_folder(element['album_id'])
                name_file = self.create_name_file(element, list_names)
                name_path = name_folder + '/' + name_file
                parameters = {
                    'path': name_path, 
                    'url': element['url']
                    }
                bar.text = f'Download {name_path}, please wait ...'

                response = requests.post(
                    url, headers=self.headers_yandex, params=parameters)
            
                del element['likes'], element['url']
                element['file_name'] = name_file
                bar()
        return list_photos

    def create_folder(self, id_album):

        '''Метод класса создает папку на Yandex диск с именем текущей
        
        даты.
        
        '''

        url = 'https://cloud-api.yandex.net/v1/disk/resources' 
        name_folders = list(time.gmtime()[0:3])[::-1]
        name_folders = '.'.join(list(map(str, name_folders)))
        name_folders += '_' + str(id_album)
        parameters = {'path': name_folders}
        requests.put(url, headers=self.headers_yandex, params=parameters)
        return name_folders


def input_id_and_token():

    '''Функция реализует пользовательский ввод номера ID профиля и 
    
    токена с полигона Yandex (при вводе пустого поля, токен считывается
    
    из файла token_yandex.txt)

    '''

    id_user = input("Введите ID пользователя: ")
    if id_user == '':
        # id_user = None
        id_user = 2726270
    token_yandex = input("Введите token с полигона Yandex: ")
    if token_yandex == '':
        with open('token_yandex.txt') as file:
            token_yandex = file.readline()
    return id_user, token_yandex

if __name__ == '__main__':
    id_user, token_yandex = input_id_and_token()
    object = TokenForApi(token_yandex)
    my_albums = object.get_list_albums(id_user)
    # pprint.pprint(my_albums)
    # my_photo = object.get_photos(id_user, count=15)
    # pprint.pprint(my_photo)
    # c = object.save_photos_to_yandex(my_photo)
    # pprint.pprint(c)
    for element in my_albums:
        my_photo = object.get_photos(id_user, element['id'], 10)
        object.save_photos_to_yandex(my_photo)
    