#!/usr/bin/env python3
# Install dependencies with:
# pip install requests_oauth2
from requests_oauth2.oauth2 import query_parse, jsonp_parse
from requests_oauth2.services import WeiboClient, QQClient, WeChatClient, YibanClient

if __name__ == '__main__':
    from pip._vendor.distlib.compat import raw_input
    # weibo_auth = WeChatClient(
    #     client_id="wx02a105ad87680fa5",
    #     client_secret="a780e68da05cafa3578b602101951858",
    #     redirect_uri="http://localhost.test:8000/accounts/oauth/weixin",
    # )
    yiban_auth = YibanClient(
        client_id="5e22fe99e06b4cee",
        client_secret="c0d02efd3362af2e03c6db73b4323b95",
        redirect_uri="http://localhost:8000/accounts/oauth/yiban",
    )

    print("Have taken already? (y/n)")
    select = raw_input()
    token = None
    if select is not "y":
        authorization_url = yiban_auth.authorize_url(
            response_type="code",
        )
        print("Authorization url: ", authorization_url)

        print("Type Authorization Code: ")
        code = raw_input()
        token = yiban_auth.get_token(
            code=code,
            grant_type="authorization_code",
        )

    if not token:
        print("Type Token: ")
        token = raw_input()
        yiban_auth.update(access_token=token)
    print("Token: ", token)

    print("=" * 30, "  OpenID  ", "=" * 30)
    data = yiban_auth.get_uid()
    [print(k, ":", v) for k, v in data.items()]

    print("=" * 30, "   Show   ", "=" * 30)
    data = yiban_auth.get_user_info(**data)
    [print(k, ":", v) for k, v in data.items()]
