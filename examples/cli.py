#!/usr/bin/env python3
# Install dependencies with:
# pip install requests_oauth2

from requests_oauth2.services import WeiboClient

if __name__ == '__main__':
    from pip._vendor.distlib.compat import raw_input
    weibo_auth = WeiboClient(
        client_id="3107116953",
        client_secret="8fd3a091eb3bcb0657976cd0f76072b0",
        redirect_uri="http://httpbin.org/get",
    )

    print("Have taken already? (y/n)")
    select = raw_input()
    token = None
    if select is not "y":
        authorization_url = weibo_auth.authorize_url(
            scope=[""],
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

    data = weibo_auth.get("/2/account/get_uid.json").body
    print("=" * 30, " Get  UID ", "=" * 30)
    [print(k, ":", v) for k, v in data.items()]

    data = weibo_auth.get("/2/users/show.json", **data).body
    print("=" * 30, "   Show   ", "=" * 30)
    [print(k, ":", v) for k, v in data.items()]
