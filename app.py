import vk_api
import os
import requests
import attr
from datetime import datetime

_WORKING_DIR = 'xxx'
_LOGIN = 'xxx'
_PASSWORD = 'xxx'
_APP_ID = 'xxx'
_LUNOHOD_ID = 'xxx'
_PHOTOS_OWNER = _LUNOHOD_ID


g_total = 0


def download_file(url: str, outdir : str) -> None:
    resp = requests.get(url, stream=True)
    if resp.ok:
        name = os.path.basename(url)
        out = os.path.join(outdir, name)
        if not os.path.isfile(out):
            with open(out, 'wb') as f:
                f.write(resp.content)
                print('[+] Downloaded', url)
    else:
        print('[-] Unable to download', url, resp)


@attr.s(frozen=True)
class Album(object):
    id = attr.ib(type=str)
    title = attr.ib(type=str)
    size = attr.ib(type=int)
    created = attr.ib(type=str)

    @classmethod
    def create_from_vk_resp(cls, resp_item):
        return cls(id=resp_item['id'],
                   title=resp_item['title'],
                   size=resp_item['size'],
                   created=str(datetime.fromtimestamp(resp_item['created'])))

    def download(self, vk, owner):
        wd = os.path.join(_WORKING_DIR, self.title + ' ' + self.created)
        os.makedirs(wd, exist_ok=True)

        photos = vk.photos.get(album_id=self.id, owner_id=owner, photo_sizes=1, count=999)
        download_photos(photos, wd)


def download_photos(resp, folder):
    for item in resp['items']:
        total_sizes = len(item['sizes'])
        if total_sizes > 0:
            global g_total
            g_total += 1
            download_file(item['sizes'][total_sizes - 1]['url'], folder)


def get_albums(vk, owner):
    albums_resp = vk.photos.getAlbums(owner_id=owner)
    return [Album.create_from_vk_resp(item) for item in albums_resp['items']]


def main() -> None:
    vk_session = vk_api.VkApi(_LOGIN, _PASSWORD, app_id=_APP_ID, scope='photos')

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    api = vk_session.get_api()

    albums = get_albums(api, _PHOTOS_OWNER)
    i = 1
    for a in albums:
        print('Downloading', a.title, '{}/{}'.format(i, len(albums)))
        a.download(api, _PHOTOS_OWNER)
        i += 1

    print(g_total)


if __name__ == '__main__':
    main()
