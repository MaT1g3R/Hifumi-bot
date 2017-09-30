from itertools import zip_longest

from translations import Translation


def test_language():
    tr = Translation()
    en = tr.en
    for lan, val in tr._data.items():
        if lan == 'en':
            continue
        for file_name, file_data in val.items():
            assert file_name in en
            for key, en_key in zip_longest(
                    file_data.keys(), en[file_name].keys()):
                assert not key or key in en[file_name]
                assert (
                    tr.get(lan, file_name, en_key) ==
                    tr.get(lan, file_name[:-5], en_key)
                )
                if en_key in file_data:
                    assert (
                        tr.get(lan, file_name, en_key) !=
                        tr.get('en', file_name, en_key)
                    )
                else:
                    assert (
                        tr.get(lan, file_name, en_key) ==
                        tr.get('en', file_name, en_key)
                    )
