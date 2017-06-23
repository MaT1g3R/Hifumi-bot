"""
A collection of functions to deal with language support
"""

from pathlib import Path

from scripts.file_io import load_json
from scripts.helpers import read_all_files, suplement_dict


def read_language(path: Path):
    """
    Read all language files and return it in a dict
    :param path: the path that points to the language folder
    :return: all language files in a dict
    """
    language = {
        f.name[:-5]: load_json(f, encoding='utf-8')
        for f in read_all_files(path)
        if f.name.endswith('.json')
    }
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
