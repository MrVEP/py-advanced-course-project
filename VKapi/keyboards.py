import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from credentials import group_token

vk_session = vk_api.VkApi(token=group_token)
vk = vk_session.get_api()


def getting_started(user_id: int):
    getting_started_keyboard = VkKeyboard(one_time=True)

    getting_started_keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)

    vk.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        keyboard=getting_started_keyboard.get_keyboard(),
        message='Чтобы запустить бота, нажмите "Начать"'
    )


def choose_sex(user_id: int):
    choose_sex_keyboard = VkKeyboard(one_time=True)

    choose_sex_keyboard.add_button('М', color=VkKeyboardColor.PRIMARY)
    choose_sex_keyboard.add_button('Ж', color=VkKeyboardColor.NEGATIVE)

    vk.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        keyboard=choose_sex_keyboard.get_keyboard(),
        message='Выберите Ваш пол:'
    )


def confirm_info(user_id: int):
    confirm_info_keyboard = VkKeyboard(one_time=True)

    confirm_info_keyboard.add_button('Все верно!', color=VkKeyboardColor.POSITIVE)
    confirm_info_keyboard.add_button('Изменить данные', color=VkKeyboardColor.NEGATIVE)

    vk.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        keyboard=confirm_info_keyboard.get_keyboard(),
        message='Подтвердите Ваши данные:'
    )


def search_or_change(user):
    search_or_change_keyboard = VkKeyboard(one_time=True)

    search_or_change_keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)
    search_or_change_keyboard.add_button('Изменить данные', color=VkKeyboardColor.NEGATIVE)

    vk.messages.send(
        user_id=user.id,
        random_id=get_random_id(),
        keyboard=search_or_change_keyboard.get_keyboard(),
        message=f'Ваши данные: \nВозраст: {user.age} \nГород: {user.city}'
                f'\nПол: {"М" if user.sex == 2 else "Ж"}'
                f'\nДиапазон: от {user.age_range[0]} до {user.age_range[1]}'
    )


def change_info(user):
    change_info_keyboard = VkKeyboard(one_time=True)

    change_info_keyboard.add_button('Все верно!', color=VkKeyboardColor.POSITIVE)

    change_info_keyboard.add_line()

    change_info_keyboard.add_button('Пол', color=VkKeyboardColor.PRIMARY)
    change_info_keyboard.add_button('Возраст', color=VkKeyboardColor.PRIMARY)

    change_info_keyboard.add_line()

    change_info_keyboard.add_button('Город', color=VkKeyboardColor.PRIMARY)
    change_info_keyboard.add_button('Диапазон', color=VkKeyboardColor.PRIMARY)

    vk.messages.send(user_id=user.id,
                     message=f'Ваши данные: \nВозраст: {user.age}'
                             f'\nГород: {user.city}'
                             f'\nПол: {"М" if user.sex == 2 else "Ж"}'
                             f'\nДиапазон: от {user.age_range[0]} до {user.age_range[1]}',
                     random_id=get_random_id())

    vk.messages.send(
        user_id=user.id,
        random_id=get_random_id(),
        keyboard=change_info_keyboard.get_keyboard(),
        message='Выберите параметр для изменения:'
    )