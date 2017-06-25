from aiohttp import ClientResponse, ClientResponseError, ClientSession


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

    def __del__(self):
        """
        Class destructor, close the client session.
        """
        self.session.close()

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
        :raises: ClientResponseError if status code isn't 200
        """
        async with self.session.get(
                url, allow_redirects=allow_redirects, **kwargs) as r:
            if 200 <= r.status < 300:
                return r
            raise ClientResponseError
