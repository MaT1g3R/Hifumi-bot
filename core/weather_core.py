from time import time
from typing import Union

from discord import Embed
from discord.embeds import EmptyEmbed

from bot import HTTPStatusError, SessionManager
from core.tzwhere_fix import TzWhere
from scripts.helpers import is_num, round_place, time_with_zone

__r = round_place(1)


async def weather(api: str, colour, session_manager: SessionManager,
                  tzw: TzWhere, location: str, localize: dict):
    """
    Get the weather of an location.
    :param api: the openweathermap api key.
    :param colour: colour for the embed.
    :param session_manager: the session manager.
    :param tzw: the TzWhere class to get time zone by coordinates.
    :param location: the location.
    :param localize: the localization strings.
    :return: the weather info of that location.
    """
    url = 'http://api.openweathermap.org/data/2.5/weather?'
    param = {
        'q': location,
        'appid': api
    }
    try:
        res = await session_manager.get_json(url, param)
    except HTTPStatusError as e:
        if e.code == 404:
            return localize['nothing_found']
        else:
            return localize['api_error'].format('Openweathermap') + f'\n{e}'

    data = __weather_data(res)
    if not any(data):
        return localize['nothing_found']
    main, des, icon = data
    name = res.get('name', None)
    visibility = res.get('visibility', None)
    wind = res.get('wind', {})
    wind_speed = wind.get('speed', None)
    wind_deg = wind.get('deg', None)
    wind_gust = wind.get('gust', None)
    rain = res.get('rain', {}).get('3h', None)
    snow = res.get('snow', {}).get('3h', None)
    clouds = res.get('clouds', {}).get('all', None)
    md = __main_data(res)
    temp, pressure, sea_level, grnd_level, humidity, temp_min, temp_max = md
    country, sunrise, sunset = __sys_data(res)
    local_time, sunrise_str, sunset_str = __time_info(
        res, tzw, sunrise, sunset)

    embed = Embed(
        title=f':flag_{country.lower()}: ' + localize['weather_info'] + name,
        colour=colour,
        description=__get_des(local_time, main, des, clouds, localize)
    )

    if icon:
        icon_url = f'http://openweathermap.org/img/w/{icon}.png'
        embed.set_thumbnail(url=icon_url)

    tmp_str = __temp_str(temp, temp_min, temp_max, localize)
    if tmp_str:
        embed.add_field(name=':thermometer: ' + localize['temperature'],
                        value=tmp_str)
    if humidity:
        embed.add_field(name=':droplet: ' + localize['humidity'],
                        value=f'{humidity}%')

    wind_str = __wind_str(wind_speed, wind_deg, wind_gust, localize)
    if wind_str:
        embed.add_field(name=localize['wind'],
                        value=wind_str)

    pressure_str = __pressure_str(pressure, sea_level, grnd_level, localize)
    if pressure_str:
        embed.add_field(name=':hotsprings: ' + localize['pressure'],
                        value=pressure_str)

    if is_num(visibility):
        km = __r(visibility / 1000)
        mile = __r(visibility * 0.000621371)
        embed.add_field(name=localize['visibility'],
                        value=f'{km} km | {mile} mile')

    precipitation_str = __precipitation_str(rain, snow, localize)
    if precipitation_str:
        embed.add_field(name=localize['precipitation'], value=precipitation_str)

    if sunrise_str or sunset_str:
        name = localize['sun']
        if sunrise_str:
            lt = localize['sunrise']
            sunrise_str = f':sunrise: {lt}: ' + sunrise_str
        if sunset_str:
            lt = localize['sunset']
            sunset_str = f':city_sunset: {lt}: ' + sunset_str
        sun_val = [s for s in (sunrise_str, sunset_str) if s]
        val = '\n'.join(sun_val)
        embed.add_field(name=name, value=val, inline=False)
    return embed


def __get_des(local_time, main, des, clouds, localize):
    """

    :param local_time:
    :param main:
    :param des:
    :param clouds:
    :param localize:
    :return:
    """
    description = ''
    pad = lambda x: '\n' if x else ''
    if local_time:
        lt = localize['local_time']
        description += f':clock: {lt}: {local_time}'
    if main or des:
        lst = [s for s in (main, des) if s]
        description += pad(description) + '**' + ' | '.join(lst) + '**'
    if clouds:
        c_str = ':cloud: ' + localize['clouds'] + f': {clouds}%'
        description += pad(description) + c_str
    return description or EmptyEmbed


def __weather_data(res):
    """
    Get the weather data from the weather api response.
    :param res: the response.
    :return: (main, description, icon)
    """
    data = res.get('weather', None)
    if not data:
        return (None,) * 3
    weather_main, weather_des = [], []
    icon = None
    for d in data:
        tmp_icon = d.get('icon', None)
        if tmp_icon and not icon:
            icon = tmp_icon
        tmp_main = d.get('main', None)
        if tmp_main:
            weather_main.append(tmp_main)
        tmp_des = d.get('description', None)
        if tmp_des:
            weather_des.append(tmp_des)

    return ', '.join(weather_main), ', '.join(weather_des), icon


def __main_data(res):
    """
    Get the main data from the weather api response.
    :param res: the api response.
    :return: temp, pressure, sea_level, grnd_level, humidity, temp_min, temp_max
    """
    if 'main' not in res:
        return (None,) * 7
    data = res['main']
    temp = data.get('temp', None)
    pressure = data.get('pressure', None)
    sea_level = data.get('sea_level', None)
    grnd_level = data.get('grnd_level', None)
    humidity = data.get('humidity', None)
    temp_min = data.get('temp_min', None)
    temp_max = data.get('temp_max', None)
    return temp, pressure, sea_level, grnd_level, humidity, temp_min, temp_max


def __sys_data(res):
    """
    Get the sys data from the weather api response.
    :param res: the api response.
    :return: country, sunrise, sunset
    """
    if 'sys' not in res:
        return (None,) * 3
    data = res['sys']
    country = data.get('country', None)
    sunrise = data.get('sunrise', None)
    sunset = data.get('sunset', None)
    return country, sunrise, sunset


def __time_info(res, tzw, sunrise, sunset):
    """
    Get the time info from the weather api response.
    :param res: the weather api response.
    :param tzw: the TzWhere class to get time zone by coordinates.
    :return: local_time, sunrise_str, sunset_str
    """
    try:
        lat, lon = res['coord']['lat'], res['coord']['lon']
        tz = tzw.tzNameAt(lat, lon, True) or 'UTC'
    except KeyError:
        tz = 'UTC'

    f = lambda x: x.strftime('%H:%M:%S') + ' ' + tz
    local_stamp = res.get('dt', time())
    local_time = f(time_with_zone(local_stamp, tz))
    sunrise_str = f(time_with_zone(sunrise, tz)) if sunrise else None
    sunset_str = f(time_with_zone(sunset, tz)) if sunset else None

    return local_time, sunrise_str, sunset_str


def __temp_str(temp, low, high, localize: dict):
    """
    Convert temptures to string representations.
    :param temp: tempture in kelvin.
    :param low: low tempture in kelvin.
    :param high: high tempture in kelvin.
    :param localize: localization strings.
    :return: string representation of the 3 temps.
    """

    def make_str(t):
        c = lambda kelvin: kelvin - 273.15
        f = lambda kelvin: (kelvin * (9 / 5)) - 459.67
        cs = lambda k: __r(c(k))
        fs = lambda k: __r(f(k))
        return f'**{cs(t)}°C | {fs(t)}°F**'

    res = []
    if is_num(temp):
        res.append(make_str(temp))
    if is_num(low):
        res.append(
            localize['low'] + ': ' + make_str(low)
        )
    if is_num(high):
        res.append(
            localize['high'] + ': ' + make_str(high)
        )
    return '\n'.join(res) if res else None


def __wind_str(speed, deg, gust, localize: dict):
    """
    Get a string repersentation of wind speed.
    :param speed: the wind speed.
    :param deg: the wind direction in degrees.
    :param gust: the wind gust.
    :param localize: the localization strings.
    :return: the string representation of the wind speed.
    """
    if not is_num(speed) and not is_num(deg) and not is_num(gust):
        return None
    speed_str = lambda s: f': {__r(s)} m/s | {__r(2.23694 * s)} mph'
    res = []
    if is_num(deg):
        dir_ = __wind_dir(deg)
        res.append(localize['direction'] + f': {dir_} ({__r(deg)}°)')
    if is_num(speed):
        res.append(localize['speed'] + speed_str(speed))
    if is_num(gust):
        res.append(localize['gust'] + speed_str(gust))
    return '\n'.join(res)


def __wind_dir(deg: Union[int, float]):
    """
    Get wind direction by degree.
    :param deg: the degree.
    :return: the wind direction.
    """
    if 348.75 <= deg or deg < 11.25:
        return 'N'

    if 11.25 <= deg < 33.75:
        return 'NNE'

    if 33.75 <= deg < 56.25:
        return 'NE'

    if 56.25 <= deg < 78.75:
        return 'ENE'

    if 78.75 <= deg < 101.25:
        return 'E'

    if 101.25 <= deg < 123.75:
        return 'ESE'

    if 123.75 <= deg < 146.25:
        return 'SE'

    if 146.25 <= deg < 168.75:
        return 'SSE'

    if 168.75 <= deg < 191.25:
        return 'S'

    if 191.25 <= deg < 213.75:
        return 'SSW'

    if 213.75 <= deg < 236.25:
        return 'SW'

    if 236.25 <= deg < 258.75:
        return 'WSW'

    if 258.75 <= deg < 281.25:
        return 'W'

    if 281.25 <= deg < 303.75:
        return 'WNW'

    if 303.75 <= deg < 326.25:
        return 'NW'

    if 326.25 <= deg < 348.75:
        return 'NNW'


def __pressure_str(pressure, sea_level, grnd_level, localize: dict):
    """
    Get a string representation of atmospheric pressure.
    :param pressure: the atmospheric pressure.
    :param sea_level: the atmospheric pressure at sea level.
    :param grnd_level: the atmospheric pressure at ground level.
    :param localize: the localization strings.
    :return: the string representation of atmospheric pressure.
    """
    if (not is_num(pressure) and
            not is_num(sea_level) and
            not is_num(grnd_level)):
        return None
    res = []
    if is_num(pressure):
        res.append(localize['pressure'] + f': {pressure} hPa')
    if is_num(sea_level):
        res.append(localize['sea_level'] + f': {sea_level} hPa')
    if is_num(grnd_level):
        res.append(localize['grnd_level'] + f': {grnd_level} hPa')
    return '\n'.join(res)


def __precipitation_str(rain, snow, localize: dict):
    """
    Get a string representation of precipitation.
    :param rain: mm of rain.
    :param snow: mm of snow.
    :param localize: localization strings.
    :return: a string representation of precipitation.
    """
    if not is_num(rain) and not is_num(snow):
        return None
    res = []
    if is_num(rain):
        lt = localize['rain']
        res.append(f':cloud_rain: {rain} mm {lt}')
    if is_num(snow):
        lt = localize['snow']
        res.append(f':snowflake: {snow} mm {lt}')
    return '\n'.join(res)
