#!/usr/bin/env python3
# Install dependencies with:
# pip install requests_oauth2

from requests_oauth2.services import WeiboClient

if __name__ == '__main__':
    weibo_auth = WeiboClient(
        client_id="34333455",
        client_secret="79b3ed171fc8936df2dc36358272fce6",
        redirect_uri="http://localhost:5000/accounts/oauth/weibo.do",
    )

    authorization_url = weibo_auth.authorize_url(
        scope=[""],
        response_type="code",
    )
    print("Authorization url: ", authorization_url)

    from pip._vendor.distlib.compat import raw_input

    code = raw_input()
    token = weibo_auth.get_token(
        code=code,
        grant_type="authorization_code",
    )
    print("Token: ", token)

    data = weibo_auth.get("/2/account/get_uid.json").body
    print("Data UID: ", data)

    data = weibo_auth.get("/2/users/show.json", **data).body
    print("Info: ", data)
