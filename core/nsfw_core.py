"""
NSFW functions
"""
import xml.etree.ElementTree as Et
from json import loads, decoder
from random import choice

from pybooru import Danbooru, PybooruAPIError
from requests import get, ConnectionError, HTTPError

SEARCH = '//post.json?tags={}'


def sorry(bot, ctx):
    """
    Get the sorry string for nsfw
    :param bot: the bot
    :param ctx: the discord context object
    :return: the nsfw sorry message
    """
    return bot.get_language_dict(ctx)['nsfw_sorry']


def error(bot, ctx):
    """
    Get the nsfw error string
    :param bot: the bot
    :param ctx: the discord context 
    :return: the nsfw error sting
    """
    return bot.get_language_dict(ctx)['nsfw_error']


def fuzzy(bot, ctx):
    """
    Get the nsfw fuzzy string
    :param bot: the bot
    :param ctx: the discord context
    :return: the nsfw fuzzy string
    """
    return bot.get_language_dict(ctx)['nsfw_fuzzy']


def tag_finder(tag, site, db_controller, api: Danbooru = None):
    """
    Try to find or fuzzy match tag in db then the site after the attempt
    :param tag: the tag to look for
    :param site: the site name
    :param api: the danbooru api
    :param db_controller: the db controller
    :return: (tag, is_fuzzy)
    :rtype: tuple
    """
    if db_controller.tag_in_db(site, tag):
        return tag, False
    elif site == 'danbooru':
        tag_response = api.tag_list(name=tag, hide_empty='yes')
        if tag_response and tag_response[0]['name'] == tag:
            db_controller.write_tag('danbooru', tag)
            return tag, False
        else:
            return db_controller.fuzzy_match_tag(site, tag), True
    return db_controller.fuzzy_match_tag(site, tag), True


def danbooru(bot, ctx, search, api: Danbooru):
    """
    Search danbooru for lewds
    :param search: the search terms
    :param bot: the bot
    :param ctx: the discord context
    :param api: the danbooru api object
    :return: lewds
    """
    db_controller = bot.data_handler
    if len(search) == 0:
        return __danbooru(bot, ctx, search, api)
    else:
        tag_finder_res = [tag_finder(t, 'danbooru', db_controller, api)
                          for t in search]
        is_fuzzy = False
        for entry in tag_finder_res:
            if entry[1] is True:
                is_fuzzy = True
                break
        search = [t[0] for t in tag_finder_res if t[0] is not None]
        fuzzy_string = '' if not is_fuzzy else \
            fuzzy(bot, ctx).format('Danbooru', ', '.join(search))
        if len(search) > 0:
            return fuzzy_string + __danbooru(bot, ctx, search, api)
        else:
            return sorry(bot, ctx)


def __danbooru(bot, ctx, search, api):
    """
    A helper function for danbooru search
    :param search: the search terms
    :param bot: the bot
    :param ctx: the discord context
    :param api: the danbooru api 
    :return: a danbooru url if something is found else sorry string,
    or error string if API error is raised
    """
    base = 'https://danbooru.donmai.us'
    try:
        res = api.post_list(tags=' '.join(search), random=True, limit=1)
    except PybooruAPIError:
        return error(bot, ctx).format('Danbooru')
    return base + res[0]['large_file_url'] \
        if len(res) > 0 and 'large_file_url' in res[0] \
        else sorry(bot, ctx)


def k_or_y(bot, ctx, search, site_name, limit=0, is_fuzzy=False):
    """
    Search konachan or yandere for lewds
    :param bot: the bot
    :param ctx: the discord context
    :param search: the search terms
    :param site_name: which site to search for 
    :param limit: the limit of the recursion depth, 
    to prevent infinite recursion
    :param is_fuzzy: indicates if this search is a fuzzy result
    :return: lewds
    """
    db_controller = bot.data_handler
    if limit > 2:
        return sorry(bot, ctx)
    base = {
        'Konachan': 'https://konachan.com',
        'Yandere': 'https://yande.re'
    }[site_name]
    r_url = base + SEARCH.format('%20'.join(search))
    try:
        res = loads(get(r_url).content)
    except decoder.JSONDecodeError:
        return error(bot, ctx).format(site_name)
    if len(res) <= 0:
        tags = []
        for query in search:
            res, fuz = tag_finder(query, site_name.lower(), db_controller)
            if res is not None:
                tags.append(res)
            if fuz:
                is_fuzzy = fuz
        if not tags:
            return sorry(bot, ctx)
        else:
            return k_or_y(bot, ctx, tags, site_name, limit + 1, is_fuzzy)
    else:
        for tag in search:
            db_controller.write_tag(site_name.lower(), tag)
        img = choice(res)['file_url']
        res = 'https:' + img if site_name == 'Konachan' else img
        if is_fuzzy:
            res = fuzzy(bot, ctx).format(site_name, ', '.join(search)) + res
        return res


def gelbooru(bot, ctx, search, limit=0, is_fuzzy=False):
    """
    Search gelbooru for lewds
    :param bot: the bot
    :param ctx: the discord context
    :param search: the search terms
    :param limit: the limit of the recursion depth, 
    to prevent infinite recursion
    :param is_fuzzy: indicates if this search is a fuzzy result
    :return: lewds
    """
    db_controller = bot.data_handler
    if limit > 2:
        return sorry(bot, ctx)
    url = "https://gelbooru.com//index.php?page=dapi&s=post&q=index&tags={}" \
        .format('%20'.join(search))
    try:
        result = get(url).content
    except ConnectionError and HTTPError:
        return error(bot, ctx).format('Gelbooru')
    root = Et.fromstring(result)
    res = ['https:' + child.attrib['file_url'] for child in root]
    if len(res) > 0:
        res = choice(res)
        for tag in search:
            db_controller.write_tag('gelbooru', tag)
        if is_fuzzy:
            res = fuzzy(bot, ctx).format('Gelbooru', ', '.join(search)) + res
        return res
    else:
        tags = []
        for tag in search:
            t, fuz = tag_finder(tag, 'gelbooru', db_controller)
            if t is not None:
                tags.append(t)
            if fuz:
                is_fuzzy = fuz
        if not tags:
            return sorry(bot, ctx)
        else:
            return gelbooru(bot, ctx, tags,  limit + 1, is_fuzzy)


def random_str(bot, ctx):
    """
    Get the string for random search result
    :param bot: the bot
    :param ctx: the discord context object
    :return: the random str
    """
    return bot.get_language_dict(ctx)['random_nsfw']

