"""
NSFW functions
"""
from random import choice
from typing import List, Optional, Tuple

from bot import HTTPStatusError, SessionManager
from data_controller.tag_matcher import TagMatcher
from scripts.helpers import flatten

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
        param: dict, site: str, session_manager: SessionManager,
        tag_matcher: TagMatcher) -> tuple:
    """
    Make an HTTP request to a lewd site.
    :param tags: the list of tags for the search.
    :param rating: the rating of the search.
    :param url: the request url.
    :param param: the request parameters.
    :param site: the site name.
    :param session_manager: the aiohttp session manager
    :param tag_matcher: the TagMatcher object.
    :return: a tuple of
    (request response, tags that are in the TagMatcher db,
    tags that are not in the TagMatcher db)
    :raises: ClientResponseError if the status code isnt 200
    """
    safe_queries, unsafe_queries = __process_queries(
        site, tags, tag_matcher)
    combined = __combine(rating, '%20', safe_queries, unsafe_queries)
    param['tags'] = combined
    res = await session_manager.get_json(url, param)
    return res, safe_queries, unsafe_queries


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
        'danbooru': 'https://danbooru.donmai.us//posts.json?',
        'konachan': 'https://konachan.com//post.json?',
        'yandere': 'https://yande.re//post.json?',
        'e621': 'https://e621.net/post/index.json?',
        'gelbooru': 'https://gelbooru.com//index.php?'
    }[site]
    url_formatter = {
        'danbooru': lambda x: 'https://danbooru.donmai.us' + x['file_url'],
        'konachan': lambda x: 'https:' + x['file_url'],
        'yandere': lambda x: x['file_url'],
        'e621': lambda x: x['file_url'],
        'gelbooru': lambda x: 'https:' + x['file_url']
    }[site]
    tag_key = {
        'danbooru': 'tag_string',
        'konachan': 'tags',
        'yandere': 'tags',
        'e621': 'tags',
        'gelbooru': 'tags'
    }[site]
    param = {
        'danbooru': {'login': user, 'api_key': api_key, 'limit': '1',
                     'random': 'true'},
        'konachan': {},
        'yandere': {},
        'e621': {},
        'gelbooru': {'page': 'dapi', 's': 'post', 'q': 'index', 'json': '1'}
    }[site]
    return request_url, url_formatter, tag_key, param


async def __get_lewd(
        tags: Optional[list], rating: Optional[str], site: str, site_params,
        tag_matcher: TagMatcher, session_manager: SessionManager,
        limit=0, fuzzy=False) -> tuple:
    """
    Get lewds from a site.
    :param tags: the search tags.
    :param rating: the rating of the search.
    :param site: the site name.
    :param site_params: the function call parameters for the site.
    :param tag_matcher: the TagMatcher object.
    :param session_manager: the aiohttp SessionManager.
    :param limit: maximum recursion depth
    :param fuzzy: whether the search was fuzzy or not.
    :return: a tuple of
    (file url, tags used in the search, fuzzy, tags to write to the db)
    """
    if limit > 2:
        return (None,) * 4
    url, url_formatter, tag_key, param = site_params
    post_list, safe_queries, unsafe_queries = await __request_lewd(
        tags, rating, url, param, site, session_manager, tag_matcher)

    if post_list:
        file_url, tags_to_write = __parse_post_list(post_list, url_formatter,
                                                    tag_key)
        return file_url, safe_queries + unsafe_queries, fuzzy, tags_to_write
    retry = __retry_search(site, safe_queries, unsafe_queries, tag_matcher)
    if retry:
        return await __get_lewd(
            retry, rating, site, site_params,
            tag_matcher, session_manager, limit + 1, True
        )
    return (None,) * 4


async def get_lewd(
        session_manager: SessionManager, site: str, search_query: tuple,
        localize: dict, tag_matcher: TagMatcher, user=None,
        api_key=None) -> tuple:
    """
    Get lewd picture you fucking perverts.
    :param session_manager: the aiohttp SessionManager.
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

    try:
        file_url, searched_tags, fuzzy, tags_to_write = await __get_lewd(
            tags, rating, site, site_params, tag_matcher, session_manager)
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
    except HTTPStatusError as e:
        error = localize['api_error'].format(site.title()) + f'\n{e}'
        return error, None


async def greenteaneko(localize, session_manager: SessionManager):
    """
    Get a random green tea neko comic
    :param session_manager: the aiohttp SessionManager.
    :param localize: the localization strings
    :return: the green tea neko comic
    """
    url = 'https://rra.ram.moe/i/r?'
    params = {
        'type': 'nsfw-gtn',
        'nsfw': 'true'
    }
    try:
        js = await session_manager.get_json(url, params)
    except HTTPStatusError as e:
        return localize['api_error'].format('rra.ram.moe') + f'\n{e}'
    else:
        return 'https://rra.ram.moe{}\n{}'.format(
            js['path'], localize['gtn_artist']
        )
