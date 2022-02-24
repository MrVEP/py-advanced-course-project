import vk_api
import sqlalchemy
import json
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from VKapi.user_data import VKUser

import database as db
from credentials import group_token, group_id
from VKapi import keyboards, vk_api_scripts

vk_session = vk_api.VkApi(token=group_token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id)


def get_age_range(response: str) -> list[int] or bool:
    response = response.split('-')
    age_range = [0, 0]
    if len(response) != 2:
        return False
    else:
        try:
            for i in range(2):
                age_range[i] = int(response[i])
            if age_range[1] < age_range[0]:
                return False
            else:
                return age_range
        except ValueError:
            return False


def get_backup():
    with open('temp_backup.json', encoding='utf-8') as file:
        data = json.load(file)
        return data


def save_backup(data):
    with open('temp_backup.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def push_backup_to_db():
    data = get_backup()
    empty_backup_template = '''{
      "users": {

      },
      "results": {

      }
    }'''
    for i in data['users'].keys():
        i = int(i)
        temp_user = VKUser(i)
        temp_user.first_name = data['users'][f'{i}'][0]
        temp_user.last_name = data['users'][f'{i}'][1]
        temp_user.age = data['users'][f'{i}'][2]
        temp_user.sex = data['users'][f'{i}'][3]
        temp_user.city = data['users'][f'{i}'][4]
        temp_user.city_id = data['users'][f'{i}'][5]
        temp_user.age_range = data['users'][f'{i}'][6]
        if i not in db.get_all_users_id():
            db.add_user(temp_user)
        else:
            db.change_info(temp_user)
    for i in data['results'].keys():
        for j in data['results'][i]:
            if j not in db.get_old_results(i):
                db.add_result(i, j)
    with open('temp_backup.json', 'w', encoding='utf-8') as file:
        file.write(empty_backup_template)


def relationship_bot():
    db_failed = False
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.object.message['from_id']
            if event.object.message['text'] == 'Начать':
                try:
                    database = db.get_all_users_id()
                    push_backup_to_db()
                except sqlalchemy.exc.OperationalError:
                    db_failed = True
                    data = get_backup()
                    vk.messages.send(user_id=user_id,
                                     message=f'К сожалению, база данных на данный момент не доступна. '
                                             f'Вы все еще можете воспользоваться ботом, однако результаты могут '
                                             f'повторяться с выдаными раннее.',
                                     random_id=get_random_id())
                    database = []
                    for i in data['users'].keys():
                        database.append(int(i))
                if user_id not in database:
                    # Если бот имеет дело с новым пользователем, то сначала он заполнит его личные данные
                    # со страницы вк и спросит то, что не сможет получить с нее.
                    vk_user = VKUser(user_id)
                    vk_user.pull_from_vk_page()
                    if not vk_user.age:
                        correct_format = False
                        while not correct_format:
                            vk.messages.send(user_id=user_id,
                                             message=f'Укажите ваш возраст:',
                                             random_id=get_random_id())
                            for event in longpoll.listen():
                                if event.type == VkBotEventType.MESSAGE_NEW:
                                    new_info = event.object.message['text']
                                    break
                            try:
                                new_info = int(new_info)
                                correct_format = True
                                vk_user.age = new_info
                            except ValueError:
                                vk.messages.send(user_id=user_id,
                                                 message=f'Некорректные данные!',
                                                 random_id=get_random_id())
                        vk_user.age_range = [vk_user.age, vk_user.age]
                    if not vk_user.sex:
                        correct_sex = False
                        while not correct_sex:
                            keyboards.choose_sex(user_id)
                            for event in longpoll.listen():
                                if event.type == VkBotEventType.MESSAGE_NEW:
                                    new_info = event.object.message['text']
                                    if new_info == 'М':
                                        vk_user.sex = 2
                                        correct_sex = True
                                        break
                                    elif new_info == 'Ж':
                                        vk_user.sex = 1
                                        correct_sex = True
                                        break
                    if not vk_user.city:
                        correct_city = False
                        while not correct_city:
                            vk.messages.send(user_id=user_id, message=f'Укажите ваш город:', random_id=get_random_id())
                            for event in longpoll.listen():
                                if event.type == VkBotEventType.MESSAGE_NEW:
                                    new_info = event.object.message['text']
                                    break
                            city_id = vk_api_scripts.get_city_id(new_info)
                            if city_id:
                                vk_user.city = new_info
                                vk_user.city_id = city_id
                                correct_city = True
                            else:
                                vk.messages.send(user_id=user_id,
                                                 message=f'Некорректные данные!',
                                                 random_id=get_random_id())
                    vk.messages.send(user_id=user_id,
                                     message=f'Ваши данные: \nВозраст: {vk_user.age} \nГород: {vk_user.city}'
                                             f'\nПол: {"М" if vk_user.sex == 2 else "Ж"}'
                                             f'\nДиапазон: от {vk_user.age_range[0]} до {vk_user.age_range[1]}',
                                     random_id=get_random_id())
                    response = None
                    keyboards.confirm_info(user_id)
                    # После получения всех данных, бот позволяет изменить любой из параметров
                    while response != 'Все верно!':
                        for event in longpoll.listen():
                            if event.type == VkBotEventType.MESSAGE_NEW:
                                response = event.object.message['text']
                                if response == 'Пол':
                                    correct_sex = False
                                    while not correct_sex:
                                        keyboards.choose_sex(user_id)
                                        for event in longpoll.listen():
                                            if event.type == VkBotEventType.MESSAGE_NEW:
                                                new_info = event.object.message['text']
                                                if new_info == 'М':
                                                    vk_user.sex = 2
                                                    correct_sex = True
                                                    break
                                                elif new_info == 'Ж':
                                                    vk_user.sex = 1
                                                    correct_sex = True
                                                    break
                                if response == 'Возраст':
                                    correct_format = False
                                    while not correct_format:
                                        vk.messages.send(user_id=user_id, message=f'Укажите ваш возраст:',
                                                         random_id=get_random_id())
                                        for event in longpoll.listen():
                                            if event.type == VkBotEventType.MESSAGE_NEW:
                                                new_info = event.object.message['text']
                                                break
                                        try:
                                            new_info = int(new_info)
                                            correct_format = True
                                            vk_user.age = new_info
                                        except ValueError:
                                            vk.messages.send(user_id=user_id,
                                                             message=f'Некорректные данные!',
                                                             random_id=get_random_id())
                                if response == 'Город':
                                    correct_city = False
                                    while not correct_city:
                                        vk.messages.send(user_id=user_id, message=f'Укажите ваш город:',
                                                         random_id=get_random_id())
                                        for event in longpoll.listen():
                                            if event.type == VkBotEventType.MESSAGE_NEW:
                                                new_info = event.object.message['text']
                                                break
                                        city_id = vk_api_scripts.get_city_id(new_info)
                                        if city_id:
                                            vk_user.city = new_info
                                            vk_user.city_id = city_id
                                            correct_city = True
                                        else:
                                            vk.messages.send(user_id=user_id,
                                                             message=f'Некорректные данные!',
                                                             random_id=get_random_id())
                                if response == 'Диапазон':
                                    vk_user.age_range = [None, None]
                                    correct_range = False
                                    while not correct_range:
                                        vk.messages.send(user_id=user_id, message=f'Укажите диапазон возраста '
                                                                                  f'для поиска от Х до Y лет '
                                                                                  f'в формате "X-Y":',
                                                         random_id=get_random_id())
                                        for event in longpoll.listen():
                                            if event.type == VkBotEventType.MESSAGE_NEW:
                                                received_range = event.object.message['text']
                                                break
                                        vk_user.age_range = get_age_range(received_range)
                                        if not vk_user.age_range[0] or not vk_user.age_range[1]:
                                            vk.messages.send(user_id=user_id,
                                                             message=f'Некорректные данные!',
                                                             random_id=get_random_id())
                                        else:
                                            correct_range = True
                                if response != 'Все верно!':
                                    keyboards.change_info(vk_user)
                                break
                    # Сформировав класс VKUser со всеми данными, бот запишет их в БД
                    if db_failed:
                        data['users'][f'{user_id}'] = [vk_user.first_name,
                                                  vk_user.last_name,
                                                  vk_user.age,
                                                  vk_user.sex,
                                                  vk_user.city,
                                                  vk_user.city_id,
                                                  vk_user.age_range]
                        data['results'][f'{user_id}'] = []
                    else:
                        db.add_user(vk_user)
                else:
                    # Если бот имеет дело с уже существующим пользователем, то он просто подтянет все данные из БД
                    if db_failed:
                        vk_user = VKUser(user_id)
                        vk_user.first_name = data['users'][f'{user_id}'][0]
                        vk_user.last_name = data['users'][f'{user_id}'][1]
                        vk_user.age = data['users'][f'{user_id}'][2]
                        vk_user.sex = data['users'][f'{user_id}'][3]
                        vk_user.city = data['users'][f'{user_id}'][4]
                        vk_user.city_id = data['users'][f'{user_id}'][5]
                        vk_user.age_range = data['users'][f'{user_id}'][6]
                    else:
                        vk_user = db.get_user_info(user_id)
                    vk.messages.send(user_id=user_id, message=f'С возвращением, {vk_user.first_name}!',
                                     random_id=get_random_id())
                keyboards.search_or_change(vk_user)
                # Прежде чем начинать поиск пары, бот снова предложит изменить какие-либо данные
                for event in longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        if event.object.message['text'] == 'Изменить данные':
                            response = None
                            while response != 'Все верно!':
                                keyboards.change_info(vk_user)
                                for event in longpoll.listen():
                                    if event.type == VkBotEventType.MESSAGE_NEW:
                                        response = event.object.message['text']
                                        if response == 'Пол':
                                            correct_sex = False
                                            while not correct_sex:
                                                keyboards.choose_sex(user_id)
                                                for event in longpoll.listen():
                                                    if event.type == VkBotEventType.MESSAGE_NEW:
                                                        new_info = event.object.message['text']
                                                        if new_info == 'М':
                                                            vk_user.sex = 2
                                                            correct_sex = True
                                                            break
                                                        elif new_info == 'Ж':
                                                            vk_user.sex = 1
                                                            correct_sex = True
                                                            break
                                        if response == 'Возраст':
                                            correct_format = False
                                            while not correct_format:
                                                vk.messages.send(user_id=user_id, message=f'Укажите ваш возраст:',
                                                                 random_id=get_random_id())
                                                for event in longpoll.listen():
                                                    if event.type == VkBotEventType.MESSAGE_NEW:
                                                        new_info = event.object.message['text']
                                                        break
                                                try:
                                                    new_info = int(new_info)
                                                    correct_format = True
                                                    vk_user.age = new_info
                                                except ValueError:
                                                    vk.messages.send(user_id=user_id,
                                                                     message=f'Некорректные данные!',
                                                                     random_id=get_random_id())
                                        if response == 'Город':
                                            correct_city = False
                                            while not correct_city:
                                                vk.messages.send(user_id=user_id, message=f'Укажите ваш город:',
                                                                 random_id=get_random_id())
                                                for event in longpoll.listen():
                                                    if event.type == VkBotEventType.MESSAGE_NEW:
                                                        new_info = event.object.message['text']
                                                        break
                                                city_id = vk_api_scripts.get_city_id(new_info)
                                                if city_id:
                                                    vk_user.city = new_info
                                                    vk_user.city_id = city_id
                                                    correct_city = True
                                                else:
                                                    vk.messages.send(user_id=user_id,
                                                                     message=f'Некорректные данные!',
                                                                     random_id=get_random_id())
                                        if response == 'Диапазон':
                                            vk_user.age_range = [None, None]
                                            correct_range = False
                                            while not correct_range:
                                                vk.messages.send(user_id=user_id, message=f'Укажите диапазон возраста '
                                                                                          f'для поиска от Х до Y лет '
                                                                                          f'в формате "X-Y":',
                                                                 random_id=get_random_id())
                                                for event in longpoll.listen():
                                                    if event.type == VkBotEventType.MESSAGE_NEW:
                                                        received_range = event.object.message['text']
                                                        break
                                                vk_user.age_range = get_age_range(received_range)
                                                if not vk_user.age_range[0] or not vk_user.age_range[1]:
                                                    vk.messages.send(user_id=user_id,
                                                                     message=f'Некорректные данные!',
                                                                     random_id=get_random_id())
                                                else:
                                                    correct_range = True
                                        break
                            if db_failed:
                                data['users'][user_id] = [vk_user.first_name,
                                                          vk_user.last_name,
                                                          vk_user.age,
                                                          vk_user.sex,
                                                          vk_user.city,
                                                          vk_user.city_id,
                                                          vk_user.age_range]
                            else:
                                db.change_info(vk_user)
                            break
                        elif event.object.message['text'] == 'Начать поиск':
                            results = vk_api_scripts.search_pair(vk_user)
                            # Получив список id подходящих пар, бот найдет первое id, которого еще нет в БД,
                            # добавит его туда и выдаст полученный результат, после чего завершит свою работу.
                            new_pair_id = False
                            if db_failed:
                                old_results = data['results'][f'{user_id}']
                            else:
                                old_results = db.get_old_results(vk_user.id)
                            for result in results:
                                if result not in old_results:
                                    new_pair_id = result
                                    break
                            if not new_pair_id:
                                vk.messages.send(user_id=user_id,
                                                 message=f'Новых результатов не получено.'
                                                         f'\nИзмените возрастной диапазон.',
                                                 random_id=get_random_id())
                            else:
                                if db_failed:
                                    data['results'][f'{user_id}'].append(new_pair_id)
                                else:
                                    db.add_result(vk_user.id, new_pair_id)
                                pair_top_pics = vk_api_scripts.get_result_info(new_pair_id)
                                vk.messages.send(user_id=user_id,
                                                 message=f'Найден подходящий результат: '
                                                         f'vk.com/id{new_pair_id}',
                                                 attachment=[f'{pair_top_pics[0]}',
                                                             f'{pair_top_pics[1]}',
                                                             f'{pair_top_pics[2]}'],
                                                 random_id=get_random_id())
                            break
                if db_failed:
                    save_backup(data)
                keyboards.getting_started(user_id)
            else:
                keyboards.getting_started(user_id)
