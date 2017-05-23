"""
Functions for Utilities commands
"""
from json import JSONDecodeError

from imdbpie import Imdb
from requests import get

from core.discord_functions import build_embed


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
        runtime_minutes = res.runtime
        runtime_str = '{}{} {}{}'.format(
            runtime_minutes//60, localize['hours'], runtime_minutes % 60, localize['minutes']
        ) if runtime_minutes is not None else 'N/A'
        rated = null_check(res.certification)
        genre = null_check(', '.join(res.genres))
        director = names(res.directors_summary)
        writer = names(res.writers_summary)
        cast = names(res.cast_summary)
        plot = null_check(res.plot_outline)
        poster = null_check(res.poster_url)
        score = null_check(res.rating)
        body = [

        ]
        if ep_count is not None:
            body.append('')
        if season_count is not None:
            body.append('')
        body += []



        # return build_embed([], 0xE5BC26)
        return res.__dict__
    except (JSONDecodeError, IndexError):
        return localize['title_not_found']


# *This title is a ${data.Type}*
#
# **Title:** ${data.Title}
# **Series:** ${data.Type === 'series' ? 'Yes, with ' + data.totalSeasons + ' seasons' : 'No'}
# **Release:** ${data.Released}
# **Rated:** ${data.Rated}
# **Aprox. runtime:** ${data.Runtime}
# **Genre:** ${data.Genre}
# **Director:** ${data.Director}
# **Writer:** ${data.Writer}
# **Actors:** ${data.Actors}
# **Plot:** ${data.Plot.length > 1200 ? data.Plot.substring(0, 1200) + '...' : data.Plot}
# **Metascore:** ${data.Metascore}
# :star: ${data.imdbRating}/10 (reviewed from ${data.imdbVotes} users)
# **Poster:** ${data.Poster}

if __name__ == '__main__':
    from pprint import pprint
    a = Imdb()
    r = imdb('breaking bad', a, {'title_not_found': ''})
    pprint(r)
