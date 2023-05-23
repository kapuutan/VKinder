from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll
from vk_api.keyboard import VkKeyboard
from random import randrange


VK_TOKEN = input('Token: ')
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk)


def send_message(user_id, message):
    vk.messages.send(user_id=user_id, message=message, random_id=randrange(10 ** 7))


def send_photos_and_links(user_id, users):
    if len(users) == 0:
        send_message(user_id, 'К сожалению, не удалось найти подходящих людей :(')
    else:
        for user in users:
            message = f"{user.first_name} {user.last_name}, {user.age} лет, г.{user.hometown}\n"
            photos = vk.photos.get(owner_id=user.user_id, album_id='profile', count=3, rev=1)
            for photo in photos['items']:
                message += f"{photo['likes']['count']} лайков, {photo['comments']['count']} комментариев\n"
                message += f"Ссылка на профиль: https://vk.com/id{user.user_id}\n\n"
            send_message(user_id, message)


def find_users(user_id, age_from, age_to, sex, city_id, status):
    user_info = vk.users.get(user_ids=user_id, fields='city,sex,status')
    if user_info and 'city' in user_info[0]:
        city = user_info[0]['city']['id']
        if city:
            city_id = city
    users = vk.users.search(count=10, sex=sex, age_from=age_from, age_to=age_to, status=status, city=city_id,
                            has_photo=1, fields='id, first_name, last_name, bdate, city, relation, sex')
    send_photos_and_links(user_id, users)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()
            user_id = event.user_id

            if request == "привет":
                send_message(user_id, f"Привет, {user_id}! Я помогу тебе найти человека по интересам.")
                send_message(user_id, "Для начала, скажи свой город:")
            elif request.isdigit() and len(request) == 5:
                city_id = int(request)
                send_message(user_id, "Хорошо, теперь укажи свой возраст:")
            elif request.isdigit() and 14 <= int(request) <= 120:
                age_from = int(request)
                age_to = age_from + 5
                send_message(user_id, "Скажи, какой пол тебе интересен (1 - женский, 2 - мужской):")
            elif request == "1" or request == "2":
                sex = int(request)
                send_message(user_id, "Отлично, теперь укажи семейное положение (0 - не женат/не замужем, 1 - есть парень/есть девушка, 2 - помолвлен/помолв")
            elif request.isdigit() and 14 <= int(request) <= 120:
                age_from = int(request)
                age_to = age_from + 5
                send_message(user_id, "Скажи, какой пол тебе интересен (1 - женский, 2 - мужской):")
            elif request == "1" or request == "2":
                sex = int(request)
                send_message(user_id, "Отлично, теперь укажи семейное положение (0 - не женат/не замужем, 1 - есть парень/есть девушка, 2 - помолвлен/помолвлена, 3 - женат/замужем, 4 - всё сложно, 5 - в активном поиске):")
            elif request.isdigit() and 0 <= int(request) <= 5:
                status = int(request)
                find_users(user_id, age_from, age_to, sex, city_id, status)
            else:
                send_message(user_id, "Я не могу обработать это сообщение. Пожалуйста, попробуй еще раз.")




