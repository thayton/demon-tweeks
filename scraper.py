#!/usr/bin/env python

import csv
import time
import json
import requests

from bs4 import BeautifulSoup

class DemonTweeksScraper(object):
    def __init__(self):
        self.session = requests.Session()
        self.params = {}

    def makes(self):
        self.params.pop('makeCode', None)
        self.params.pop('modelCode', None)
        self.params.pop('year', None)
        self.params.pop('variantCode', None)

        resp = self.session.get('https://www.demon-tweeks.com/rest/V1/vehicles/makes', params=self.params)
        data = resp.json()

        print json.dumps(data, indent=2)
        
        for d in data:
            self.params['makeCode'] = d['code']
            yield d['code']

    def models(self):
        self.params.pop('modelCode', None)        
        self.params.pop('year', None)
        self.params.pop('variantCode', None)
        
        resp = self.session.get('https://www.demon-tweeks.com/rest/V1/vehicles/models', params=self.params)
        data = resp.json()

        for d in data:
            self.params['modelCode'] = d['code']            
            yield d['code']

    def years(self):
        self.params.pop('year', None)        
        self.params.pop('variantCode', None)
        
        resp = self.session.get('https://www.demon-tweeks.com/rest/V1/vehicles/years', params=self.params)
        data = resp.json()
        
        for d in data:
            self.params['year'] = d['label']            
            yield d['label']

    def variants(self):
        self.params.pop('variantCode', None)
        
        resp = self.session.get('https://www.demon-tweeks.com/rest/V1/vehicles/variants', params=self.params)
        data = resp.json()
        
        print json.dumps(data, indent=2)
        
        return [ d['label'] for d in data ]

        # for v in data:
        #    self.params['variantCode'] = v['label']
        #    yield v['label']

    def vehicles(self):
        resp = self.session.get('https://www.demon-tweeks.com/rest/V1/vehicles/vehicle', params=self.params)
        data = resp.json()

        for v in data:
            yield v

    def csv_save(self, data):
        headers = [
            'typeCode', 'makeCode', 'modelCode', 'year', 'variants'
        ]
        filename = 'demons-tweeks.csv'
        
        with open(filename, 'w') as fp:
            writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(headers)

            for d in data:
                row = [
                    d.get(h) for h in headers
                ]
                
                writer.writerow(row) 
        
    def scrape(self):
        data = []
        
#        for typeCode in ['car', 'motorcycle']:
        for typeCode in ['motorcycle']:
            self.params['typeCode'] = typeCode
            for make in self.makes():
                print make
                time.sleep(0.5)
                for model in self.models():
                    print model
                    time.sleep(0.5)                    
                    for year in self.years():
                        print year
                        time.sleep(0.5)
                        d = self.params.copy()
                        d['variants'] = '\n'.join( self.variants() )
                        data.append(d)


                break
        
        self.csv_save(data)
        
if __name__ == '__main__':
    scraper = DemonTweeksScraper()
    scraper.scrape()
    
