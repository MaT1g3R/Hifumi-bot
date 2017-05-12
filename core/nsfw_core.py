"""
NSFW functions
"""
import xml.etree.ElementTree as Et
from json import loads, decoder
from random import choice

from pybooru import Danbooru, PybooruAPIError
from requests import get, ConnectionError, HTTPError

from core.data_controller import write_tag, fuzzy_match_tag, tag_in_db

SEARCH = '//post.json?tags={}'


def random_str(bot, ctx):
    """
    Get the string for random search result
    :param bot: the bot
    :param ctx: the discord context object
    :return: the random str
    """
    return bot.get_language_dict(ctx)['random_nsfw']


def tag_finder(cur, site, tag):
    """
    Try to find or fuzzy match tag in db then the site after the attempt
    :param cur: the database cursor
    :param tag: the tag to look for
    :param site: the site name
    :return: (tag, is_fuzzy)
    :rtype: tuple
    """
    if tag_in_db(cur, site, tag):
        return tag, False
    else:
        return fuzzy_match_tag(cur, site, tag), True


def tag_list_gen(all_results, site_name):
    """
    Generate all the tags from a search
    :param all_results: all sarch results
    :param site_name: the site name
    :return: a list of all tags
    """
    site_name = site_name.lower()
    tag_str = 'tags' if site_name != 'danbooru' else 'tag_string'
    result = []
    for r in all_results:
        tags = str.split(r[tag_str], ' ')
        result += tags
    return result + ['rating:safe', 'rating:explicit', 'rating:questionable']


def danbooru(cur, search, api: Danbooru, localize, limit=0, is_fuzzy=False):
    """
    Search danbooru for lewds
    :param cur: the database cursor
    :param search: the search terms
    :param api: the danbooru api object
    :param localize: the localizaton strings
    :param limit: limit to prevent infinite recursion
    :param is_fuzzy: if the search is is_fuzzy
    :return: lewds
    """
    if limit > 2:
        return localize['nsfw_sorry'], None
    res, tags, success = __danbooru(search, api, localize)
    if success:
        if is_fuzzy:
            res = localize['nsfw_fuzzy'].format('danbooru', ', '.join(search)) \
                  + res
        return res, tags
    else:
        tag_res = [tag_finder(cur, 'danbooru', t) for t in search]
        new_tags = [t[0] for t in tag_res if t[0] is not None]
        for t in tag_res:
            if t[1]:
                is_fuzzy = True
                break
        if new_tags:
            return danbooru(
                cur, new_tags, api, localize, limit + 1, is_fuzzy
            )
        else:
            return localize['nsfw_sorry'], None


def __danbooru(search, api, localize):
    """
    A helper function for danbooru search
    :param search: the search terms
    :param api: the danbooru api 
    :return: a danbooru url if something is found else sorry string,
    or error string if API error is raised
    """
    base = 'https://danbooru.donmai.us'
    try:
        res = api.post_list(tags=' '.join(search), random=True, limit=1)
    except PybooruAPIError:
        return localize['nsfw_error'].format('Danbooru'), None, False
    if len(res) > 0 and 'large_file_url' in res[0]:
        return base + res[0]['large_file_url'], \
               tag_list_gen(res, 'danbooru'), True
    else:
        return localize['nsfw_sorry'], None, False


def k_or_y(cur, search, site_name, localize, limit=0, is_fuzzy=False):
    """
    Search konachan or yandere for lewds
    :param cur: the database cursor
    :param search: the search terms
    :param site_name: which site to search for 
    :param localize: the localization strings
    :param limit: the limit of the recursion depth, 
    to prevent infinite recursion
    :param is_fuzzy: indicates if this search is a fuzzy result
    :return: lewds
    """
    if limit > 2:
        return localize['nsfw_sorry']
    base = {
        'Konachan': 'https://konachan.com',
        'Yandere': 'https://yande.re'
    }[site_name]
    r_url = base + SEARCH.format('%20'.join(search))
    try:
        res = loads(get(r_url).content)
    except decoder.JSONDecodeError:
        return localize['nsfw_error'].format(site_name), None
    if len(res) <= 0:
        tags = []
        for query in search:
            res, fuz = tag_finder(cur, site_name.lower(), query)
            if res is not None:
                tags.append(res)
            if fuz:
                is_fuzzy = fuz
        if not tags:
            return localize['nsfw_sorry'], None
        else:
            return k_or_y(cur, tags, site_name, localize, limit + 1, is_fuzzy)
    else:
        tags = tag_list_gen(res, site_name)
        img = choice(res)['file_url']
        res = 'https:' + img if site_name == 'Konachan' else img
        if is_fuzzy:
            res = localize['nsfw_fuzzy'].format(site_name, ', '.join(search)) \
                  + res
        return res, tags


def gelbooru(conn, cur, search, localize, limit=0, is_fuzzy=False):
    """
    Search gelbooru for lewds
    :param conn: the database connection
    :param cur: the database cursor
    :param search: the search terms
    :param localize: the localization strings
    :param limit: the limit of the recursion depth, 
    to prevent infinite recursion
    :param is_fuzzy: indicates if this search is a fuzzy result
    :return: lewds
    """
    if limit > 2:
        return localize['nsfw_sorry']
    url = "https://gelbooru.com//index.php?page=dapi&s=post&q=index&tags={}" \
        .format('%20'.join(search))
    try:
        result = get(url).content
    except ConnectionError and HTTPError:
        return localize['nsfw_error'].format('Gelbooru')
    root = Et.fromstring(result)
    res = ['https:' + child.attrib['file_url'] for child in root]
    if len(res) > 0:
        res = choice(res)
        for tag in search:
            write_tag(conn, cur, 'gelbooru', tag)
        if is_fuzzy:
            res = localize['nsfw_fuzzy'].format('Gelbooru',
                                                ', '.join(search)) + res
        return res
    else:
        tags = []
        for tag in search:
            t, fuz = tag_finder(cur, 'gelbooru', tag)
            if t is not None:
                tags.append(t)
            if fuz:
                is_fuzzy = fuz
        if not tags:
            return localize['nsfw_sorry']
        else:
            return gelbooru(conn, cur, tags, localize, limit + 1, is_fuzzy)


def e621(cur, search, localize, limit=0, is_fuzzy=False):
    """
    Search e621 for lewds
    :param cur: the database cursor
    :param search: the search terms
    :param localize: the localization strings
    :param limit: max recursion depth to prevent infinite recursion
    :param is_fuzzy: if the search is fuzzy
    :return: the lewds
    """
    if limit > 2:
        return localize['nsfw_sorry']
    url = 'https://e621.net/post/index.json?limit=30&tags=' + '%20'.join(search)
    try:
        res = loads(get(url).content)
    except decoder.JSONDecodeError:
        return localize['nsfw_error'].format('e621'), None
    if len(res) > 0:
        img = choice(res)['file_url']
        fuz = localize['nsfw_fuzzy'].format('e621',
                                            ', '.join(search)) if is_fuzzy \
            else ''
        return fuz + img, tag_list_gen(res, 'e621')
    else:
        tags = []
        for query in search:
            res, fuz = tag_finder(cur, 'e621', query)
            if fuz:
                is_fuzzy = fuz
            if res is not None:
                tags.append(res)
        if not tags:
            return localize['nsfw_sorry'], None
        else:
            return e621(cur, tags, localize, limit + 1, is_fuzzy)


def greenteaneko(localize):
    """
    Get a random green tea neko comic
    :param localize: the localization strings
    :return: the green tea neko comic
    """
    url = 'https://rra.ram.moe/i/r?type=nsfw-gtn&nsfw=true'
    try:
        result = loads(get(url).content)
        credit = localize['gtn_artist']
        return 'https://rra.ram.moe' + result['path'] + '\n' + credit
    except decoder.JSONDecodeError:
        localize['nsfw_error'].format('rra.ram.moe')
