"""
NSFW functions
"""
import xml.etree.ElementTree as Et
from json import loads, decoder
from random import choice

from pybooru import Danbooru, PybooruAPIError
from requests import get, ConnectionError, HTTPError


SORRY = 'Sorry! nothing found'
ERROR = 'Something went wrong with the {} API. ' \
        'Please report this to my owner or await a fix.'
SEARCH = '//post.json?tags={}'


def danbooru(search, api: Danbooru, db_controller):
    """
    Search danbooru for lewds
    :param search: the search term
    :param api: the danbooru api object
    :param db_controller: the db controller
    :return: lewds
    """
    if len(search) == 0:
        try:
            res = api.post_list(tags=' '.join(search), random=True, limit=1)
        except PybooruAPIError:
            return ERROR.format('Danbooru')
        base = 'https://danbooru.donmai.us'
        return base + res[0]['large_file_url'] \
            if len(res) > 0 and 'large_file_url' in res[0] \
            else SORRY
    else:
        tag_finder_res = [tag_finder(t, 'danbooru', api, db_controller)
                          for t in search]
        is_fuzzy = False
        for entry in tag_finder_res:
            if entry[1] is True:
                is_fuzzy = True
                break
        search = [t[0] for t in tag_finder_res if t[0] is not None]
        fuzzy_string = '' if not is_fuzzy else \
            'You have entered invalid danbooru tags, ' \
            'here\'s the result of the search using these tags ' \
            'that I tried to match: `{}`\n'.format(', '.join(search))
        if len(search) > 0:
            try:
                res = api.post_list(tags=' '.join(search), random=True, limit=1)
            except PybooruAPIError:
                return ERROR.format('Danbooru')
            base = 'https://danbooru.donmai.us'
            return fuzzy_string + base + res[0]['large_file_url'] \
                if len(res) > 0 and 'large_file_url' in res[0] \
                else SORRY
        else:
            return SORRY


def tag_finder(tag, site, api: Danbooru, db_controller):
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
    else:
        # TODO for other sites
        return None, None


# def sankaku(search):
#     """
#     Search sankaku for lewdsresources
#     :param search: the search term
#     :return: lewds
#     """
#     # https://safebooru.org//index.php?page=dapi&s=post&q=index&tags={}
#     base = 'https://chan.sankakucomplex.com'
#     r_url = base + '/post.json?tag={}'.format('%20'.join(search))
#     try:
#         res = loads(r_url)
#     except decoder.JSONDecodeError:
#         res = 'Something went wrong with the sankaku API. ' \
#               'Please report this to my owner or await a fix.'
#     return res


def k_or_y(search, site_name):
    """
    Search konachan or yandere for lewds
    :param site_name: which site to search for 
    :param search: the search term
    :return: lewds
    """
    base = {
        'Konachan': 'https://konachan.com',
        'Yandere': 'https://yande.re'
    }[site_name]
    r_url = base + SEARCH.format('%20'.join(search))
    try:
        res = loads(get(r_url).content)
    except decoder.JSONDecodeError:
        return ERROR.format(site_name)
    if len(res) <= 0:
        return SORRY
    else:
        img = choice(res)['file_url']
        return 'https:' + img if site_name == 'Konachan' else img


def gelbooru(search):
    """
    Search gelbooru for lewds
    :param search: the search term 
    :return: lewds
    """
    url = "https://gelbooru.com//index.php?page=dapi&s=post&q=index&tags={}" \
        .format('%20'.join(search))
    try:
        result = get(url).content
    except ConnectionError and HTTPError:
        return ERROR.format('Gelbooru')
    root = Et.fromstring(result)
    res = ['https:' + child.attrib['file_url'] for child in root]
    return choice(res) if len(res) > 0 else SORRY
