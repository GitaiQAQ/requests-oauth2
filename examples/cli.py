#!/usr/bin/env python3
# Install dependencies with:
# pip install requests_oauth2
from requests_oauth2.oauth2 import query_parse, jsonp_parse
from requests_oauth2.services import WeiboClient, QQClient, WeChatClient

if __name__ == '__main__':
    from pip._vendor.distlib.compat import raw_input
    weibo_auth = WeChatClient(
        client_id="wx02a105ad87680fa5",
        client_secret="a780e68da05cafa3578b602101951858",
        redirect_uri="http://localhost.test:8000/accounts/oauth/weixin",
    )

    print("Have taken already? (y/n)")
    select = raw_input()
    token = None
    if select is not "y":
        authorization_url = weibo_auth.authorize_url(
            response_type="code",
        )
        print("Authorization url: ", authorization_url)

        print("Type Authorization Code: ")
        code = raw_input()
        token = weibo_auth.get_token(
            code=code,
            grant_type="authorization_code",
        )

    if not token:
        print("Type Token: ")
        token = raw_input()
        weibo_auth.update(access_token=token)
    print("Token: ", token)

    print("=" * 30, "  OpenID  ", "=" * 30)
    data = weibo_auth.get_uid()
    [print(k, ":", v) for k, v in data.items()]

    print("=" * 30, "   Show   ", "=" * 30)
    data = weibo_auth.get_user_info(**data)
    [print(k, ":", v) for k, v in data.items()]
