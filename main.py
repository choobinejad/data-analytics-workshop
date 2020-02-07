import json
from elasticsearch import Elasticsearch
import elasticsearch
import requests
import fire
from termcolor import colored
from src.helpers import *

import sys
class Configure(object):
    """Utilities for indexing data for the workshop."""

    def cloud(self, cloud_id, cloud_user, cloud_password, es_endpoint, kibana_endpoint):
        """Configure Elastic Cloud environment variables for use with Beats and other workshop components. This is
        not a secure configuration for production use; it is intended to be transparent and easy to follow for the
        purposes of the workshop."""
        set_env('CLOUD_ID', cloud_id)
        set_env('CLOUD_PASSWORD', cloud_password)
        set_env('CLOUD_USER', cloud_user)
        set_env('CLOUD_AUTH', '{}:{}'.format(cloud_user, cloud_password))
        set_env('ES_ENDPOINT', es_endpoint)
        set_env('KIBANA_ENDPOINT', kibana_endpoint)
        filebeat_config(cloud_id, '{}:{}'.format(cloud_user, cloud_password))

    @staticmethod
    def ingest(nuke=False):
        """Create ingest pipelines for the main taxi data sources.
        """
        with open('~temp.env.json', 'r') as f:
            conf = json.load(f)
        es = Elasticsearch(conf['ES_ENDPOINT'], http_auth=(conf['CLOUD_USER'], conf['CLOUD_PASSWORD']))
        with open('./src/es-assets/taxi-ingest.pipeline.json', 'r') as f:
            es.ingest.put_pipeline('taxi-ingest', body=json.load(f))
        print(colored('Created ingest pipeline: taxi-ingest', 'green'))

    @staticmethod
    def templates(nuke=False):
        """Create index templates for the main taxi data sources.
        """
        tmps = ['taxi-trips', 'taxi-trips-yellow', 'taxi-trips-green', 'taxi-trips-fhv', 'taxi-trips-fhvhv',
                'transform-summary-driver']
        with open('~temp.env.json', 'r') as f:
            conf = json.load(f)
        es = Elasticsearch(conf['ES_ENDPOINT'], http_auth=(conf['CLOUD_USER'], conf['CLOUD_PASSWORD']))
        if nuke:
            for i in tmps:
                try:
                    es.indices.delete_template(i)
                    print(colored('Deleted template: {}'.format(i), 'red'))
                except elasticsearch.exceptions.NotFoundError:
                    print(colored('Template: {} does not exist; proceeding'.format(i), 'red'))
        for i in tmps:
            if not es.indices.exists_template(i):
                with open('./src/es-assets/{}.template.json'.format(i), 'r') as f:
                    es.indices.put_template(i, body=json.load(f))
                    print(colored('Created template: {}'.format(i), 'green'))
            else:
                print(colored('Template already exists: {}; proceeding'.format(i), 'green'))


class Data(object):
    """Utilities for indexing data for the workshop."""

    @staticmethod
    def generate_text(nuke=False):
        """Generate text to demonstrate language analyzer configuration and full text search.
        """
        with open('~temp.env.json', 'r') as f:
            conf = json.load(f)
        es = Elasticsearch(conf['ES_ENDPOINT'], http_auth=(conf['CLOUD_USER'], conf['CLOUD_PASSWORD']))
        if nuke:
            try:
                es.indices.delete('arabic_messages')
                print(colored('Deleted index: arabic_messages', 'red'))
            except elasticsearch.exceptions.NotFoundError:
                pass
        if not es.indices.exists('arabic_messages'):
            with open('./src/es-assets/arabic_messages.mapping.json', 'r') as f:
                es.indices.create('arabic_messages', body=json.load(f))
                print(colored('Created index: arabic_messages', 'green'))
        else:
            print(colored('Index already exists: arabic_messages; proceeding', 'green'))
        counter = 0
        for d in generate_arabic_text():
            [es.index('arabic_messages', d) for i in range(3)]
            counter += 3
            pb = progress(count=counter, total=855, status='({} of 855 docs)'.format(counter))
        print(colored('Done\n', 'green'))


class Labs(object):
    """Helpers for the lab exercises."""

    def generate_text(self):
        """Generate text to demonstrate language analyzer configuration and full text search."""
        for d in generate_arabic_text():
            print(d)


class Workshop(object):
    """A CLI to control the data analytics workshop."""

    def __init__(self):
        self.data = Data()
        self.labs = Labs()
        self.configure = Configure()


def main():
    fire.Fire(Workshop(), name='workshop')


if __name__ == '__main__':
    main()
