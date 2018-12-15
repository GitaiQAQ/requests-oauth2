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
    wechat_auth = WeChatClient(
        client_id="wx422c46c53d2bae37",
        client_secret="4cbc181555f15195f3ba92a84671a526",
        redirect_uri="https://m.joblabx.com/account/oauth/wechat",
    )
    # wechat_auth = YibanClient(
    #     client_id="e7c07edf7fa39a0e",
    #     client_secret="d7b078b7bdbdd337ede83951c0cda372",
    #     redirect_uri="https://m.joblabx.com/accounts/oauth/yiban",
    # )

    print("Have taken already? (y/n)")
    select = raw_input()
    token = None
    if select is not "y":
        authorization_url = wechat_auth.authorize_url(
            response_type="code",
        )
        print("Authorization url: ", authorization_url)

        print("Type Authorization Code: ")
        code = raw_input()
        token = wechat_auth.get_token(
            code=code,
            grant_type="authorization_code",
        )

    if not token:
        print("Type Token: ")
        token = raw_input()
        wechat_auth.update(access_token=token)
    print("Token: ", token)

    print("=" * 30, "  OpenID  ", "=" * 30)
    data = wechat_auth.get_uid()
    [print(k, ":", v) for k, v in data.items()]

    print("=" * 30, "   Show   ", "=" * 30)
    data = wechat_auth.get_user_info(**data)
    [print(k, ":", v) for k, v in data.items()]
