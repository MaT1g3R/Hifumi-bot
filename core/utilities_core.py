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
        id_ = api.search_for_title(query)[0]['imdb_id']
        res = api.get_title_by_id(id_)
        eps = api.get_episodes(id_) if res.type == 'tv_series' else None
        ep_count = len(eps) if eps is not None else None
        season_count = eps[-1].season if eps is not None else None
        title = res.title
        release = res.release_date
        runtime = res.runtime
        rated = res.certification
        genre = res.genres
        director = res.directors_summary
        writer = res.writers_summary
        cast = res.cast_summary
        plot = res.plot_outline
        poster = res.poster_url
        score = res.rating
        return build_embed([], 0xE5BC26)
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
    pprint(imdb('breaking bad', a, {'title_not_found': ''}))
