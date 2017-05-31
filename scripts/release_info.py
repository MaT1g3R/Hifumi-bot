from requests import get

URL = 'https://api.github.com/repos/hifumibot/hifumibot/releases'


def get_latest_release() -> str:
    """
    Get the latest release version from the github repo
    :return: the version number of the latest release
    """
    return get(URL + '/latest').json().get('tag_name', '').strip('v')
