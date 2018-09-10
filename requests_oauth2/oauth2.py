import json
import logging
from functools import lru_cache

import requests

from six.moves.urllib.parse import quote, urlencode, parse_qsl, urljoin

from requests_oauth2.errors import ConfigurationError

logger = logging.getLogger("requests.oauth2")


def check_configuration(*attrs):
    """Check that each named attr has been configured
    """

    def real_decorator(fn, *args, **kwargs):
        def wrapped(self, *args, **kwargs):
            for attr in attrs:
                val = getattr(self, attr, getattr(kwargs, attr, getattr(args, attr, None)))
                if val is None:
                    raise ConfigurationError("{} not configured".format(attr))
            return fn(self, *args, **kwargs)

        return wrapped

    return real_decorator


def query(*attrs):
    """Check that each named attr has been configured
    """
    def real_decorator(fn, *args, **kwargs):
        def wrapped(self, *args, **kwargs):
            for attr in attrs:
                val = getattr(self, attr, kwargs.get(attr, getattr(args, attr, None)))
                if val is None:
                    raise ConfigurationError("{} not configured".format(attr))
                else:
                    kwargs.setdefault(attr, val)
            return fn(self, *args, **kwargs)

        return wrapped

    return real_decorator


def query_parse(txt):
    if type(txt) is dict:
        return txt
    qs = parse_qsl(txt)
    ret = dict(qs)
    return _check_expires_in(ret)


def jsonp_parse(jsonp_str, cbn="callback"):
    if type(jsonp_str) is dict:
        return jsonp_str
    _jsonp_begin = (cbn or "callback") + '('
    _jsonp_end = ');'
    jsonp_str = jsonp_str.strip()
    if not jsonp_str.startswith(_jsonp_begin) or \
            not jsonp_str.endswith(_jsonp_end):
        raise ValueError('Invalid JSONP')
    return json.loads(jsonp_str[len(_jsonp_begin):-len(_jsonp_end)])


def text_parse(txt):
    return txt


def _check_expires_in(ret):
    expires_in = ret.get('expires_in')
    if expires_in and expires_in.isdigit():
        ret['expires_in'] = int(expires_in)
    return ret


class OAuth2(object):
    client_id: str = None
    client_secret: str = None

    access_token: str = None
    expires_in: str = None
    refresh_token: str = None

    site: str = None
    redirect_uri: str = None
    authorization_url: str = '/oauth2/authorize'
    token_url: str = '/oauth2/token'
    refresh_url: str = '/oauth2/refresh'
    revoke_url: str = '/oauth2/revoke'
    scope_sep: str = ','

    _header_authorization_format: str = "Bearer %s"

    def __init__(self, **kwargs):
        """
        Initializes the hook with OAuth2 parameters
        """
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        if hasattr(self, "_" + key):
            self.__dict__["_" + key] = value
        else:
            self.__dict__[key] = value

    def get_attr(self, key, **kwargs):
        return kwargs.get(key, getattr(self, key))

    @property
    def headers(self, **kwargs):
        return {'Authorization': self.get_attr('_header_authorization_format',
                                               **kwargs) % self.get_attr('access_token')}

    @property
    def submitted_attrs(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def _request(self, method, url, **kwargs):
        """
        Make a request to an OAuth2 endpoint
        """
        params = None
        data = None

        if method in ('POST', 'PUT'):
            data = kwargs
        else:
            params = kwargs

        logger.debug("- url: %s" % urljoin(self.site, url))
        logger.debug("- method: %s" % method)
        logger.debug("- headers: %s" % self.headers)
        logger.debug("- kwargs: %s" % kwargs)
        logger.debug("- data: %s" % data)
        logger.debug("- params: %s" % params)

        response = requests.request(method, urljoin(self.site, url),
                                    params=params,
                                    data=data,
                                    headers=self.headers,
                                    allow_redirects=True)

        logger.debug("- content-type: %s" % response.headers.get("content-type"))
        logger.debug("- body: %s" % response.text)
        try:
            response.body = response.json()
        except:
            response.body = response.text
        return response

    @query("access_token", )
    def get(self, *args, **kwargs):
        return self._request("GET", *args, **kwargs)

    @check_configuration("authorization_url", "redirect_uri", "client_id", "scope_sep")
    def authorize_url(self, scope='', **kwargs):
        """
        Returns the url to redirect the user to for user consent
        """
        if isinstance(scope, (list, tuple, set, frozenset)):
            scope = self.scope_sep.join(scope)

        oauth_params = {
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'scope': scope,
        }
        oauth_params.update(kwargs)
        return "%s?%s" % (urljoin(self.site, self.authorization_url),
                          urlencode(oauth_params))

    @check_configuration("token_url", )
    @query("client_id", "client_secret", "redirect_uri", "code", )
    def get_token(self, code, **kwargs):
        """.
        Requests an access token
        """
        if self.access_token is None:
            response = self._request("POST", self.token_url, code=code, **kwargs)
            if type(response.body) is dict:
                self.update(**response.body)
            response.body = query_parse(response.body)
            if type(response.body) is dict:
                self.update(**response.body)
        return self.access_token

    @check_configuration("refresh_token", )
    @query("client_id", "client_secret", )
    def refresh_token(self, **kwargs):
        """
        Request a refreshed token
        """
        return self.get(self.refresh_token,
                        client_secret=self.client_secret,
                        **kwargs)

    @check_configuration("revoke_url", )
    @query("client_id", "client_secret", )
    def revoke_token(self, **kwargs):
        """
        Revoke an access token
        """
        return self.get(self.revoke_url, **kwargs)
