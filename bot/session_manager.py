from asyncio import get_event_loop
from http import HTTPStatus
from logging import WARN

from aiohttp import ClientResponse, ClientSession
from demjson import decode
from requests import get


class HTTPStatusError(Exception):
    def __init__(self, code: int, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return f'HTTPStatusError: Code: {self.code} Message: {self.msg}'

    def __repr__(self):
        return f'HTTPStatusError({self.code}, {self.msg})'


class SessionManager:
    """
    An aiohttp client session manager.
    """

    def __init__(self, session: ClientSession, logger):
        """
        Initialize the instance of this class.
        """
        self.session = session
        self.logger = logger
        self.codes = {
            val.value: key
            for key, val in HTTPStatus.__members__.items()
        }

    def __del__(self):
        """
        Class destructor, close the client session.
        """
        self.session.close()

    def get_msg(self, code: int):
        """
        Get the message from an HTTP status code.
        :param code: the status code.
        :return: the message.
        """
        try:
            return self.codes[code]
        except KeyError:
            return None

    def return_response(self, res, code):
        """
        Return an Aiohttp or Request response object.
        :param res: the response.
        :param code: the response code.
        :return: the response object.
        :raises: HTTPStatusError if status code isn't 200
        """
        if 200 <= code < 300:
            return res
        raise HTTPStatusError(code, self.get_msg(code))

    def __json_sync(self, url, params):
        """
        Return the json content from an HTTP request using requests.
        :param url: the url.
        :param params: the request params.
        :return: the json content in a python dict.
        :raises HTTPStatusError: if the status code isn't in the 200s
        """
        try:
            res = self.sync_get(url, params)
        except HTTPStatusError as e:
            raise e
        else:
            return res.json()

    async def __json_async(self, url, params):
        """
        Return the json content from an HTTP request using Aiohttp.
        :param url: the url.
        :param params: the request params.
        :return: the json content in a python dict.
        :raises HTTPStatusError: if the status code isn't in the 200s
        """
        try:
            res = await self.get(url, params=params)
        except HTTPStatusError as e:
            raise e
        else:
            try:
                return await res.json()
            except Exception as e:
                self.logger.log(WARN, str(e))
                text = await res.text()
                return decode(text)

    async def get_json(self, url: str, params: dict = None):
        """
        Get the json content from an HTTP request.
        :param url: the url.
        :param params: the request params.
        :return: the json content in a dict if success, else the error message.
        :raises HTTPStatusError: if the status code isn't in the 200s
        """
        try:
            return await self.__json_async(url, params)
        except Exception as e:
            if isinstance(e, HTTPStatusError):
                raise e
            else:
                self.logger.log(WARN, str(e))
                return self.__json_sync(url, params)

    def sync_get(self, url, params, **kwargs):
        """
        A fall back get method using requests.get
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query
        string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        :raises: HTTPStatusError if status code isn't 200
        """
        res = get(url, params=params, **kwargs)
        return self.return_response(res, code=res.status_code)

    async def get(
            self, url, *, allow_redirects=True, **kwargs) -> ClientResponse:
        """
        Make HTTP GET request
        :param url: Request URL, str or URL
        :param allow_redirects: If set to False, do not follow redirects.
        True by default (optional).
        :param kwargs: In order to modify inner request parameters,
        provide kwargs.
        :return: a client response object.
        :raises: HTTPStatusError if status code isn't 200
        """
        async with self.session.get(
                url, allow_redirects=allow_redirects, **kwargs) as r:
            return self.return_response(r, r.status)


class l:
    def log(self, *args, **kwagrs):
        print(args, kwagrs)


async def foo():
    s = SessionManager(ClientSession(), l())
    url = 'https://rra.ram.moe/i/r?'
    params = {
        'type': 'nsfw-gtn',
        'nsfw': 'true'
    }
    base_error = '{}'
    r = await s.get_json(url, base_error, params)
    print(r)


if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(foo())
