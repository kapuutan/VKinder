from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


TOKEN = input('Token: ')
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk)


def send_message(user_id, message):
    vk.messages.send(user_id=user_id, message=message, random_id=randrange(10 ** 7))


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
    users = vk.users.search(q='', count=1000, city=user_info['city']['id'], sex=3-user_info['sex'], age_from=user_info['age']-5, age_to=user_info['age']+5, status=user_info['relation'])
    if 'response' not in users or not users['response']:
        return []
    result = []
    for user in users['response']['items']:
        user_id = user['id']
        if user_id == user_info['id']:
            continue
        user_info = get_user_info(user_id)
        if not user_info or user_info['is_closed'] or 'deactivated' in user_info:
            continue
        top_photos = get_top_photos(user_id)
        if not top_photos:
            continue
        result.append({'id': user_id, 'first_name': user_info['first_name'], 'last_name': user_info['last_name'], 'age': user_info['age'], 'city': user_info['city']['title'], 'photos': top_photos})
    return result



def send_photos_and_links(user_id, users):
    if len(users) == 0:
        send_message(user_id, 'К сожалению, не удалось найти подходящих людей :(')
    else:
        for user in users:
            message = f"{user['first_name']} {user['last_name']}, {user['age']} лет, г.{user['city']}\n"
            for photo in user['photos']:
                message += f"{photo['likes']} лайков, {photo['comments']} комментариев\n{photo['url']}\n\n"
            message += f"https://vk.com/id{user['id']}"
            send_message(user_id, message)


def find_and_send_users(user_info):

    users = search_users(user_info)


    users = sorted(users, key=lambda u: sum(p['likes'] for p in u['photos']), reverse=True)


    send_photos_and_links(user_info['id'], users[:3])

