"""
NSFW functions
"""
from random import choice
from typing import List, Optional, Tuple

from aiohttp import ClientSession, ClientResponseError
from requests import get
from xmltodict import parse

from data_controller.tag_matcher import TagMatcher
from scripts.helpers import aiohttp_get, flatten

__all__ = ['get_lewd', 'greenteaneko']


def __parse_query(query: Tuple[str]) -> tuple:
    """
    Helper function to parse user search query.
    :param query: the search query.
    :return: (list of tags, rating)
    """
    rating = None
    tags = []
    for q in query:
        if q[:8].lower() in ('rating:s', 'rating:e', 'rating:q'):
            rating = q.lower()
        else:
            tags.append(q)
    return tags, rating


def __combine(rating, join_str, *tags: List[str]) -> str:
    """
    Combine a rating string and multiple tag lists into a single search
    string.
    :param rating: the rating.
    :param join_str: the character to join the list.
    :param tags: the lists of tags.
    :return: a single search string.
    """
    if rating:
        return join_str.join(flatten(tags) + [rating])
    return join_str.join(flatten(tags))


def __process_queries(
        site: str, tags: List[str], tag_matcher: TagMatcher) -> tuple:
    """
    Process a list of tags to separate them into two lists.
    :param site: the site of the tags
    :param tags: the list of tags.
    :param tag_matcher: the TagMatcher object.
    :return: two lists of tags. The first one are the list of tags that are
    in the db, the second one are the list of tags that aren't in the db.
    """
    safe_queries = []
    unsafe_queries = []
    for q in tags:
        if tag_matcher.tag_exist(site, q):
            safe_queries.append(q)
        else:
            unsafe_queries.append(q)
    return safe_queries, unsafe_queries


async def __request_lewd(
        tags: List[str], rating: Optional[str], url: str,
        site: str, session: ClientSession, tag_matcher: TagMatcher) -> tuple:
    """
    Make an HTTP request to a lewd site.
    :param tags: the list of tags for the search.
    :param rating: the rating of the search.
    :param url: the request url.
    :param site: the site name.
    :param session: the aiohttp ClientSession
    :param tag_matcher: the TagMatcher object.
    :return: a tuple of
    (request response, tags that are in the TagMatcher db,
    tags that are not in the TagMatcher db)
    :raises: ClientResponseError if the status code isnt 200
    """
    safe_queries, unsafe_queries = __process_queries(
        site, tags, tag_matcher)
    combined = __combine(rating, '%20', safe_queries, unsafe_queries)

    # FIXME: gelbooru doesn't play nice with aiohttp
    if site == 'gelbooru':
        res = get(url + combined)
        if res.status_code != 200:
            raise ClientResponseError
    else:
        res = await aiohttp_get(url + combined, session, False)
    return res, safe_queries, unsafe_queries


async def __parse_result(response, site: str) -> list:
    """
    Parse the HTTP response of a search and return the post list.
    :param response: the HTTP response.
    :param site: the site name.
    :return: The list of posts.
    """
    if site == 'gelbooru':
        res = parse(response.text)['posts']
        if 'post' in res and res['post']:
            return res['post']
    else:
        return await response.json()


def __parse_post_list(
        post_list: list, url_formatter: callable, tag_key) -> tuple:
    """
    Parse the post list to return the file url and its tags.
    :param post_list: the post list.
    :param url_formatter: a callable to get the file url.
    :param tag_key: the key to get the tag string.
    :return: a tuple of (file url, list of tags)
    """
    post = choice(post_list)
    file_url = url_formatter(post)
    return file_url, post[tag_key].split(' ')


def __retry_search(
        site: str, safe_queries: List[str],
        unsafe_queries: List[str], tag_matcher: TagMatcher) -> list:
    """
    Generate tags to retry the search if no results were found.
    :param site: the site name.
    :param safe_queries: the search tags that are in the db.
    :param unsafe_queries: the search tags that are not in the db.
    :param tag_matcher: the TagMatcher object.
    :return: a list of tags that are either in the db or matched with one in
    the db.
    """
    retry = safe_queries[:]
    for unsafe in unsafe_queries:
        match = tag_matcher.match_tag(site, unsafe)
        if match:
            retry.append(match)
    return retry


def __get_site_params(
        site: str, api_key: Optional[str], user: Optional[str]) -> tuple:
    """
    Get function call parameters for a site.
    :param site: the site name.
    :param api_key: the danbooru api key, not required for other sites.
    :param user: the danbooru username, not required for other sites.
    :return: the request url, the file url formatter, the key for the tag string
    """
    request_url = {
        'danbooru': f'https://danbooru.donmai.us//posts.json?login='
                    f'{user}&api_key={api_key}&limit=1&random=true&tags=',
        'konachan': 'https://konachan.com//post.json?tags=',
        'yandere': 'https://yande.re//post.json?tags=',
        'e621': 'https://e621.net/post/index.json?&tags=',
        'gelbooru': 'https://gelbooru.com//index.php?'
                    'page=dapi&s=post&q=index&tags='
    }[site]
    url_formatter = {
        'danbooru': lambda x: 'https://danbooru.donmai.us' + x['file_url'],
        'konachan': lambda x: 'https:' + x['file_url'],
        'yandere': lambda x: x['file_url'],
        'e621': lambda x: x['file_url'],
        'gelbooru': lambda x: 'https:' + x['@file_url']
    }[site]
    tag_key = {
        'danbooru': 'tag_string',
        'konachan': 'tags',
        'yandere': 'tags',
        'e621': 'tags',
        'gelbooru': '@tags'
    }[site]
    return request_url, url_formatter, tag_key


async def __get_lewd(
        tags: Optional[list], rating: Optional[str], site: str, site_params,
        tag_matcher: TagMatcher, session: ClientSession = None,
        limit=0, fuzzy=False) -> tuple:
    """
    Get lewds from a site.
    :param tags: the search tags.
    :param rating: the rating of the search.
    :param site: the site name.
    :param site_params: the function call parameters for the site.
    :param tag_matcher: the TagMatcher object.
    :param session: the aiohttp ClientSesson.
    :param limit: maximum recursion depth
    :param fuzzy: whether the search was fuzzy or not.
    :return: a tuple of
    (file url, tags used in the search, fuzzy, tags to write to the db)
    """
    assert session or site == 'gelbooru'
    if limit > 2:
        return (None,) * 4
    url, url_formatter, tag_key = site_params
    res, safe_queries, unsafe_queries = await __request_lewd(
        tags, rating, url, site, session, tag_matcher)
    post_list = await __parse_result(res, site)
    if post_list:
        file_url, tags_to_write = __parse_post_list(post_list, url_formatter,
                                                    tag_key)
        return file_url, safe_queries + unsafe_queries, fuzzy, tags_to_write
    retry = __retry_search(site, safe_queries, unsafe_queries, tag_matcher)
    if retry:
        return await __get_lewd(
            retry, rating, site, site_params,
            tag_matcher, session, limit + 1, True
        )
    return (None,) * 4


async def get_lewd(
        site: str, search_query: tuple, localize: dict,
        tag_matcher: TagMatcher, user=None, api_key=None) -> tuple:
    """
    Get lewd picture you fucking perverts.
    :param site: the site name.
    :param search_query: the search query.
    :param localize: the localization strings.
    :param tag_matcher: the TagMatcher object.
    :param user: the danbooru username, not required for other sites.
    :param api_key: the danbooru api key, not required for other sites.
    :return: a tuple of
    (the message with the file url to send, a list of tags to write to the db)
    """
    assert site in ('danbooru', 'konachan', 'yandere', 'e621', 'gelbooru')
    assert (user and api_key) or site != 'danbooru'
    tags, rating = __parse_query(search_query)
    site_params = __get_site_params(site, api_key, user)

    session = ClientSession() if site != 'gelbooru' else None
    try:
        file_url, searched_tags, fuzzy, tags_to_write = await __get_lewd(
            tags, rating, site, site_params, tag_matcher, session)
        if session is not None:
            session.close()
        if file_url:
            msg = file_url
            if fuzzy:
                msg = localize['nsfw_fuzzy'].format(
                    site.title(), ', '.join(searched_tags)) + file_url
            elif not search_query:
                msg = localize['random_nsfw'] + '\n' + file_url
            return msg, tags_to_write
        else:
            return localize['nsfw_sorry'], None
    except ClientResponseError:
        return localize['api_error'].format(site.title()), None


async def greenteaneko(localize):
    """
    Get a random green tea neko comic
    :param localize: the localization strings
    :return: the green tea neko comic
    """
    url = 'https://rra.ram.moe/i/r?type=nsfw-gtn&nsfw=true'
    try:
        res = await aiohttp_get(url, ClientSession(), True)
        js = await res.json()
        return 'https://rra.ram.moe{}\n{}'.format(
            js['path'], localize['gtn_artist'])
    except ClientResponseError:
        return localize['api_error'].format('rra.ram.moe')
