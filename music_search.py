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
    version="1.0 2023/09/03 v2.0 2023/09/26",
    author="Penguin"
)
class Music_search(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.get_music
        logger.info("[Music]载入成功")

    def get_url(self, name_or_id, mode):
        request_url = ""
        if mode == "search":
            request_url = "https://music.penguinway.space/search?keywords=" + str(name_or_id)
        if mode == "get":
            request_url = "https://music.penguinway.space/song/url/v1?id=" + str(name_or_id) + "&level=exhigh"
        re = requests.get(url=request_url)
        return re.json()

    def clear_file(self, data, re):
        max_len = 30
        songs = []
        if len(data) > max_len:
            songs = [song for song in data if not song["did"]]
            re += "\n已清理多余音乐！"
            logger.info("已清理多余音乐！")
        return songs, re

    def get_music(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        string = e_context["context"].content
        reply = Reply()
        reply.type = ReplyType.TEXT
        msg: ChatMessage = e_context["context"]["msg"]

        if "音乐查询%" in string or "查询音乐%" in string:
            names = string[5:]
            if names == "":
                reply.content = "音乐名为空！请输入正确的音乐名！\n"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            results_search = self.get_url(name_or_id=names, mode="search")
            logger.info("查询音乐:" + str(names))
            music_id = results_search["result"]["songs"][0]["id"]
            result_get = self.get_url(name_or_id=music_id, mode="get")
            music_url = result_get["data"][0]["url"]
            logger.info("播放链接:" + str(music_url))
            reply.content = ("\n作品名:" + str(results_search["result"]["songs"][0]["name"]) +
                             "\n作者名:" + str(results_search["result"]["songs"][0]["artists"][0]["name"]) +
                             "\n播放链接:" + music_url)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

        elif "添加音乐%" in string or "音乐添加%" in string:
            names = string[5:]
            if names == "":
                reply.content = "音乐名为空！请输入正确的音乐名！\n"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="r", encoding="UTF-8") as f:
                file = json.load(f)
            results = self.get_url(name_or_id=names, mode="search")
            logger.info("添加音乐:" + str(names))
            json_file = {
                "id": str(results["result"]["songs"][0]["id"]),
                "作品名": str(results["result"]["songs"][0]["name"]),
                "作者名": str(results["result"]["songs"][0]["artists"][0]["name"]),
                "did": False
            }
            file.append(json_file)
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="w", encoding="UTF-8") as f:
                json.dump(file, f, indent=4, ensure_ascii=False)
            logger.info("添加音乐到json文件中成功")
            reply.content = ("添加成功！\n作品名："
                             + str(json_file["作品名"])
                             + "\n作者名："
                             + str(json_file["作者名"]))
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

        elif "%音乐日推" == string or "%日推音乐" == string:
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="r", encoding="UTF-8") as f:
                song = json.load(f)
            if song[-1]["did"]:
                reply.content = "列表中已经没有歌曲可以推荐，请添加！"
                logger.info("列表为空！退出！")
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            for today_song in song:
                if not today_song["did"]:
                    music_id = today_song["id"]
                    result = self.get_url(name_or_id=music_id, mode="get")
                    music_url = result["data"][0]["url"]
                    today_song["did"] = True
                    reply.content = ("今日日推:" +
                                     "\n作品名：" + str(today_song["作品名"]) +
                                     "\n作者名：" + str(today_song["作者名"]) +
                                     "\n播放链接：" + str(music_url)
                                     )
                    break
                else:
                    continue
            songs, reply.content = self.clear_file(data=song, re=reply.content)
            e_context["reply"] = reply
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="w", encoding="UTF-8") as f:
                json.dump(songs, f, indent=4, ensure_ascii=False)
            e_context.action = EventAction.BREAK_PASS

        elif "%查询日推" == string or "%日推查询" == string:
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="r", encoding="UTF-8") as f:
                song = json.load(f)
                reply.content = "日推列表为:\n"
            for i in range(0, len(song)):
                reply.content += (
                        str(i + 1) + ":"
                        + song[i]["作品名"]
                        + "    "
                        + "播放情况:" + str(song[i]["did"]) + "\n")
            songs, reply.content = self.clear_file(data=song, re=reply.content)
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="w", encoding="UTF-8") as f:
                json.dump(songs, f, indent=4, ensure_ascii=False)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

        elif "删除音乐%" in string or "音乐删除%" in string:
            name = string[5:]
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="r", encoding="UTF-8") as f:
                file = json.load(f)
            if not name.isdigit():
                for song in file:
                    if name == song["作品名"]:
                        del song
                        logger.info("删除列表项")
                        reply.content = "删除成功！"
                        break
                    if song == file[-1]:
                        reply.content = "查无此曲！"
            else:
                reply.content = "请输入正确的作品名！"
            with open("/chatgpt-on-wechat/plugins/music_url/music.json", mode="w", encoding="UTF-8") as f:
                json.dump(file, f, indent=4, ensure_ascii=False)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        else:
            e_context.action = EventAction.CONTINUE

    def get_help_text(self, **kwargs):
        help_text = ("使用说明：\n" + "1.查询音乐 命令为: 查询音乐%example or 音乐查询%example\n" +
                     "2.添加音乐到日推列表 命令为: 添加音乐%example or 音乐添加%example\n" +
                     "3.日推 命令为: %音乐日推 or %日推音乐 (Tip.一般不建议手动进行日推)\n" +
                     "4.查询日推 命令为: %查询日推 or %日推查询\n" +
                     "5.删除列表项 命令为: 删除音乐%example or 音乐删除%example (Tip.[example]仅可为作品名)")
        return help_text
