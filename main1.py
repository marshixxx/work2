from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from database import *
 
vk_token = "vk1.a.M6-dUrKpYL1cg11BOYqA-FFkgBe4c8XUC4qf34yyygfJrxapsVPHsfTwvFWZ_RIIbdDi1pLmoC1aFvbTuoIMN0M_lON-xXoLBK0OJMul8cf7ThX76q-bdEoHuHZSK5wOjX30u5hLHqxyO2kx9sTC6d9aZUSh8Y6NTsPsp5cdzY4sQAZNKAws-LIhbIJQejU9uP192w2ea2dY6OpDAKP3Ag"
 
vk = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk)
 
class Vkinder:
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=vk_token)
        self.vk_api = self.vk.get_api()
 
    def search_users(self, city, age, sex):
        user = self.vk_api.users.get(fields='city,age,sex')[0]
        if not user.get('city') or not user.get('age') or not user.get('sex'):
            return []
        fields = 'photo_max_orig,sex,bdate'
        if 'bdate' not in user:
            fields += ',bdate'
        users = self.vk_api.users.search(
            q='',
            city=city,
            fields=fields,
            count=1
        )
        if not users['items'] or 'age' not in users['items'][0]:
            return []
        users = self.vk_api.users.search(
            q='',
            city=city,
            fields='photo_max_orig',
            age_from=users['items'][0]['age'] - 5,
            age_to=users['items'][0]['age'] + 5,
            sex=sex,
            count=1000
        )
        return users['items']
 
    def get_user_photos(self, user_id):
        photos = self.vk_api.photos.get(
            owner_id=user_id,
            album_id='profile',
            extended=1,
            count=3
        )
        sorted_photos = sorted(
            photos['items'],
            key=lambda x: x['likes']['count'],
            reverse=True
        )
        photo_links = []
        for photo in sorted_photos:
            photo_links.append(photo['sizes'][-1]['url'])
        return photo_links
 
    def get_user_info(self, user_id):
        try:
            user_info = self.vk_api.users.get(
                user_ids=user_id,
                fields='photo_max_orig,city,sex,bdate',
                count=1
            )
            user_info = user_info[0]
            return user_info
        except IndexError:
            return None
 
def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'attachment': ''})
 
def handle_message(event):
    user_id = event.user_id
    message = event.text.lower()
    if message == 'поиск':
        vkinder = Vkinder(vk_token)
        user_info = vkinder.get_user_info(user_id)
        if user_info:
            users = vkinder.search_users(
                user_info.get('city', {}).get('id'),
                user_info.get('age', 0),
                user_info.get('sex', 0)
            )
            if users:
                for user in users:
                    photos = vkinder.get_user_photos(user['id'])
                    user_info = vkinder.get_user_info(user['id'])
                    if user_info:
                        message = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
                        message += f"Дата рождения: {user_info.get('bdate', '')}\n"
                        message += f"Город: {user_info.get('city', {}).get('title', '')}\n"
                        for photo_link in photos:
                            message += f"Фото: [{photo_link}]({photo_link})\n"
                        message += f"Ссылка на профиль: https://vk.com/id{user['id']}"
                        write_msg(user_id, message)
                        save_search_results(create_connection(), user_id, user['id'], user_info.get('first_name', ''), user_info.get('last_name', ''), user_info.get('bdate', ''), user_info.get('city', {}).get('title', ''))
            else:
                write_msg(user_id, "По вашему запросу никого не найдено")
        else:
            write_msg(user_id, "Для использования данной команды вам необходимо заполнить свой профиль")
    else:
        write_msg(user_id, "Я вас не понимаю. Введите корректную команду")
 
def handle_error(event):
    print(event)
 
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        try:
            handle_message(event)
        except Exception as e:
            handle_error(e)