import sys
import json
import yaml
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from hashlib import md5
from random import randint


def generate_arabic_text():
    with open('./data/alf-layla-wa-akhbar.txt', 'r') as f:
        for sentence in f.read().split('.'):
            doc = dict(
                message=sentence,
                author=md5(sentence.encode()).hexdigest()[:5],
                position=generate_nyc_position(),
                driver_id=randint(0, 500),
                passenger_id=randint(0, 500)
            )
            doc['@timestamp'] = datetime.utcnow().isoformat()
            yield doc


def set_env(name, value):
    with open('~temp.env.json', 'r') as f:
        try:
            env = json.load(f)
        except json.decoder.JSONDecodeError:
            env = {}
    env[name] = value
    with open('~temp.env.json', 'w') as f:
        json.dump(env, f)


def filebeat_config(cloud_id, cloud_auth):

    def represent_none(self, _):
        return self.represent_scalar('tag:yaml.org,2002:null', '')

    yaml.add_representer(type(None), represent_none)

    with open('./src/beats-assets/filebeat.yml', 'r') as f:
        fb = yaml.load(f, Loader=yaml.FullLoader)
    fb['cloud.id'] = cloud_id
    fb['cloud.auth'] = cloud_auth
    with open('./src/beats-assets/filebeat.yml', 'w') as f:
        yaml.dump(fb, f)


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()
    if count == total:
        print('\n')


def generate_nyc_position():
    """NYC  coordinates
    40.806732, -73.991281
    40.603767, -73.745071
    """
    lat, lon = randint(40603767, 40806732), randint(-73991281, -73745071)
    scaled_lat, scaled_lon = float(lat)/1e6, float(lon)/1e6
    return dict(lat=scaled_lat, lon=scaled_lon)


def create_index_patterns():
    with open('~temp.env.json', 'r') as f:
        conf = json.load(f)
