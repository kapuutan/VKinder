import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from sqlalchemy.orm import sessionmaker
from database import User, Base, engine
from vk_api.keyboard import VkKeyboard
from config import VK_TOKEN
from VKinder_interface import search_users

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk)
Session = sessionmaker(bind=engine)

def send_message(user_id, message, attachment=None):
    vk.messages.send(user_id=user_id, message=message, random_id=vk_api.utils.get_random_id(), attachment=attachment)

def get_user_info(user_id):
    user_info = vk.users.get(user_id=user_id, fields='photo_max, hometown, bdate, sex, relation')
    if not user_info or 'response' not in user_info:
        return None
    return user_info['response'][0]

def get_top_photos(user_id):
    photos = vk.photos.get(owner_id=user_id, album_id='profile', extended=1, count=1000)
    if not photos or 'response' not in photos:
        return None
    photos = sorted([photo for photo in photos['response']['items'] if 'likes' in photo and 'comments' in photo],
                    key=lambda x: x['likes']['count'] + x['comments']['count'], reverse=True)
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

def handle_message_new(event):
    user_info = get_user_info(event.obj.message['from_id'])
    if not user_info:
        send_message(event.obj.message['from_id'], 'Не удалось получить информацию о пользователе.')
        return

    hometown = user_info.get("hometown")
    if not hometown:
        send_message(event.obj.message['from_id'], 'Введите название города через клавиатуру:')
        return

    age_to = user_info.get("age_to")
    if age_to is None:
        send_message(event.obj.message['from_id'], 'Введи максимальный возраст через клавиатуру:')
        return

    age_from = user_info.get("age_from")
    if age_from is None:
        send_message(event.obj.message['from_id'], 'Введи минимальный возраст через клавиатуру:')
        return

    sex = user_info.get("sex")
    if sex is None:
        send_message(event.obj.message['from_id'], 'Выбери пол искомых людей через клавиатуру:', vk_api.keyboard.VkKeyboard.get_sex_keyboard())
        return

    status = user_info.get("status")
    if status is None:
        send_message(event.obj.message['from_id'], 'Введите семейное положение через клавиатуру:', vk_api.keyboard.VkKeyboard.get_status_keyboard())
        return

    search_params = {'age_from': age_from, 'age_to': age_to, 'sex': sex, 'hometown': hometown, 'status': status}
    users = search_users(**search_params)

    if not users:
        send_message(event.obj.message['from_id'], 'Пользователи не найдены.')
        return

    send_message(event.obj.message['from_id'], 'Найдены следующие пользователи:')
    for user in users:
        send_message(event.obj.message['from_id'], user.first_name + ' ' + user.last_name)
        send_message(event.obj.message['from_id'], f'id: {user.user_id}')
        send_message(event.obj.message['from_id'], 'https://vk.com/id' + str(user.user_id))


