from requests_oauth2 import OAuth2


class GoogleClient(OAuth2):
    site = "https://accounts.google.com"
    authorization_url = "/o/oauth2/auth"
    token_url = "/o/oauth2/token"
    scope_sep = " "


class FacebookClient(OAuth2):
    site = "https://www.facebook.com/"
    authorization_url = "/dialog/oauth"
    token_url = "/oauth/access_token"
    scope_sep = " "


class InstagramClient(OAuth2):
    site = "https://api.instagram.com"
    authorization_url = "/oauth/authorize"
    token_url = "/oauth/access_token"
    scope_sep = " "


class QQClient(OAuth2):
    site = "https://graph.qq.com"
    authorization_url = "/oauth2.0/authorize"
    token_url = "/oauth2.0/token"
    scope_sep = ","

    def __init__(self, **kwargs):
        super(QQClient, self).__init__(**kwargs)
        self.oauth_consumer_key = self.client_id

    def _request(self, method, url, **kwargs):
        response = super(QQClient, self)._request(method, url, **kwargs)
        if "code" in response.body:
            raise Exception(response.body, response.url)
        if "ret" in response.body and response.body.get("ret") < 0:
            raise Exception(response.body, response.url)
        return response


class WeiboClient(OAuth2):
    def __init__(self, **kwargs):
        super(WeiboClient, self).__init__(
            site="https://api.weibo.com",
            authorization_url="/oauth2/authorize",
            token_url="/oauth2/access_token",
            scope_sep=",",
            **kwargs
        )

    def _request(self, method, url, **kwargs):
        response = super(WeiboClient, self)._request(method, url, **kwargs)
        if "error" in response.body:
            raise Exception(response.body)
        return response


class YibanClient(OAuth2):
    site = "https://openapi.yiban.cn"
    authorization_url = "/oauth/authorize"
    token_url = "/oauth/access_token"
    scope_sep = " "

    def _request(self, method, url, **kwargs):
        response = super(YibanClient, self)._request(method, url, **kwargs)
        if "status" in response.body and response.body['status'] is 'error':
            raise Exception(response.body, response.url)
        return response
    # .body['info']

