import requests

temperature_rules = [
    (-10, 'Очень холодно. Одевайте все самое теплое.'),
    (0, 'Холодно, стоит взять теплую куртку и шарф.'),
    (10, 'Прохладно, стоит одеться потеплее.'),
    (15, 'Приятная погода, но куртка не помешает.'),
    (20, 'Тепло. Легкая кофта подойдет.'),
    (27, 'Очень тепло. Футболка и шорты - то, что нужно.'),
    (50, 'Очень жарко, держитесь в тени и возьмите с собой воды.')
]


def cityname_to_coord(api_key, city_name):
    url_decode = f"https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={city_name}"
    with requests.get(url_decode) as resp:
        json_result = resp.json()
        coord = json_result["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        result_coordinates = coord.split()
        return result_coordinates
