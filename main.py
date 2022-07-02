import requests
from tqdm import tqdm
import json
import re
import os


class MonsterSiren:

    def __init__(self):
        self.headers = {
            'Referer': 'https://monster-siren.hypergryph.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29 '
        }

    def __get_album_list(self):
        response = requests.get(
            url='https://monster-siren.hypergryph.com/api/albums',
            headers=self.headers
        )
        albumData_list = json.loads(response.text)['data']
        # print(f'共找到{len(albumData_list)}个专辑')
        for albumData in albumData_list:
            yield albumData

    def __get_song_data(self, cid):
        response = requests.get(
            url=f'https://monster-siren.hypergryph.com/api/song/{cid}',
            headers=self.headers
        )
        song_data = json.loads(response.text)['data']
        return song_data

    def __get_album_info(self):
        for albumInfo in self.__get_album_list():
            response = requests.get(
                url=f'https://monster-siren.hypergryph.com/api/album/{albumInfo["cid"]}/detail',
                headers=self.headers
            )
            albumData = json.loads(response.text)['data']
            song_list = []
            for song_info in albumData['songs']:
                song_data = self.__get_song_data(song_info['cid'])
                song_temp = {
                    'artists': song_data['artists'],
                    'lyricUrl': song_data['lyricUrl'],
                    'sourceUrl': song_data['sourceUrl'],
                    'name': song_data['name']
                }
                song_list.append(song_temp)
            data = {
                'artistes': albumInfo['artistes'],
                'belong': albumData['belong'],
                'coverUrl': albumData['coverUrl'],
                'coverDeUrl': albumData['coverDeUrl'],
                'intro': albumData['intro'],
                'name': albumData['name'],
                'songs': song_list
            }
            yield data

    def save_data(self):
        path_detection = re.compile(r'[\\/:*?<>"|]')

        def is_path(path):
            if not os.path.exists(path):
                os.mkdir(path)

        def url_download(url, headers, name, path):
            if os.path.isfile(f'{path}/{name}'):
                # print(f'{name}已存在')
                return
            else:
                # print(f'正在下载{name}')
                pass
            response = requests.get(
                url=url,
                headers=headers
            )
            with open(f'{path}/{name}', 'wb') as file:
                file.write(response.content)

        first_path = './monster-siren'
        is_path(first_path)
        for data in self.__get_album_info():
            second_path = first_path + '/' + \
                path_detection.sub('!', data['name'])
            is_path(second_path)
            if not os.path.isfile(second_path + '/' + 'info.txt'):
                with open(second_path + '/' + 'info.txt', 'w', encoding='utf-8') as f:
                    f.write(f'专辑名称：{data["name"]}\n')
                    f.write(f'专辑属于：{data["belong"]}\n')
                    f.write(f'专辑作者：{"、".join(data["artistes"])}\n')
                    # f-string表达式不能出现反斜杠，用format方法替换
                    f.write('专辑介绍：{}\n'.format(
                        data["intro"].replace("\n", "\n                ")))
                    f.write('歌曲列表：\n')
                    for song in data['songs']:
                        f.write(
                            f'{song["name"]}   作者：{"、".join(song["artists"])}\n')
            for song in tqdm(data['songs'], desc=f'{data["name"]}'):
                third_path = second_path + '/' + \
                    path_detection.sub('!', song['name'])
                is_path(third_path)
                if song['lyricUrl'] is not None:
                    url_download(
                        url=song['lyricUrl'],
                        headers=self.headers,
                        name=f'{path_detection.sub("!", song["name"])}.{song["lyricUrl"].split(".")[-1]}',
                        path=third_path
                    )
                if song['sourceUrl'] is not None:
                    url_download(
                        url=song['sourceUrl'],
                        headers=self.headers,
                        name=f'{path_detection.sub("!", song["name"])}.{song["sourceUrl"].split(".")[-1]}',
                        path=third_path
                    )
            if data['coverUrl'] is not None:
                url_download(
                    url=data['coverUrl'],
                    headers=self.headers,
                    name=f'专辑封面.{data["coverUrl"].split(".")[-1]}',
                    path=second_path
                )
            if data['coverDeUrl'] is not None:
                url_download(
                    url=data['coverDeUrl'],
                    headers=self.headers,
                    name=f'封面.{data["coverDeUrl"].split(".")[-1]}',
                    path=second_path
                )
            pass


if __name__ == '__main__':
    MS = MonsterSiren()
    MS.save_data()
    pass
