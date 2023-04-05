import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS viewed_profiles
                (user_id INTEGER, viewed_id INTEGER,
                 PRIMARY KEY (user_id, viewed_id))''')

def find_users_and_send_photos(user_id, age_from, age_to, city):
    viewed_ids = [row[0] for row in cursor.execute('SELECT viewed_id FROM viewed_profiles WHERE user_id=?', (user_id,))]

    users = vk.users.search(access_token=ACCESS_TOKEN, user_id=user_id, age_from=age_from, age_to=age_to, city=city,
                            count=10, fields='photo_100,photo_200_orig')
    for user in users['items']:
        if user['id'] not in viewed_ids:
            cursor.execute('INSERT INTO viewed_profiles (user_id, viewed_id) VALUES (?, ?)', (user_id, user['id']))
            conn.commit()

            message = f"{user['first_name']} {user['last_name']}, {user['age']} лет, г.{user['city']}\n"
            photos = vk.photos.get(owner_id=user['id'], album_id='profile', count=3, rev=1)
            for photo in photos['items']:
                message += f"{photo['likes']['count']} лайков, {photo['comments']['count']} комментариев\n{photo['sizes'][-1]['url']}\n\n"
            message += f"https://vk.com/id{user['id']}"
            send_message(user_id, message)

def send_photos_and_links(user_id, users):
    if len(users) == 0:
        send_message(user_id, 'К сожалению, не удалось найти подходящих людей :(')
    else:
        for user in users:
            message = f"{user['first_name']} {user['last_name']}, {user['age']} лет, г.{user['city']}\n"
            photos = vk.photos.get(owner_id=user['id'], album_id='profile', count=3, rev=1)
            for photo in photos['items']:
                message += f"{photo['likes']['count']} лайков, {photo['comments']['count']} комментариев\n{photo['sizes'][-1]['url']}\n\n"
            message += f"https://vk.com/id{user['id']}"
            send_message(user_id, message)


