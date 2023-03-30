while True:
    print('1. Найти людей по критериям')
    print('2. Выйти')
    choice = input('Выберите действие: ')

    if choice == '1':
        city = input('Введите город: ')
        age = int(input('Введите возраст: '))
        sex = int(input('Введите пол (1 - женский, 2 - мужской): '))

        user_info = {'city': city, 'age': age, 'sex': sex}
        users = search_users(user_info)
        send_photos_and_links(user_id, users)

    elif choice == '2':
        print('До свидания!')
        break

    else:
        print('Неверный выбор, попробуйте еще раз')
