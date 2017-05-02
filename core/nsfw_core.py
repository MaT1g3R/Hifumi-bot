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
FUZZY = 'You have entered invalid {} tags, ' \
            'here\'s the result of the search using these tags ' \
            'that I tried to match: `{}`\n'


def danbooru(search, api: Danbooru, db_controller):
    """
    Search danbooru for lewds
    :param search: the search terms
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
        tag_finder_res = [tag_finder(t, 'danbooru',  db_controller, api)
                          for t in search]
        is_fuzzy = False
        for entry in tag_finder_res:
            if entry[1] is True:
                is_fuzzy = True
                break
        search = [t[0] for t in tag_finder_res if t[0] is not None]
        fuzzy_string = '' if not is_fuzzy else \
            FUZZY.format('Danbooru', ', '.join(search))
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


def tag_finder(tag, site, db_controller, api: Danbooru=None):
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


def k_or_y(search, site_name, db_controller, limit=0, fuzzy=False):
    """
    Search konachan or yandere for lewds
    :param search: the search terms
    :param site_name: which site to search for 
    :param db_controller: the database controller
    :param limit: the limit of the recursion depth, 
    to prevent infinite recursion
    :param fuzzy: indicates if this search is a fuzzy result
    :return: lewds
    """
    if limit > 2:
        return SORRY
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
        tags = []
        for query in search:
            res, fuz = tag_finder(query, site_name.lower(), db_controller)
            if res is not None:
                tags.append(res)
            if fuz:
                fuzzy = fuz
        if not tags:
            return SORRY
        else:
            return k_or_y(tags, site_name, db_controller, limit+1, fuzzy)
    else:
        for tag in search:
            db_controller.write_tag(site_name.lower(), tag)
        img = choice(res)['file_url']
        res = 'https:' + img if site_name == 'Konachan' else img
        if fuzzy:
            res = FUZZY.format(site_name, ', '.join(search)) + res
        return res


def gelbooru(search, db_controller, limit=0, fuzzy=False):
    """
    Search gelbooru for lewds
    :param search: the search terms
    :param db_controller: the database controller
    :param limit: the limit of the recursion depth, 
    to prevent infinite recursion
    :param fuzzy: indicates if this search is a fuzzy result
    :return: lewds
    """
    if limit > 2:
        return SORRY
    url = "https://gelbooru.com//index.php?page=dapi&s=post&q=index&tags={}" \
        .format('%20'.join(search))
    try:
        result = get(url).content
    except ConnectionError and HTTPError:
        return ERROR.format('Gelbooru')
    root = Et.fromstring(result)
    res = ['https:' + child.attrib['file_url'] for child in root]
    if len(res) > 0:
        res = choice(res)
        for tag in search:
            db_controller.write_tag('gelbooru', tag)
        if fuzzy:
            res = FUZZY.format('Gelbooru', ', '.join(search)) + res
        return res
    else:
        tags = []
        for tag in search:
            t, fuz = tag_finder(tag, 'gelbooru', db_controller)
            if t is not None:
                tags.append(t)
            if fuz:
                fuzzy = fuz
        if not tags:
            return SORRY
        else:
            return gelbooru(tags, db_controller, limit+1, fuzzy)
