"""
NSFW functions
"""
import xml.etree.ElementTree as Et
from json import loads, decoder
from random import choice

from pybooru import Danbooru, PybooruAPIError
from requests import get, ConnectionError, HTTPError

from config.settings import DATA_CONTROLLER

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


def random_str(bot, ctx):
    """
    Get the string for random search result
    :param bot: the bot
    :param ctx: the discord context object
    :return: the random str
    """
    return bot.get_language_dict(ctx)['random_nsfw']


def tag_finder(tag, site):
    """
    Try to find or fuzzy match tag in db then the site after the attempt
    :param tag: the tag to look for
    :param site: the site name
    :return: (tag, is_fuzzy)
    :rtype: tuple
    """
    if DATA_CONTROLLER.tag_in_db(site, tag):
        return tag, False
    else:
        return DATA_CONTROLLER.fuzzy_match_tag(site, tag), True


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


def danbooru(bot, ctx, search, api: Danbooru, limit=0, is_fuzzy=False):
    """
    Search danbooru for lewds
    :param search: the search terms
    :param bot: the bot
    :param ctx: the discord context
    :param api: the danbooru api object
    :param limit: limit to prevent infinite recursion
    :param is_fuzzy: if the search is is_fuzzy
    :return: lewds
    """
    if limit > 2:
        return sorry(bot, ctx), None
    res, tags, success = __danbooru(bot, ctx, search, api)
    if success:
        if is_fuzzy:
            res = fuzzy(bot, ctx).format('danbooru', ', '.join(search)) + res
        return res, tags
    else:
        tag_res = [tag_finder(t, 'danbooru') for t in search]
        new_tags = [t[0] for t in tag_res if t[0] is not None]
        for t in tag_res:
            if t[1]:
                is_fuzzy = True
                break
        if new_tags:
            return danbooru(bot, ctx, new_tags, api, limit + 1, is_fuzzy)
        else:
            return sorry(bot, ctx), None


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
        return error(bot, ctx).format('Danbooru'), None, False
    if len(res) > 0 and 'large_file_url' in res[0]:
        return base + res[0]['large_file_url'], \
               tag_list_gen(res, 'danbooru'), True
    else:
        return sorry(bot, ctx), None, False


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
        return error(bot, ctx).format(site_name), None
    if len(res) <= 0:
        tags = []
        for query in search:
            res, fuz = tag_finder(query, site_name.lower())
            if res is not None:
                tags.append(res)
            if fuz:
                is_fuzzy = fuz
        if not tags:
            return sorry(bot, ctx), None
        else:
            return k_or_y(bot, ctx, tags, site_name, limit + 1, is_fuzzy)
    else:
        tags = tag_list_gen(res, site_name)
        img = choice(res)['file_url']
        res = 'https:' + img if site_name == 'Konachan' else img
        if is_fuzzy:
            res = fuzzy(bot, ctx).format(site_name, ', '.join(search)) + res
        return res, tags


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
            DATA_CONTROLLER.write_tag('gelbooru', tag)
        if is_fuzzy:
            res = fuzzy(bot, ctx).format('Gelbooru', ', '.join(search)) + res
        return res
    else:
        tags = []
        for tag in search:
            t, fuz = tag_finder(tag, 'gelbooru')
            if t is not None:
                tags.append(t)
            if fuz:
                is_fuzzy = fuz
        if not tags:
            return sorry(bot, ctx)
        else:
            return gelbooru(bot, ctx, tags, limit + 1, is_fuzzy)


def e621(bot, ctx, search, limit=0, is_fuzzy=False):
    """
    Search e621 for lewds
    :param bot: the bot
    :param ctx: the discord context
    :param search: the search terms
    :param limit: max recursion depth to prevent infinite recursion
    :param is_fuzzy: if the search is fuzzy
    :return: the lewds
    """
    if limit > 2:
        return sorry(bot, ctx)
    url = 'https://e621.net/post/index.json?limit=30&tags=' + '%20'.join(search)
    try:
        res = loads(get(url).content)
    except decoder.JSONDecodeError:
        return error(bot, ctx).format('e621'), None
    if len(res) > 0:
        img = choice(res)['file_url']
        fuz = fuzzy(bot, ctx).format('e621', ', '.join(search)) if is_fuzzy \
            else ''
        return fuz + img, tag_list_gen(res, 'e621')
    else:
        tags = []
        for query in search:
            res, fuz = tag_finder(query, 'e621')
            if fuz:
                is_fuzzy = fuz
            if res is not None:
                tags.append(res)
        if not tags:
            return sorry(bot, ctx), None
        else:
            return e621(bot, ctx, tags, limit + 1, is_fuzzy)


def greenteaneko(ctx, bot):
    """
    Get a random green tea neko comic
    :param ctx: the discord context
    :param bot: the bot
    :return: the green tea neko comic
    """
    url = 'https://rra.ram.moe/i/r?type=nsfw-gtn&nsfw=true'
    try:
        result = loads(get(url).content)
        credit = bot.get_language_dict(ctx)['gtn_artist']
        return 'https://rra.ram.moe' + result['path'] + '\n' + credit
    except decoder.JSONDecodeError:
        error(bot, ctx).format('rra.ram.moe')
