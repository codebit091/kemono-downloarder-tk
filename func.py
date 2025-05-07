from pathlib import Path
import requests
import json
import time


# 禁止文字置換
def rename_for_windows(name):
    while True:
        tmp = name
        # 半角文字の削除
        name = name.translate(
            (
                str.maketrans(
                    {
                        "\a": "",
                        "\b": "",
                        "\f": "",
                        "\n": "",
                        "\r": "",
                        "\t": "",
                        "\v": "",
                        "'": "'",
                        '"': '"',
                        "\0": "",
                    }
                )
            )
        )
        # エスケープシーケンスを削除
        name = name.translate(
            (
                str.maketrans(
                    {
                        "\\": "￥",
                        "/": "／",
                        ":": "：",
                        "*": "＊",
                        "?": "？",
                        '"': "”",
                        ">": "＞",
                        "<": "＜",
                        "|": "｜",
                    }
                )
            )
        )
        # 先頭/末尾のドットの削除
        name = name.strip(".")
        # 先頭/末尾の半角スペースを削除
        name = name.strip(" ")
        # 先頭/末尾の全角スペースを削除
        name = name.strip("　")

        if name == tmp:
            break

    return name


# API接続
def access_api(input_url: str, index: int = 0) -> dict:
    service = input_url.split("/")[3]
    creator_id = input_url.split("/")[5]
    api_url = (
        f"https://kemono.su/api/v1/{service}/user/{creator_id}/posts-legacy?o={index}"
    )
    try:
        res = requests.get(api_url)
        res.raise_for_status()
        time.sleep(1)
        res_json = res.json()
    except requests.exceptions.RequestException as e:
        print("API通信エラー：", e)
    return res_json


# ディレクトリ作成
def make_dir(artist_data: dict) -> tuple:
    artist_name = rename_for_windows(artist_data["props"]["name"])
    artist_service = artist_data["props"]["service"]
    artist_id = artist_data["props"]["id"]
    artist_dir = f"download/{artist_name}-{artist_service}-{artist_id}"
    Path(f"{artist_dir}").mkdir(exist_ok=True, parents=True)
    return artist_dir, artist_name


# ファイルリスト作成
def make_file_list(input_url: str, posts_count: int, artist_dir: str) -> list[dict]:
    posts_data = []
    for i in range(0, posts_count, 50):
        posts_json = access_api(input_url, i)

        results = posts_json["results"]
        result_previews = posts_json["result_previews"]
        result_attachments = posts_json["result_attachments"]

        for index in range(len(results)):
            post_data = {
                "id": results[index]["id"],
                "title": rename_for_windows(results[index]["title"]),
                "published": results[index]["published"],
                "files": [],
            }

            for content in result_previews[index]:
                post_data["files"].append(
                    {
                        "name": rename_for_windows(content["name"]),
                        "url": f"{content['server']}/data{content['path']}",
                    }
                )
            for content in result_attachments[index]:
                post_data["files"].append(
                    {
                        "name": rename_for_windows(content["name"]),
                        "url": f"{content['server']}/data{content['path']}",
                    }
                )

            posts_data.append(post_data)

    with open(f"{artist_dir}/posts_data.json", "w", encoding="utf-8") as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)

    return posts_data


# ファイル保存
def save_file(
    posts_data: list[dict], artist_dir: str, progress_data: list[list]
) -> None:
    for i, post_data in enumerate(posts_data):
        progress_data[0][1].set(len(posts_data))
        progress_data[0][2].set(i + 1)

        dir_id = post_data["id"]
        dir_name = post_data["title"]
        dir_path = Path(f"{artist_dir}/{dir_id} - {dir_name}")
        if not (dir_path.exists()):
            Path(dir_path).mkdir(exist_ok=True, parents=True)
            time.sleep(3)

        progress_data[1][0].set(dir_name)

        for j, file_data in enumerate(post_data["files"]):
            progress_data[1][1].set(len(post_data["files"]))
            progress_data[1][2].set(j + 1)

            file_name = file_data["name"]
            file_url = file_data["url"]
            file_path = Path(f"{dir_path}/{j}-{file_name}")
            if not (file_path.exists()):
                progress_data[2][0].set(file_name)
                try:
                    with requests.get(file_url, stream=True) as r:
                        r.raise_for_status()
                        with open(file_path, "wb") as f:
                            progress_data[2][2].set(0)
                            for chunk in r.iter_content(chunk_size=1024 * 1024):
                                f.write(chunk)

                                data_size = int(r.headers.get("content-length", -1))
                                progress_data[2][1].set(data_size)
                                chunk_sum = progress_data[2][2].get()
                                if chunk_sum + 1024 * 1024 > data_size:
                                    chunk_sum = data_size
                                else:
                                    chunk_sum += 1024 * 1024
                                progress_data[2][2].set(chunk_sum)

                    time.sleep(2)
                except requests.exceptions.RequestException as e:
                    progress_data[3] = f"ファイルアクセスエラーあり"
                    error_info = f"{dir_name}:{file_name}:{e}\n"
                    with open(
                        f"{artist_dir}/error_report.txt", "a", encoding="utf-8"
                    ) as f:
                        f.write(error_info)
                    return
