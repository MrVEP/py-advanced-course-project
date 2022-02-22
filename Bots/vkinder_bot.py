import vk_api
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


def relationship_bot():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.object.message['from_id']
            if event.object.message['text'] == 'Начать':
                if user_id not in db.get_all_users_id():
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
                    db.add_user(vk_user)
                else:
                    # Если бот имеет дело с уже существующим пользователем, то он просто подтянет все данные из БД
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
                            db.change_info(vk_user)
                            break
                        elif event.object.message['text'] == 'Начать поиск':
                            results = vk_api_scripts.search_pair(vk_user)
                            # Получив список id подходящих пар, бот найдет первое id, которого еще нет в БД,
                            # добавит его туда и выдаст полученный результат, после чего завершит свою работу.
                            new_pair_id = False
                            for result in results:
                                if result not in db.get_old_results(vk_user.id):
                                    new_pair_id = result
                                    break
                            if not new_pair_id:
                                vk.messages.send(user_id=user_id,
                                                 message=f'Новых результатов не получено.'
                                                         f'\nИзмените возрастной диапазон.',
                                                 random_id=get_random_id())
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
                keyboards.getting_started(user_id)
            else:
                keyboards.getting_started(user_id)
