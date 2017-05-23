"""
Functions for Utilities commands
"""
from json import JSONDecodeError

from imdbpie import Imdb
from requests import get
from .discord_functions import build_embed


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
            hours, minutes = divmod(runtime / 100, 60)
            runtime_str = '{} {} {} {}'.format(
                round(hours), localize['hours'],
                round(minutes), localize['minutes']
            )
            return runtime_str
        else:
            runtime_str = 'N/A'
        rated = null_check(res.certification)
        genre = null_check(', '.join(res.genres))
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
