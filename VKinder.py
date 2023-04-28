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
    user_info = vk.users.get(user_id=user_id, fields='photo_max, city, bdate, sex, relation')
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


def search_users(city_id, age_from, age_to, sex, status):
    with Session() as session:
        query = session.query(User).filter(User.city_id == city_id,
                                            User.sex == sex,
                                            User.status == status,
                                            User.age >= age_from,
                                            User.age <= age_to).limit(50)
        users = query.all()
        query.update({User.user_id: User.user_id + 1})
        session.commit()
    return users


def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_info = get_user_info(event.user_id)
            if not user_info:
                send_message(event.user_id, 'Не удалось получить информацию о пользователе.')
                continue

            age_from = int(input('Введите минимальный возраст искомых людей: '))
            age_to = int(input('Введите максимальный возраст искомых людей: '))
            sex = int(input('Введите пол искомых людей (1 - женский, 2 - мужской): '))
            status = int(input(
                'Введите семейное положение искомых людей (1 - не женат/не замужем, 2 - есть друг/подруга, 3 - помолвлен(а), 4 - женат/замужем, 5 - всё сложно, 6 - в активном поиске, 7 - влюблен(а), 8 - в гражданском браке): '))
            city_id = int(input('Введите id города искомых людей: '))

            with Session() as session:
                query = session.query(User).filter(User.city_id == city_id,
                                                   User.sex == sex,
                                                   User.status == status,
                                                   User.age >= age_from,
                                                   User.age <= age_to)
                users = query.all()

            if not users:
                send_message(event.user_id, 'Пользователи, соответствующие указанным параметрам, не найдены.')
                continue

            used_users = []
            with Session() as session:
                used_users_query = session.query(User).filter(User.vk_id == event.user_id).first()
                if used_users_query:
                    used_users = used_users_query.used_users.split(',')

            for user in users:
                if str(user.id) in used_users:
                    continue

                user_info = get_user_info(user.vk_id)
                if not user_info:
                    continue

                top_photos = get_top_photos(user.vk_id)
                if not top_photos:
                    continue

                message = 'Информация о пользователе:\n\n'
                message += f'Имя: {user_info.get("first_name", "")} {user_info.get("last_name", "")}\n'
                message += f'Возраст: {user.age}\n'
                message += f'Город: {user_info.get("city", {}).get("title", "")}\n'
                message += f'Семейное положение: {user_info.get("relation", "")}\n\n'
                message += 'Топ-3 фотографии:\n\n'
                for photo in top_photos:
                    photo_attachment = vk_api.VkUpload(vk


