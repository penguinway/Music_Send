import json

import requests


def get_url(name):
    search_url = "https://music.penguinway.space/search?keywords=" + str(name)
    back = requests.get(url=search_url)
    results = back.json()
    print("作品名:" + str(results["result"]["songs"][0]["name"]) + "\n" +
          "作者名:" + str(results["result"]["songs"][0]["artists"][0]["name"]))


def add_json(name):
    with open("music.json", mode="r", encoding="UTF-8") as f:
        file = json.load(f)
    search_url = search_url = "https://music.penguinway.space/search?keywords=" + str(name)
    json_file = {}
    back = requests.get(url=search_url)
    results = back.json()
    json_file["id"] = str(results["result"]["songs"][0]["id"])
    json_file["作品名"] = str(results["result"]["songs"][0]["name"])
    json_file["作者名"] = str(results["result"]["songs"][0]["artists"][0]["name"])
    # music_id = json_file["id"]
    # url_url = "https://music.penguinway.space/song/url/v1?id=" + str(music_id) + "&level=exhigh"
    # geturl = requests.get(url=url_url)
    # result = geturl.json()
    # music_url = result["data"][0]["url"]
    # json_file["url"] = music_url
    json_file["did"] = False
    file.append(json_file)
    with open("music.json", mode="w", encoding="UTF-8") as f:
        json.dump(file, f, indent=4, ensure_ascii=False)


def delete_json(name):
    print(name)
    with open("music.json", mode="r", encoding="UTF-8") as f:
        file = json.load(f)
    if name.isdigit():
        del file[name - 1]
    if not name.isdigit():
        for i in range(0, len(file)):
            if name == file[i]["作品名"]:
                del file[i]
                print("删除成功！")
                break
    print(len(file))
    with open("music.json", mode="w", encoding="UTF-8") as f:
        json.dump(file, f, indent=4, ensure_ascii=False)


def song_send():
    song = []
    with open("music.json", mode="r", encoding="UTF-8") as f:
        song = json.load(f)
    for i in range(0, len(song)):
        if not song[i]["did"]:
            today_song = song[i]
            music_id = today_song["id"]
            url_url = "https://music.penguinway.space/song/url/v1?id=" + str(music_id) + "&level=exhigh"
            geturl = requests.get(url=url_url)
            result = geturl.json()
            music_url = result["data"][0]["url"]
            today_song["did"] = True
            print("今日日推：\n" +
                  "作品名：" + str(today_song["作品名"]) + "\n" +
                  "作者名：" + str(today_song["作者名"]) + "\n" +
                  "播放链接：" + str(music_url)
                  )
            with open("music.json", mode="w", encoding="UTF-8") as f:
                json.dump(song, f, indent=4, ensure_ascii=False)
            break
        else:
            continue


write = input("请输入：")
if "音乐查询#" in write or "查询音乐#" in write:
    names = write[5:]
    get_url(name=names)
elif "添加音乐#" in write or "音乐添加#" in write:
    names = write[5:]
    add_json(name=names)
elif "#日推" in write:
    song_send()
elif "#删除音乐" in write:
    names = write[5:]
    delete_json(name=names)
else:
    pass
