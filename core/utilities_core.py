"""
Functions for Utilities commands
"""
from json import JSONDecodeError
from random import randint
from textwrap import wrap

from discord.embeds import Embed, EmptyEmbed
from imdbpie import Imdb

from bot import HTTPStatusError, SessionManager


async def number_fact(num, localize, session_manager: SessionManager):
    """
    Find a fact about a number
    :param num: the number
    :param localize: the localization strings
    :param session_manager: the SessionManager
    :return: a string representation for the fact
    """
    header = localize['num_fact_random'] if num is None \
        else localize['num_fact_found']
    bad_num_msg = localize['num_fact_str']
    not_found_msg = localize['num_fact_not_found']
    try:
        if num != 'random':
            num = int(num)
    except ValueError:
        return bad_num_msg
    url = f'http://numbersapi.com/{num}?json=true'
    try:
        res = await session_manager.get_json(url)
        return header.format(res['number']) + res['text'] if res['found'] \
            else not_found_msg
    except HTTPStatusError as e:
        return localize['api_error'].format('Numbers Fact') + f'\n{e}'


async def imdb(query, api: Imdb, localize):
    """
    Send an api request to imdb using the search query
    :param query: the search query
    :param api: the imdb api object
    :param localize: the localization strings
    :return: the result
    """
    # FIXME: Use Aiohttp instead of this api wrapper
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
        runtime = res.runtime
        if runtime is not None:
            hours, seconds = divmod(runtime, 3600)
            minutes = seconds / 60
            runtime_str = '{} {} {} {}'.format(
                round(hours), localize['hours'],
                round(minutes), localize['minutes']
            )
        else:
            runtime_str = 'N/A'
        rated = null_check(res.certification)
        genre = ', '.join(res.genres) if res.genres else 'N/A'
        director = names(res.directors_summary)
        writer = names(res.writers_summary)
        cast = names(res.cast_summary)
        plot = null_check(res.plot_outline)
        poster = res.poster_url
        score = f'{res.rating}/10' if res.rating is not None else 'N/A'

        embed = Embed(colour=0xE5BC26)
        embed.set_author(name=title)
        if poster:
            embed.set_image(url=poster)
        if season_count is not None:
            embed.add_field(name=localize['seasons'], value=season_count)
        if ep_count is not None:
            embed.add_field(name=localize['episodes'], value=str(ep_count))

        embed.add_field(name=localize['release_date'], value=release)
        embed.add_field(name=localize['rated'], value=rated)
        embed.add_field(name=localize['runtime'], value=runtime_str)
        embed.add_field(name=localize['genre'], value=genre)
        embed.add_field(name=localize['director'], value=director)
        embed.add_field(name=localize['writer'], value=writer)
        embed.add_field(name=localize['cast'], value=cast)
        embed.add_field(name=localize['score'], value=score)
        embed.add_field(name=localize['plot_outline'], value=plot, inline=False)

        return embed

    except (JSONDecodeError, IndexError):
        return localize['title_not_found']


async def recipe_search(
        query, localize, edamam_app_id, edamam_key,
        session_manager: SessionManager):
    """
    Search for a food recipe
    :param query: the search query
    :param localize: the localization strings
    :param edamam_app_id: the edamam app id
    :param edamam_key: the edamam api key
    :param session_manager: the SessionManager
    :return: a discord embed object of the recipe
    """
    url = f'https://api.edamam.com/search?'
    params = {
        'app_id': edamam_app_id,
        'app_key': edamam_key,
        'q': query,
        'to': '1',
        'returns': 'label'
    }
    try:
        js = await session_manager.get_json(url, params)
        res = js['hits'][0]['recipe']
    except IndexError:
        return localize['recipe_not_found']
    except HTTPStatusError as e:
        return localize['api_error'].format('Edamam') + f'\n{e}'

    servings = res.get('yield', None)
    if servings and servings % 1 == 0:
        servings = int(servings)
    calories = res.get('calories', None)
    cal_percent = res.get(
        'totalDaily', {}).get('ENERC_KCAL', {}).get('quantity', None)

    line1 = f'{round(calories)} ' + localize['kcal'] if calories else ''
    line2 = f'\n{round(cal_percent)}%' if cal_percent else ''
    if servings and line1:
        line1 += ' ({} {} {})'.format(
            round(calories / servings),
            localize['kcal'], localize['per_serving']
        )
    if servings and line2:
        line2 += ' ({}% {})'.format(
            round(cal_percent / servings), localize['per_serving']
        )
    cal_str = line1 + line2
    diet_labels = res.get('dietLabels', None)
    diet_labels = ', '.join(diet_labels) if diet_labels else None
    health_labels = res.get('healthLabels', None)
    health_labels = ', '.join(health_labels) if health_labels else None
    cautions = res.get('cautions', None)
    cautions = ', '.join(cautions) if cautions else None
    ingredients = res.get('ingredientLines', None)
    ingredients = '\n'.join(ingredients) if ingredients else None

    des = localize['recipe_en'] if localize['language_data']['code'] != 'en' \
        else EmptyEmbed
    colour = int(
        '0x%02X%02X%02X' % (randint(0, 255), randint(0, 255), randint(0, 255)),
        base=16
    )
    embed = Embed(colour=colour, description=des)
    author = {}
    if 'label' in res and res['label']:
        author['name'] = res['label']
    if 'url' in res and res['url']:
        author['url'] = res['url']
    if author:
        embed.set_author(
            name=author.get('name', EmptyEmbed),
            url=author.get('url', EmptyEmbed)
        )
    if 'image' in res and res['image']:
        embed.set_thumbnail(url=res['image'])
    if 'source' in res and res['source']:
        recipe_source = localize['recipe_source']
        source = res['source']
        recipe_open = localize['recipe_open']
        embed.set_footer(text=f'{recipe_source}{source} | {recipe_open}')
    body = [
        (localize['servings'], servings),
        (localize['calories'], cal_str),
        (localize['cautions'], cautions),
        (localize['diet_labels'], diet_labels),
        (localize['health_labels'], health_labels),
        (localize['ingredients'], ingredients, False)
    ]
    for t in body:
        if t[1]:
            inline = len(t) == 3 and t[-1]
            name = str(t[0])
            val = str(t[1])
            if len(val) > 900:
                too_long = localize['ing_too_long']
                val = val[:900] + f'\n...\n{too_long}'
            embed.add_field(name=name, value=val, inline=inline)
            print(t[0], t[1], inline)
    return embed


def parse_remind_arg(time: str):
    """
    Parse the remind command argument.
    It should look like this hh:mm:ss
    :param time: the time string to be parsed.
    :return: the total time in seconds.
    """
    t = tuple(int(s) for s in time.split(':'))
    if not 1 <= len(t) <= 3:
        raise ValueError
    res = 0
    multi = 1
    for i in reversed(t):
        res += i * multi
        multi *= 60
    return res


async def urban(localize, session_manager: SessionManager, query):
    """
    Search urbandictionary for a word.
    :param localize: the localization strings.
    :param session_manager: the session manager.
    :param query: the search query.
    :return: the search result.
    """
    try:
        url = f'http://api.urbandictionary.com/v0/define?term={query}'
        res = await session_manager.get_json(url)
    except HTTPStatusError as e:
        return [localize['api_error'].format('Urbandictionary') + f'\n{e}']
    else:
        if res['tags']:
            entry = res['list'][0]
            def_ = entry['definition']
            word = entry['word']
            upboats = entry['thumbs_up']
            downboatds = entry['thumbs_down']
            if entry['example']:
                example = entry['example']
            else:
                example = "No example was found."
            def_ = ['```\n' + s.replace('`', chr(0x1fef)) + '\n```' for s in
                    wrap(def_, 1800, replace_whitespace=False)]
            return ([localize['urban_head'].format(word, example)]
                    + def_
                    + [localize['urban_tail'].format(upboats, downboatds)])
        else:
            return [localize['nothing_found']]
