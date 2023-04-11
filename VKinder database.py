import sqlite3

conn = sqlite3.connect('vkontakte.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                city INTEGER,
                age_from INTEGER,
                age_to INTEGER,
                sex INTEGER,
                status INTEGER,
                FOREIGN KEY (id) REFERENCES profiles (id)
            );""")

cur.execute("""CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                city TEXT,
                sex INTEGER,
                status INTEGER,
                photo_url TEXT,
                likes INTEGER,
                comments INTEGER
            );""")

def add_user(id, city, age_from, age_to, sex, status):
    cur.execute(f"INSERT INTO users (id, city, age_from, age_to, sex, status) VALUES ({id}, {city}, {age_from}, {age_to}, {sex}, {status});")
    conn.commit()

def get_users_by_id(user_id):
    cur.execute(f"SELECT id FROM users WHERE id={user_id}")
    result = cur.fetchall()
    return result

def get_profiles_by_filters(city, age_from, age_to, sex, status):
    cur.execute(f"SELECT * FROM profiles WHERE city='{city}' AND age BETWEEN {age_from} AND {age_to} AND sex={sex} AND status={status} ORDER BY likes DESC, comments DESC LIMIT 3")
    result = cur.fetchall()
    return result



