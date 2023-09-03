import requests
import plugins
from bridge.bridge import Bridge
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common import const
from common.expired_dict import ExpiredDict
from common.log import logger
from config import conf
from plugins import *


@plugins.register(
    name="Music_send",
    desire_priority=20,
    desc="一个简单的音乐搜索器，基于网易云音乐api",
    namecn="音乐搜索",
    version="ver.2023/09/03",
    author="Penguin_YeTong"
)
class Music_search(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.get_music
        logger.info("[Music]inited")

    def get_music(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        string = e_context["context"].content
        reply = Reply()
        reply.type = ReplyType.TEXT
        msg: ChatMessage = e_context["context"]["msg"]
        if "音乐查询%" in string or "查询音乐%" in string:
            names = string[5:]
            search_url = "https://music.penguinway.space/search?keywords=" + str(names)
            logger.info("request" + search_url)
            back = requests.get(url=search_url)
            results = back.json()
            music_id = results["result"]["songs"][0]["id"]
            url_url = "https://music.penguinway.space/song/url/v1?id=" + str(music_id) + "&level=exhigh"
            geturl = requests.get(url=url_url)
            result = geturl.json()
            music_url = result["data"][0]["url"]
            reply.content = ("\n作品名:" + str(results["result"]["songs"][0]["name"]) + "\n" +
                             "作者名:" + str(results["result"]["songs"][0]["artists"][0]["name"]) +
                             "\n播放链接:" + music_url)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        elif "添加音乐%" in string or "音乐添加%" in string:
            names = string[5:]
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="r", encoding="UTF-8") as f:
                file = json.load(f)
            search_url = search_url = "https://music.penguinway.space/search?keywords=" + str(names)
            logger.info("request" + search_url)
            json_file = {}
            back = requests.get(url=search_url)
            results = back.json()
            json_file["id"] = str(results["result"]["songs"][0]["id"])
            json_file["作品名"] = str(results["result"]["songs"][0]["name"])
            json_file["作者名"] = str(results["result"]["songs"][0]["artists"][0]["name"])
            json_file["did"] = False
            file.append(json_file)
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="w", encoding="UTF-8") as f:
                json.dump(file, f, indent=4, ensure_ascii=False)
            logger.info("添加音乐到json文件中")
            reply.content = "添加成功！\n作品名：" + str(json_file["作品名"]) + "\n作者名：" + str(json_file["作者名"])
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        elif "%日推" == string:
            song = []
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="r", encoding="UTF-8") as f:
                song = json.load(f)
            if song[-1]["did"]:
                reply.content = "列表中已经没有歌曲可以推荐，请添加！"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            for i in range(0, len(song)):
                if not song[i]["did"]:
                    today_song = song[i]
                    music_id = today_song["id"]
                    url_url = "https://music.penguinway.space/song/url/v1?id=" + str(music_id) + "&level=exhigh"
                    geturl = requests.get(url=url_url)
                    result = geturl.json()
                    music_url = result["data"][0]["url"]
                    today_song["did"] = True
                    reply.content = ("今日日推：\n" +
                                     "作品名：" + str(today_song["作品名"]) + "\n" +
                                     "作者名：" + str(today_song["作者名"]) + "\n" +
                                     "播放链接：" + str(music_url)
                                     )
                    e_context["reply"] = reply
                    with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="w", encoding="UTF-8") as f:
                        json.dump(song, f, indent=4, ensure_ascii=False)
                    break
                else:
                    continue
            e_context.action = EventAction.BREAK_PASS
        elif "%查询日推" == string:
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="r", encoding="UTF-8") as f:
                song = json.load(f)
                reply.content = "日推列表为:\n"
            for i in range(0, len(song)):
                reply.content += (str(i+1) + ":" + song[i]["作品名"] + "    " + "播放情况:" + str(song[i]["did"]) + "\n")
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        else:
            e_context.action = EventAction.CONTINUE

    def get_help_text(self, **kwargs):
        help_text = ("使用说明：\n" + "1.查询音乐 命令为: 查询音乐%example or 音乐查询%example\n" +
                     "2.添加音乐到日推列表 命令为: 添加音乐%example or 音乐添加%example\n" +
                     "3.日推 命令为: %日推 (Tip.一般不建议手动进行日推)\n" +
                     "4.查询日推 命令为: %查询日推")
        return help_text
