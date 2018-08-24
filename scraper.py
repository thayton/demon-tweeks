#!/usr/bin/env python

import csv
import time
import json
import requests

from bs4 import BeautifulSoup
from redis import StrictRedis
from redis.exceptions import RedisError
from rediscache import RedisCache

class DemonTweeksScraper(object):
    def __init__(self):
        self.session = requests.Session()
        self.params = {}
        self.init_cache()

    def init_cache(self):
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': 'foobared'
        }

        client = StrictRedis(**redis_config)
        try:
            client.ping()
        except RedisError as ex:
            self.logger.error('Error connecting to Redis: %s' % ex)
            exit('Failed to connect to Redis, exiting...' )

        self.cache = RedisCache(client=client)

    def get(self, url, params):
        url = requests.Request('GET', url, params=self.params).prepare().url

        try:
            text = self.cache[url]
        except KeyError:
            pass
        else:
            print 'Cached ', url
            data = json.loads(text)
            return data

        time.sleep(0.5)
        
        resp = self.session.get(url, params=params)
        data = resp.json()

        self.cache[url] = resp.text
        return data
    
    def makes(self):
        self.params.pop('makeCode', None)
        self.params.pop('modelCode', None)
        self.params.pop('year', None)
        self.params.pop('variantCode', None)

        data = self.get('https://www.demon-tweeks.com/rest/V1/vehicles/makes', self.params)
        
        print json.dumps(data, indent=2)
        
        for d in data:
            self.params['makeCode'] = d['code']
            yield d['code']

    def models(self):
        self.params.pop('modelCode', None)        
        self.params.pop('year', None)
        self.params.pop('variantCode', None)

        data = self.get('https://www.demon-tweeks.com/rest/V1/vehicles/models', self.params)        

        for d in data:
            self.params['modelCode'] = d['code']            
            yield d['code']

    def years(self):
        self.params.pop('year', None)        
        self.params.pop('variantCode', None)

        data = self.get('https://www.demon-tweeks.com/rest/V1/vehicles/years', self.params) 
        
        for d in data:
            self.params['year'] = d['label']            
            yield d['label']

    def variants(self):
        self.params.pop('variantCode', None)
        
        data = self.get('https://www.demon-tweeks.com/rest/V1/vehicles/variants', self.params) 
        
        print json.dumps(data, indent=2)
        
        return [ d['label'] for d in data ]

        # for v in data:
        #    self.params['variantCode'] = v['label']
        #    yield v['label']

    def vehicles(self):
        data = self.get('https://www.demon-tweeks.com/rest/V1/vehicles/vehicle', self.params)
        
        for v in data:
            yield v

    def csv_save(self, data):
        headers = [
            'typeCode', 'makeCode', 'modelCode', 'year', 'variants'
        ]
        filename = 'demons-tweeks-car.csv'
        
        with open(filename, 'w') as fp:
            writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(headers)

            for d in data:
                row = [
                    d.get(h).encode('utf8') for h in headers
                ]
                
                writer.writerow(row) 
        
    def scrape(self):
        data = []
        
#        for typeCode in ['car', 'motorcycle']:
        for typeCode in ['car']:
            self.params['typeCode'] = typeCode
            for make in self.makes():
                print make
                for model in self.models():
                    print model
                    for year in self.years():
                        print year
                        d = self.params.copy()
                        d['variants'] = '\n'.join( self.variants() )
                        data.append(d)

        self.csv_save(data)
        
if __name__ == '__main__':
    scraper = DemonTweeksScraper()
    scraper.scrape()
    
