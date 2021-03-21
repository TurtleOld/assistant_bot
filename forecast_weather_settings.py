import requests


def cityname_to_coord(api_key, city_name):
    url_decode = f"https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={city_name}"
    with requests.get(url_decode) as resp:
        json_result = resp.json()
        coord = json_result["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        result_coordinates = coord.split()
        return result_coordinates
