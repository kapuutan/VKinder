import psycopg2

def create_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="your_database_name",
        user="your_username",
        password="your_password"
    )
    return conn


def add_user_to_db(user_info, photos):
    conn = create_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (vk_id, first_name, last_name, age, city, photo_1, photo_2, photo_3) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_info['id'], user_info['first_name'], user_info['last_name'], user_info['age'], user_info['city'],
             photos[0] if len(photos) > 0 else None, photos[1] if len(photos) > 1 else None,
             photos[2] if len(photos) > 2 else None)
        )
        conn.commit()
    except Exception as e:
        print(f"Error adding user {user_info['id']} to database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def search_users_in_db(user_info):
    conn = create_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM users WHERE city=%s AND age BETWEEN %s AND %s AND (CASE WHEN %s=1 THEN age>=18 ELSE age<18 END)",
            (user_info['city'], user_info['age']-5, user_info['age']+5, user_info['sex'])
        )
        users = cur.fetchall()
        result = []
        for user in users:
            result.append({
                'id': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'age': user[4],
                'city': user[5],
                'photos': [photo for photo in [user[6], user[7], user[8]] if photo is not None]
            })
        return result
    except Exception as e:
        print(f"Error searching users in database: {e}")
    finally:
        cur.close()
        conn.close()
def find_users_and_send_photos(user_id, user_info):
    users = search_users(user_info)
    db.insert_users(users) 
    top_users = db.get_top_users(user_info['id'])
    send_photos_and_links(user_id, top_users)
