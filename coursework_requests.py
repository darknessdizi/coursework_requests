import requests
import time
from alive_progress import alive_bar


class TokenForApi:

    '''Класс для работы с Api VK и Api Yandex'''

    URL = 'https://api.vk.com/method/'

    def __init__(self, token, number=5, version='5.194'):

        '''Конструктор класса. На вход получает токен для работы с 
        
        Yandex, версию Api для VK (по умолчанию версия 5.194) и 

        количество фотографий для загрузки (по умолчанию 5). Конструктор

        считывает токен для Api VK из файла token_vk.txt.
        
        '''

        with open('token_vk.txt') as file:
            self.token_vk = file.readline()
        self.token_yandex = token
        self.number = number
        self.final_list = []
        self.number_for_bur = number

        self.params_vk = {
            'access_token': self.token_vk,
            'v': version}

        self.headers_yandex = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_yandex}'}

    def __str__(self):
        my_str = '[{\n'
        for i in self.final_list:
            my_str += f'"file_name": "{i["file_name"]}",\n'
            my_str += f'"size": "{i["size"]}"\n'
        my_str += '}]\n'
        return my_str

    def get_photos_to_vk(self, id=None):

        '''Метод на вход получает номер ID пользователя (по умолчанию
        
        None, текущий пользователь). Метод реализует get запрос на 
        
        Api VK для получения всех фотографий пользователя или указанного
        
        количества. Данные о фотографии (имя, размер, url и likes) 
        
        добавляются в словарь. Словари добавляются в поле final_list.
        
        '''

        url = TokenForApi.URL + 'photos.getAll?'
        parameters = {
            'owner_id': id ,
            'extended': 1,
            'offset': 0,
            'count': 200,
            'photo_sizes': 1}
        list_name = []

        items = int(self.number_for_bur / 200)
        if self.number_for_bur % 200 != 0:
            items += 1
        print("Получение списка фотографий:")
        with alive_bar(items, force_tty=True) as bar:
            while True:                 
                response = requests.get(url, params={
                    **self.params_vk, **parameters}).json()
                time.sleep(0.33)
        
                if 'error' in response:
                    print(
                        '\nВнимание!!! Ошибка запроса Api VK: ', 
                        response['error']['error_msg'], end='\n\n')

                list_name = self._add_photo_to_list(response, list_name) 
                bar()

                if len(self.final_list) == response['response']['count']:
                    break
                elif len(self.final_list) == self.number:
                    break
                elif len(self.final_list) % 200 == 0:
                    parameters['offset'] += 200

    def _add_photo_to_list(self, response, list_name):

        '''Метод на вход получает json объект из которого достается url
        
        фотографии, определяется максимальный размер, расширение файла,
        
        добавляется имя на основе likes фотографии. Проводится проверка
        
        на наличие одинаковых имен. Данные на фотографии объединяются 
        
        в словарь и добавляются в поле класса final_list. 

        '''

        for i in response['response']['items']:
            name_file = i['sizes'][-1]['url'].split('/')[-1].split('?')[0]
            index = name_file.find('.')
            name_file = name_file[index:]
            name_file = f'{i["likes"]["count"]}{name_file}'
            while True:
                if name_file in list_name:
                    name = name_file.find('(')
                    if name == -1:
                        name_file = name_file.split('.')
                        name_file[0] += '(2)'
                        name_file = '.'.join(name_file)
                    else:
                        name_file = name_file.split('.')
                        count = int(name_file[0][(
                            name_file[0].rfind('(')) + 1:-1]) + 1
                        name_file[0] = str(i["likes"]["count"]) + f'({count})'
                        name_file = '.'.join(name_file)
                else:
                    self.final_list.append({
                        'size': i['sizes'][-1]['type'], 
                        'file_name': name_file,
                        'photo': {
                            'likes': i['likes']['count'],
                            'url': i['sizes'][-1]['url']}})
                    list_name.append(name_file)
                    break
            if len(self.final_list) == self.number:
                    break
        return list_name

    def save_photos_to_yandex(self, object_list):

        '''Метод принимает список словарей с данными на фотографии.
        
        Осуществляет get и put запрос на Api Yandex. Загружает 
        
        фотографии по ссылкам на Yandex.
        
        '''

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        name_folder = self.create_folder()

        print("Загрузка фотографий на Yandex:")
        with alive_bar(len(object_list), force_tty=True, dual_line=True) as bar:
            for element in object_list:
                name_path = name_folder + '/' + element['file_name']
                parameters = {'path': name_path, 'overwrite': 'true'}
                bar.text = f'Download {name_path}, please wait ...'

                response = requests.get(
                    url, headers=self.headers_yandex, params=parameters).json()
                response = requests.put(
                    response['href'], files={'file': element['photo']['url']}, 
                    headers=self.headers_yandex, params=parameters)
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
    object = TokenForApi(token_yandex, 566)
    object.get_photos_to_vk(id_user)
    object.save_photos_to_yandex(object.final_list)
    # print("\n Список файлов:\n", object)
    