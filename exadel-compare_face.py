import csv
import base64
import csv
import re
import sys
from random import randint
from time import sleep

from compreface import CompreFace
from compreface.service import DetectionService

from ivix.common import get_db_connection, pad_base64

DOMAIN: str = 'http://localhost'
PORT: str = '8000'
DETECTION_API_KEY: str = '3f9d251f-e3ff-4b3f-ac47-c04667ccd3d3'


def retry(to=(0, 0), until: int = sys.maxsize):
    def _func(func):
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            res = None
            retries = 0
            while res is None and retries < until:
                sleep(randint(to[0], to[1]))
                try:
                    res = func(*args, **kwargs)
                    return res
                except:
                    retries += 1
                    print(f'retrying... #{retries}')
                    pass
        return wrapper
    return _func


@retry(to=(1, 2))
def retriable_detect_face(image_path: str) -> dict:
    return detection.detect(image_path)


def list_coll_res(db_name: str, coll_name: str, query: dict = {}, project: dict = {}) -> list[dict]:
    with get_db_connection() as conn_rw:
        coll = conn_rw[db_name][coll_name]
    return list(coll.find(query, project))


def facebook() -> list[dict]:
    res = []
    wss = list_coll_res('test-ita_bm_opensea', 'facebook', {'logo': {'$exists': 1}},
                        {"logo": 1, "facebook_url": 1, '_id': 0})
    for ws in wss:
        if 'logo' in ws:
            d_ws = retriable_detect_face(ws['logo'])
            print(ws, d_ws)
            if 'result' in d_ws and len(d_ws['result']):
                res.append(dict(id=ws.get('facebook_url', ''),
                                image=ws.get('logo', '')))
    return res


def instagram() -> list[dict]:
    res = []
    wss = list_coll_res('test-ita_bm_opensea', 'instagram', {}, {'profile_pic_url': 1, 'instagram_url': 1})
    for ws in wss:
        if 'profile_pic_url' in ws:
            sleep(randint(1, 2))
            d_ws = detection.detect(ws['profile_pic_url'])
            print(d_ws)
            if 'result' in d_ws and len(d_ws['result']):
                res.append(dict(id=ws.get('instagram_url', ''),
                                image=ws.get('profile_pic_url', '')))
    return res


def twitter() -> list[dict]:
    res = []
    wss = list_coll_res('test-ita_bm_opensea', 'twitter', {},
                        {'profile_image_url_https': 1, 'profile_banner_url': 1, 'twitter_url': 1})
    for ws in wss:
        d_ws = {}
        if 'profile_image_url_https' in ws:
            sleep(randint(1, 2))
            d_ws = detection.detect(ws['profile_image_url_https'])
        if 'result' not in d_ws and 'profile_banner_url' in ws:
            sleep(randint(1, 2))
            d_ws = detection.detect(ws['profile_banner_url'])
        print(d_ws)
        if 'result' in d_ws and len(d_ws['result']):
            res.append(dict(id=ws.get('twitter_url', ''),
                            image=ws.get('profile_image_url_https', ws.get('profile_banner_url', ''))))
    return res


def website() -> list[dict]:
    res = []
    wss = list_coll_res('test-ita_bm_opensea', 'websites', {"$or": [{"website_url": re.compile(r'.*linktr\.ee.*')},
                                                                       {"website_url": re.compile(r'.*\/t\.me\/.*')}]},
                        {"profile_pic_url": 1, "website_url": 1, '_id': 0})
    for ws in wss:
        if 'profile_pic_url' in ws:
            if 'base64' not in ws['profile_pic_url']:
                d_ws = detection.detect(ws['profile_pic_url'])
            else:
                base64_data_url_pattern = r'^data:image.*base64,'
                d_ws = base64.decodebytes(bytes(pad_base64(re.sub(base64_data_url_pattern, '', ws['profile_pic_url'])),
                                                encoding='ascii'))
            print(d_ws)
            if 'result' in d_ws and len(d_ws['result']):
                res.append(dict(id=ws.get('website_url', ''),
                                image=ws.get('profile_pic_url', '')))
    return res


if __name__ == '__main__':
    compre_face: CompreFace = CompreFace(DOMAIN, PORT)
    detection: DetectionService = compre_face.init_face_detection(DETECTION_API_KEY)

    platform = sys.argv[1]

    identities = {
        'facebook': facebook,
        'instagram': instagram,
        'twitter': twitter,
        'website': website,
    }[platform]()

    if identities:
        keys = identities[0].keys()

        with open(f'{platform}_identities_with_faces.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(identities)
