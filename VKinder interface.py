from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

token = input('Token: ')
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)})

def send_photos_and_links(user_id, users):
    if len(users) == 0:
        write_msg(user_id, 'К сожалению, не удалось найти подходящих людей :(')
    else:
        for user in users:
            message = f"{user['first_name']} {user['last_name']}, {user['age']} лет, г.{user['city']}\n"
            photos = vk.photos.get(owner_id=user['id'], album_id='profile', count=3, rev=1)
            for photo in photos['items']:
                message += f"{photo['likes']['count']} лайков, {photo['comments']['count']} комментариев\n"
                message += f"Ссылка на профиль: https://vk.com/id{user['id']}\n\n"
            write_msg(user_id, message)

def find_users(user_id, age_from, age_to, sex, city_id, status):
    users = vk.method('users.search', {
        'count': 10,
        'sex': sex,
        'age_from': age_from,
        'age_to': age_to,
        'status': status,
        'city': city_id,
        'has_photo': 1,
        'fields': 'id, first_name, last_name, bdate, city, relation, sex'
    })['items']
    send_photos_and_links(user_id, users)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()
            user_id = event.user_id

            if request == "привет":
                write_msg(user_id, f"Привет, {user_id}! Я помогу тебе найти человека по интересам.")
                write_msg(user_id, "Для начала, скажи свой город:")
            elif request.isdigit() and len(request) == 5:
                city_id = int(request)
                write_msg(user_id, "Хорошо, теперь укажи свой возраст:")
            elif request.isdigit() and 14 <= int(request) <= 120:
                age_from = int(request)
                age_to = age_from + 5
                write_msg(user_id, "Скажи, какой пол тебе интересен (1 - женский, 2 - мужской):")
            elif request == "1" or request == "2":
                sex = int(request)
                write_msg(user_id, "Отлично, теперь укажи семейное положение (0 - не женат/не замужем, 1 - есть парень/есть девушка, 2 - помолвлен/помолвлена, 3 - женат/замужем):")
            elif request.isdigit() and 0 <= int(request) <= 3:
                status = int(request)
                write_msg(user_id, "Отлично, ищу подходящих людей...")
                users = search_users(city_id, age_from, age_to, sex, status)
                send_photos_and_links(user_id, users)
            else:
                write_msg(user_id, "Я не понимаю, что ты от меня хочешь. Попробуй написать 'привет'.")


