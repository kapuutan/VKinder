from random import randrange
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


def search_users(user_info):
    with Session() as session:
        query = session.query(User).filter(User.city_id == user_info['city']['id'],
                                            User.sex == user_info['sex'],
                                            User.status == user_info['relation'],
                                            User.age >= user_info['age_from'],
                                            User.age <= user_info['age_to'])
        users = query.all()
    return users


def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_info = get_user_info(event.user_id)
            if not user_info:
                send_message(event.user_id, 'Не удалось получить информацию о пользователе.')
                continue
            if user_info.get('bdate'):
                try:
                    age = (datetime.now() - datetime.strptime(user_info['bdate'], '%d.%m.%Y')).days // 365
                except ValueError:
                    age = None
            else:
                age = None
            if not age:
                send_message(event.user_id, 'Не удалось определить возраст пользователя.')
                continue
            user_info['age'] = age
            user_info['age_from'] = int(input('Введите минимальный возраст искомых людей: '))
            user_info['age_to'] = int(input('Введите максимальный возраст искомых людей: '))
            user_info['sex'] = int(input('Введите пол искомых людей (1 - женский, 2 - мужской): '))
            user_info['status'] = int(input('Введите семейное положение искомых людей (1 - не женат/не замужем, 2 - есть друг/подруга, 3 - помолвлен(а), 4 - женат/замужем, 5 - всё сложно, 6 - в активном поиске, 7 - влюблен(а), 8 - в гражданском браке): '))
            user_info['city_id'] = int(input('Введите id города искомых людей: '))
            search_users(event.user_id, user_info)

