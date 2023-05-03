from random import randrange
from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from db import User, Base, engine
from sqlalchemy.orm import sessionmaker
import config

vk_session = vk_api.VkApi(token=config.TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk)
Session = sessionmaker(bind=engine)


def send_message(user_id, message, attachment=None):
    vk.messages.send(user_id=user_id, message=message, random_id=randrange(10 ** 7), attachment=attachment)


def get_user_info(user_id):
    user_info = vk.users.get(user_id=user_id, fields='photo_max, hometown, bdate, sex, relation')
    if 'response' not in user_info or not user_info['response']:
        return None
    return user_info['response'][0]


def get_top_photos(user_id):
    photos = vk.photos.get(owner_id=user_id, album_id='profile', extended=1, count=1000)
    if 'response' not in photos or not photos['response']:
        return None
    photos = sorted(photos['response']['items'], key=lambda x: x['likes']['count'] + x['comments']['count'], reverse=True)
    top_photos = []
    for photo in photos[:3]:
        top_photos.append({'url': photo['sizes'][-1]['url'], 'likes': photo['likes']['count'], 'comments': photo['comments']['count']})
    return top_photos


def search_users(hometown, age_from, age_to, sex, status):
    with Session() as session:
        query = session.query(User).filter(User.hometown == hometown,
                                            User.sex == sex,
                                            User.status == status,
                                            User.age >= age_from,
                                            User.age <= age_to).limit(50)
        users = query.all()
        query.update({User.user_id: User.user_id + 1})
        session.commit()
    return users


def handle_longpoll_event(event):
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_info = get_user_info(event.user_id)
        if not user_info:
            send_message(event.user_id, 'Не удалось получить информацию о пользователе.')
            return

        age_from = int(input('Введите минимальный возраст искомых людей: '))
        age_to = int(input('Введите максимальный возраст искомых людей: '))
        sex = int(input('Введите пол искомых людей (1 - женский, 2 - мужской): '))
        status = int(input(
            'Введите семейное положение искомых людей (1 - не женат/не замужем, 2 - есть друг/подруга, 3 - помолвлен(а), 4 - женат/замужем, 5 - всё сложно, 6 - в активном поиске, 7 - влюблен(а), 8 - в гражданском браке): '))
        hometown = user_info.get("hometown")
        if not hometown:
            hometown = input('Введите название города искомых людей: ')

        users = search_users(hometown, age_from, age_to, sex, status)

        if not users:
            send_message(event.user_id, 'Пользователи, соответствующие указаннымкритериям, не найдены.')
            return
            random_user = random.choice(users)
            user_photos = get_user_photos(random_user['id'])

        if not user_photos:
            send_message(event.user_id, 'Фотографии пользователя не найдены.')
            return

        photo_url = get_largest_photo(user_photos)
        send_message(event.user_id, f"Найден пользователь {random_user['first_name']} {random_user['last_name']} ({random_user['id']}) из города {random_user['city']}")

        send_photo(event.user_id, photo_url)






