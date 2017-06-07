"""
NSFW functions
"""
from random import choice
from typing import List, Optional, Tuple

from aiohttp import ClientSession

from data_controller.tag_matcher import TagMatcher
from scripts.helpers import flatten, request_get


def random_str(bot, ctx):
    """
    Get the string for random search result
    :param bot: the bot
    :param ctx: the discord context object
    :return: the random str
    """
    return bot.get_language_dict(ctx)['random_nsfw']


def __parse_query(query: Tuple[str]):
    """
    Helper function to parse user search query.
    :param query: the search query.
    :return: (list of tags, rating)
    """
    rating = None
    tags = []
    for q in query:
        if q[:8].lower() in ('rating:s', 'rating:e', 'rating:q'):
            rating = q[:8].lower()
        else:
            tags.append(q)
    return tags, rating


def __combine(rating: Optional[str], join_str, *tags: List[str]) -> str:
    """
    Combine a rating string and multiple tag lists into a single search
    string.
    :param rating: the rating.
    :param join_str: the character to join the list.
    :param tags: the lists of tags.
    :return: a single search string.
    """
    return join_str.join(flatten(tags) + [rating])


def __process_queries(site: str, tags: List[str], tag_matcher: TagMatcher):
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


async def __danbooru_konachan_yandere_e621(
        tags: Optional[List[str]], rating: Optional[str],
        site: str, api_key: Optional[str], user: Optional[str],
        session: ClientSession, tag_matcher: TagMatcher, limit=0, fuzzy=False
) -> tuple:
    """
    Search danbooru, konachan, yandere or e621 for lewds.
    :param tags: the search tags from the user input.
    :param rating: the search rating.
    :param site: the site name.
    :param api_key: the api key (only required for danbooru)
    :param user: the user name (only required for danbooru)
    :param session: the aiohttp ClientSession.
    :param tag_matcher: the TagMatcher object.
    :param limit: max recursion depth to prevent infinite recursion
    :param fuzzy: if the search is fuzzy
    :return: (search result, list of tags used in the search,
              is_fuzzy, a list of all tags to write to the db)
    :raises ConnectionError if the status code isnt 200.
    """
    assert site in ('danbooru', 'konachan', 'yandere', 'e621')
    assert (user is not None and api_key is not None) or site != 'danbooru'
    if limit > 2:
        return (None,) * 4
    request_url = {
        'danbooru': f'https://danbooru.donmai.us//posts.json?login='
                    f'{user}&api_key={api_key}&limit=1&random=true&tags=',
        'konachan': 'https://konachan.com//post.json?tags=',
        'yandere': 'https://yande.re//post.json?tags=',
        'e621': 'https://e621.net/post/index.json?&tags='
    }[site]
    join_str = ' ' if site == 'danbooru' else '%20'
    safe_queries, unsafe_queries = __process_queries(
        site, tags, tag_matcher)
    combined = __combine(rating, join_str, safe_queries, unsafe_queries)
    res = await request_get(request_url + combined, session, False)
    res = res.json()
    if res:
        res = choice(res)
        file_url = res['file_url']
        if site == 'konachan':
            file_url = 'https:' + file_url
        if site == 'danbooru':
            file_url = 'https://danbooru.donmai.us' + file_url
        tag_key = 'tag_string' if site == 'danbooru' else 'tags'
        return \
            file_url, safe_queries + unsafe_queries, \
            fuzzy, res[tag_key].split(' ')
    for unsafe in unsafe_queries:
        match = tag_matcher.match_tag(site, unsafe)
        if match:
            safe_queries.append(match)
    if safe_queries:
        return await __danbooru_konachan_yandere_e621(
            tags, rating, site, api_key, user,
            session, tag_matcher, limit + 1, True
        )
    return (None,) * 4


if __name__ == '__main__':
    from requests import get
    from pprint import pprint

    # u = f'http://danbooru.donmai.us//posts.json?login={DANBOORU_USERNAME}&api_key={DANBOORU_API}&tags=rating:safe akizuki_(kantai_collection)&limit=1&random=true'
    # print(get(u).text)
    u = 'https://konachan.com//post.json?&limit=1&random=true'
    pprint(get(u).json())
    print('\n')
    u = 'https://yande.re//post.json?&limit=1&random=true'
    pprint(get(u).json())
    print('\n')
    u = 'https://e621.net/post/index.json?&limit=1&random=true'
    pprint(get(u).json())
