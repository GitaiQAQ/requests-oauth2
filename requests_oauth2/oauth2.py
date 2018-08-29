import json
from functools import lru_cache

import requests

from six.moves.urllib.parse import quote, urlencode, parse_qs, urljoin

from requests_oauth2.errors import ConfigurationError


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


def from_query(txt):
    qs = parse_qs(txt)
    ret = dict(qs)
    return _check_expires_in(ret)


def from_jsonp(jsonp_str, cbn="callback"):
    _jsonp_begin = (cbn or "callback") + '('
    _jsonp_end = ');'
    jsonp_str = jsonp_str.strip()
    if not jsonp_str.startswith(_jsonp_begin) or \
            not jsonp_str.endswith(_jsonp_end):
        raise ValueError('Invalid JSONP')
    return json.loads(jsonp_str[len(_jsonp_begin):-len(_jsonp_end)])


def from_text(txt):
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

    _site: str = None
    _redirect_uri: str = None
    _authorization_url: str = '/oauth2/authorize'
    _token_url: str = '/oauth2/token'
    _refresh_url: str = '/oauth2/refresh'
    _revoke_url: str = '/oauth2/revoke'
    _scope_sep: str = ','

    _header_authorization_format: str = "Bearer %s"

    def __init__(self, **kwargs):
        """
        Initializes the hook with OAuth2 parameters
        """
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            try:
                if hasattr(self, k):
                    setattr(self, k, v)
            except:
                setattr(self, "_" + k, v)

    @property
    def site(self) -> str:
        return self._site

    @property
    def redirect_uri(self) -> str:
        return urljoin(self.site, self._redirect_uri)

    @property
    def authorization_url(self) -> str:
        return urljoin(self.site, self._authorization_url)

    @property
    def token_url(self) -> str:
        return urljoin(self.site, self._token_url)

    @property
    def refresh_url(self) -> str:
        return urljoin(self.site, self._refresh_url)

    @property
    def revoke_url(self) -> str:
        return urljoin(self.site, self._revoke_url)

    @property
    def scope_sep(self) -> str:
        return self._scope_sep

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

        print("url: %s" % urljoin(self.site, url))
        print("method: %s" % method)
        print("headers: %s" % self.headers)
        print("kwargs: %s" % kwargs)
        print("data: %s" % data)
        print("params: %s" % params)

        response = requests.request(method, urljoin(self.site, url),
                                    params=params,
                                    data=data,
                                    headers=self.headers,
                                    allow_redirects=True)
        if "json" in response.headers.get("content-type"):
            response.body = response.json()
        else:
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
        return "%s?%s" % (self.authorization_url,
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
