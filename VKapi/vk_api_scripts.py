import vk_api
import time

from credentials import user_token

vk_session = vk_api.VkApi(token=user_token)
vk = vk_session.get_api()


def get_city_id(city: str) -> int or bool:
    response = vk.database.getCities(country_id=1, need_all=1, count=1000, q=f'{city}')
    city_id = False
    for i in response['items']:
        if city == i['title']:
            city_id = i['id']
    return city_id


def search_pair(user) -> list:
    result_ids = []
    response = vk.users.search(count=1000,
                               city=user.city_id,
                               sex=3-user.sex,
                               status=6,
                               age_from=user.age_range[0],
                               age_to=user.age_range[1],
                               fields='last_seen')
    for i in response['items']:
        if not i['is_closed'] and 'last_seen' in i.keys() and i['last_seen']['time'] > (time.time() - 2592000):
            result_ids.append(i['id'])
    return result_ids


def get_result_info(result_id: int) -> list:
    top1 = [-1, -1]
    top2 = [-1, -1]
    top3 = [-1, -1]
    response = vk.photos.get(count=100,
                             extended=1,
                             album_id='profile',
                             owner_id=result_id)
    pics_data = response['items']
    for pic in pics_data:
        popularity_index = pic['likes']['count']+pic['comments']['count']
        if popularity_index > top1[1]:
            top3[0] = top2[0]
            top3[1] = top2[1]
            top2[0] = top1[0]
            top2[1] = top1[1]
            top1[0] = pic['id']
            top1[1] = popularity_index
        elif popularity_index > top2[1]:
            top3[0] = top2[0]
            top3[1] = top2[1]
            top2[0] = pic['id']
            top2[1] = popularity_index
        elif popularity_index > top3[1]:
            top2[0] = pic['id']
            top2[1] = popularity_index
    result = [f'photo{result_id}_{top1[0]}', f'photo{result_id}_{top2[0]}', f'photo{result_id}_{top3[0]}']
    return result
