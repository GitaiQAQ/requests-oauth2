class OAuth2Error(Exception):
    pass


class ConfigurationError(OAuth2Error):
    def __init__(self, *args):
        super(ConfigurationError, self).__init__("c001", *args)


class ServicesError(OAuth2Error):
    def __init__(self, *args):
        super(ServicesError, self).__init__(*args)


class QQError(ServicesError):
    def __init__(self, *args, **kwargs):
        # { "ret":1002, "msg":"请先登录" }
        # http://wiki.connect.qq.com/get_user_info
        super(QQError, self).__init__(kwargs.get("ret"), kwargs.get("msg"), *args)


class WeChatError(ServicesError):
    def __init__(self, *args, **kwargs):
        # {"errcode":40003,"errmsg":"invalid openid hint: [c49C4a0396ge21]"}
        # https://mp.weixin.qq.com/wiki?action=doc&id=mp1433747234
        super(WeChatError, self).__init__(kwargs.get("errcode"), kwargs.get("errmsg"), *args)


class WeiboError(ServicesError):
    def __init__(self, *args, **kwargs):
        # {
        # 	"request" : "/statuses/home_timeline.json",
        # 	"error_code" : "20502",
        # 	"error" : "Need you follow uid."
        # }
        # https://open.weibo.com/wiki/Error_code
        super(WeiboError, self).__init__(kwargs.get("error_code"), kwargs.get("error"), *args)


class YibanError(ServicesError):
    def __init__(self, *args, **kwargs):
        # {
        #   "status":"error",
        #   "info":{
        #     "code":"错误编号",
        #     "msgCN":"中文报错信息",
        #     "msgEN":"英文报错信息"
        #   }
        # }
        super(YibanError, self).__init__(kwargs.get("code"), kwargs.get("msgCN"), *args)
