"""
Functions for Utilities commands
"""
from json import JSONDecodeError
from random import randint

from discord.embeds import EmptyEmbed
from imdbpie import Imdb
from requests import get

from config import EDAMAM_API
from scripts.discord_functions import build_embed


def number_fact(num, not_found_msg, bad_num_msg, header):
    """
    Find a fact about a number
    :param num: the number
    :param not_found_msg: message if fact is not found
    :param bad_num_msg: message if the number isnt valid
    :param header: the header for the return string
    :return: a string representation for the fact
    """
    try:
        if num != 'random':
            num = int(num)
    except ValueError:
        return bad_num_msg
    url = f'http://numbersapi.com/{num}?json=true'
    while True:
        try:
            res = get(url).json()
            break
        except JSONDecodeError:
            continue
    return header.format(res['number']) + res['text'] if res['found'] \
        else not_found_msg


def imdb(query, api: Imdb, localize):
    """
    Send an api request to imdb using the search query
    :param query: the search query
    :param api: the imdb api object
    :param localize: the localization strings
    :return: the result
    """
    try:
        names = lambda x: ', '.join((p.name for p in x)) if x else 'N/A'
        null_check = lambda x: x if x and not isinstance(x, int) else 'N/A'
        id_ = api.search_for_title(query)[0]['imdb_id']
        res = api.get_title_by_id(id_)
        eps = api.get_episodes(id_) if res.type == 'tv_series' else None
        ep_count = len(eps) if eps is not None else None
        season_count = eps[-1].season if eps is not None else None
        title = null_check(res.title)
        release = null_check(res.release_date)
        runtime = res.runtime
        if runtime is not None:
            hours, seconds = divmod(runtime, 3600)
            minutes = seconds / 60
            runtime_str = '{} {} {} {}'.format(
                round(hours), localize['hours'],
                round(minutes), localize['minutes']
            )
        else:
            runtime_str = 'N/A'
        rated = null_check(res.certification)
        genre = ', '.join(res.genres) if res.genres else 'N/A'
        director = names(res.directors_summary)
        writer = names(res.writers_summary)
        cast = names(res.cast_summary)
        plot = null_check(res.plot_outline)
        poster = res.poster_url
        score = f'{res.rating}/10' if res.rating is not None else 'N/A'
        body = []
        if season_count is not None:
            body.append((localize['seasons'], season_count))
        if ep_count is not None:
            body.append((localize['episodes'], ep_count))
        body += [
            (localize['release_date'], release),
            (localize['rated'], rated),
            (localize['runtime'], runtime_str),
            (localize['genre'], genre),
            (localize['director'], director),
            (localize['writer'], writer),
            (localize['cast'], cast),
            (localize['score'], score),
            (localize['plot_outline'], plot, False)
        ]
        res = build_embed(body, 0xE5BC26, author={'name': title})
        if poster:
            res.set_image(url=poster)
        return res
    except (JSONDecodeError, IndexError):
        return localize['title_not_found']


def recipe_search(query, localize):
    """
    Search for a food recipe
    :param query: the search query
    :param localize: the localization strings
    :return: a discord embed object of the recipe
    """
    url = f'https://api.edamam.com/search?' \
          f'app_id={EDAMAM_API[0]}&app_key={EDAMAM_API[1]}&q={query}&to=1&' \
          f'returns=label'
    try:
        res = get(url).json()['hits'][0]['recipe']
    except IndexError:
        return localize['recipe_not_found']

    kwargs = {}
    author = {}
    if 'label' in res and res['label']:
        author['name'] = res['label']
    if 'url' in res and res['url']:
        author['url'] = res['url']
    if 'image' in res and res['image']:
        kwargs['thumbnail'] = res['image']
    if 'source' in res and res['source']:
        kwargs['footer'] = localize['recipe_source'] + res['source'] + \
                           " | " + localize['recipe_open']
    if author:
        kwargs['author'] = author
    servings = res.get('yield', None)
    if servings and servings % 1 == 0:
        servings = int(servings)
    calories = res.get('calories', None)
    cal_percent = res.get(
        'totalDaily', {}).get('ENERC_KCAL', {}).get('quantity', None)

    line1 = f'{round(calories)} ' + localize['kcal'] if calories else ''
    line2 = f'\n{round(cal_percent)}%' if cal_percent else ''
    if servings and line1:
        line1 += ' ({} {} {})'.format(
            round(calories / servings),
            localize['kcal'], localize['per_serving']
        )
    if servings and line2:
        line2 += ' ({}% {})'.format(
            round(cal_percent / servings), localize['per_serving']
        )
    cal_str = line1 + line2
    diet_labels = res.get('dietLabels', None)
    diet_labels = ', '.join(diet_labels) if diet_labels else None
    health_labels = res.get('healthLabels', None)
    health_labels = ', '.join(health_labels) if health_labels else None
    cautions = res.get('cautions', None)
    cautions = ', '.join(cautions) if cautions else None
    ingredients = res.get('ingredientLines', None)
    ingredients = '\n'.join(ingredients) if ingredients else None
    body = [
        (localize['servings'], servings),
        (localize['calories'], cal_str),
        (localize['cautions'], cautions),
        (localize['diet_labels'], diet_labels),
        (localize['health_labels'], health_labels),
        (localize['ingredients'], ingredients, False)
    ]
    body = [t for t in body if t[1]]
    des = localize['recipe_en'] if localize['language_data']['code'] != 'en' \
        else EmptyEmbed
    return build_embed(
        body,
        int(
            '0x%02X%02X%02X' % (
                randint(0, 255), randint(0, 255), randint(0, 255)
            ),
            base=16
        ),
        des,
        **kwargs
    )
