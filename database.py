from vk_api.longpoll import VkEventType
from bot import bot
from db import create_table_seen_person, delete_table_seen_person


def chat_bot():
    for event in bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            user_id = event.user_id
            if request == "поиск" or request == "f":
                bot.get_age_of_user(user_id)
                bot.get_target_city(user_id)
                bot.looking_for_persons(user_id)
                bot.show_found_person(user_id)
            elif request == "удалить" or request == "d":
                delete_table_seen_person()
                create_table_seen_person()
                bot.sending_messages(
                    user_id, f' База данных очищена! Сейчас наберите "Поиск" или F '
                )
            elif request == "смотреть" or request == "s":
                if bot.get_found_person_id() != 0:
                    bot.show_found_person(user_id)
                else:
                    bot.sending_messages(user_id, f" В начале наберите Поиск или f.  ")
            else:
                bot.sending_messages(
                    user_id,
                    f"{bot.title(user_id)} "
                    f"Бот готов к поиску, наберите: \n "
                    f' "Поиск или F" - Поиск людей. \n'
                    f' "Удалить или D" - удаляет старую БД и создает новую. \n'
                    f' "Смотреть или S" - просмотр следующей записи в БД.',
                )


chat_bot()