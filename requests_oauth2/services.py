import json
from urllib.parse import urlencode

from requests_oauth2 import OAuth2
from requests_oauth2.errors import QQError, WeChatError, WeiboError, YibanError
from requests_oauth2.oauth2 import query, jsonp_parse, check_configuration


class OAuth2Encoder(json.JSONEncoder):
    def default(self, obj: OAuth2):
        if isinstance(obj, OAuth2):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class BaseProfile(object):
    def get_uid(self):
        raise NotImplementedError

    def get_user_info(self, **kwargs):
        raise NotImplementedError


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


class QQClient(OAuth2, BaseProfile):
    site = "https://graph.qq.com"
    authorization_url = "/oauth2.0/authorize"
    token_url = "/oauth2.0/token"
    scope_sep = ","

    @property
    def oauth_consumer_key(self):
        return self.client_id

    @query("access_token", "oauth_consumer_key")
    def get(self, *args, **kwargs):
        return self._request("GET", *args, **kwargs)

    def _request(self, method, url, **kwargs):
        response = super(QQClient, self)._request(method, url, **kwargs)
        if "code" in response.body:
            raise QQError(response.url, **response.body)
        if "ret" in response.body and response.body.get("ret") < 0:
            raise QQError(response.url, **response.body)
        return response

    def get_uid(self):
        return jsonp_parse(self.get("/oauth2.0/me").body)

    def get_user_info(self, openid=None, **kwargs):
        return jsonp_parse(self.get("/user/get_user_info", openid=openid).body)


class WeChatClient(OAuth2, BaseProfile):
    site = "https://api.weixin.qq.com"
    authorization_url = "https://open.weixin.qq.com/connect/oauth2/authorize"
    qrconnect_url = "https://open.weixin.qq.com/connect/qrconnect"
    token_url = "/sns/oauth2/access_token"
    scope_sep = ","
    openid = None

    @property
    def appid(self):
        return self.client_id

    # Scopes
    # 小程序&PC 开发者工具： snsapi_login
    # 服务号： snsapi_base, snsapi_userinfo
    @check_configuration("authorization_url", "redirect_uri", "client_id", "scope_sep")
    def authorize_url(self, scope="snsapi_base, snsapi_userinfo", user_agent=None, **kwargs):
        # if scope is "snsapi_base, snsapi_userinfo":
        #     if user_agent and "miniProgram" in user_agent:
        #         scope = "snsapi_login"

        if user_agent and "MicroMessenger" in user_agent:
            return self.wechat_connect(scope, **kwargs)
        return self.qrconnect(scope, **kwargs)

    @check_configuration("authorization_url", "redirect_uri", "client_id", "scope_sep")
    def qrconnect(self, scope, redirect=None, **kwargs):
        """
        微信扫码登录，需要开通相关服务
        """
        if isinstance(scope, (list, tuple, set, frozenset)):
            scope = self.scope_sep.join(scope)
        oauth_params = {
            'appid': self.appid,
            'redirect_uri': self.redirect_uri,
            'response_type': "code",
            'scope': scope,
            'state': redirect
        }
        oauth_params.update(kwargs)
        return "%s?%s" % (self.qrconnect_url,
                          urlencode(oauth_params))

    @check_configuration("authorization_url", "redirect_uri", "client_id", "scope_sep")
    def wechat_connect(self, scope, redirect=None, **kwargs):
        """
        微信内部登陆
        """
        if isinstance(scope, (list, tuple, set, frozenset)):
            scope = self.scope_sep.join(scope)
        oauth_params = {
            'appid': self.appid,
            'redirect_uri': self.redirect_uri,
            'response_type': "code",
            'scope': scope,
            'state': redirect
        }
        oauth_params.update(kwargs)
        return "%s?%s" % (self.authorization_url,
                          urlencode(oauth_params))

    def get_token(self, code, **kwargs):
        return super(WeChatClient, self).get_token(code=code,
                                                   appid=self.appid,
                                                   secret=self.client_secret,
                                                   **kwargs)

    @query("access_token", "appid")
    def get(self, *args, **kwargs):
        response = self._request("GET", *args, **kwargs)
        for i in response.body:
            if type(response.body[i]) is str:
                response.body[i] = response.body[i].encode('iso-8859-1').decode('utf-8')
        return response

    def _request(self, method, url, **kwargs):
        response = super(WeChatClient, self)._request(method, url, **kwargs)
        if "code" in response.body:
            raise WeChatError(response.url, **response.body)
        if "ret" in response.body and response.body.get("ret") < 0:
            raise WeChatError(response.url, **response.body)
        return response

    def get_uid(self):
        return {"openid": self.openid}

    @query("access_token", "openid")
    def get_user_info(self, **kwargs):
        return self.get("/sns/userinfo", lang="zh_CN", **kwargs).body


class WeiboClient(OAuth2):
    site = "https://api.weibo.com"
    authorization_url = "/oauth2/authorize"
    token_url = "/oauth2/access_token"
    scope_sep = ","

    def _request(self, method, url, **kwargs):
        response = super(WeiboClient, self)._request(method, url, **kwargs)
        if "error" in response.body:
            raise WeiboError(url, **response.body)
        return response

    def get_uid(self):
        return jsonp_parse(self.get("/2/account/get_uid.json").body)

    def get_user_info(self, uid=None, **kwargs):
        return jsonp_parse(self.get("/2/users/show.json", uid=uid).body)


class YibanClient(OAuth2):
    site = "https://openapi.yiban.cn"
    authorization_url = "/oauth/authorize"
    token_url = "/oauth/access_token"
    scope_sep = " "

    def _request(self, method, url, **kwargs):
        response = super(YibanClient, self)._request(method, url, **kwargs)
        if "status" in response.body and response.body['status'] == 'error':
            raise YibanError(response.url, **response.body["info"])
        return response

    # .body['info']

    def get_uid(self):
        # openid
        if not hasattr(self, "userid"):
            self.userid = self.get_user_info()["yb_userid"]
        return {"openid": self.userid}

    def get_user_info(self, **kwargs):
        # yb_userid, yb_username, yb_usernick, yb_sex, yb_money, yb_exp, yb_userhead, yb_schoolid, yb_schoolname,
        # yb_regtime
        return jsonp_parse(self.get("/user/me").body["info"])
