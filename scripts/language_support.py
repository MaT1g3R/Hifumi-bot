"""
A collection of functions to deal with language support
"""

from pathlib import Path

from scripts.data_controller import set_language_, delete_language_
from scripts.file_io import read_all_files, read_json
from scripts.helpers import suplement_dict


def read_language(path: Path):
    """
    Read all language files and return it in a dict
    :param path: the path that points to the language folder
    :return: all language files in a dict
    """
    language = {f.name[:-5]: read_json(f.open(encoding='utf-8'))
                for f in read_all_files(path)
                if f.name.endswith('.json')}
    for key, val in language.items():
        if key != 'en':
            new_val = suplement_dict(language['en'], val)
            language[key] = new_val
    return language


def generate_language_entry(language_data):
    """
    Generate a string representation of a language
    :param language_data: the language data dict
    :return: the string representation of a language
    """
    return '{} / {} ({})\n'.format(
        language_data['native_name'], language_data['english_name'],
        language_data['code']
    )


def generate_language_list(language, key):
    """
    Generate a string representation of all languages
    :param language: all languages
    :param key: the language key for the server
    :return: string representation of all languages
    """
    language_dict = language[key]
    lst = []
    for val in language.values():
        lst.append(val['language_data'])
    lst.sort(key=lambda x: x['code'])
    s = ''
    for l in lst:
        s += '* ' + generate_language_entry(l) + '\n'
    return language_dict['language_list'].format(s)


def set_language(bot, ctx, language, delete=False):
    """
    Set the language for the server, and return the message
    :param bot: the bot
    :param ctx: the discord context
    :param language: the language to set to
    :param delete: True of deleting the server language info from the db
    :return: the message
    """
    conn = bot.conn
    cur = bot.cur
    server_id = ctx.message.server.id
    if delete:
        delete_language_(conn, cur, server_id)
    else:
        set_language_(conn, cur, server_id, language)
    localize = bot.get_language_dict(ctx)
    language_data = localize['language_data']
    translators = language_data['translators']
    return localize['lan_set_success'].format(
        generate_language_entry(language_data), ', '.join(translators)
    )
