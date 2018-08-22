#!/usr/bin/env python

import json
import requests

from bs4 import BeautifulSoup

class DemonTweeksScraper(object):
    def __init__(self):
        self.session = requests.Session()
        self.params = {}

    def makes(self):
        self.params = {}        
        self.params['typeCode'] = 'car'

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

        for v in data:
            self.params['variantCode'] = v['label']
            yield v['label']

    def vehicles(self):
        resp = self.session.get('https://www.demon-tweeks.com/rest/V1/vehicles/vehicle', params=self.params)
        data = resp.json()

        for v in data:
            yield v
            
    def scrape(self):
        for make in self.makes():
            print make
            for model in self.models():
                print model
                for year in self.years():
                    print year
                    for variant in self.variants():
                        print variant
                        for vehicle in self.vehicles():
                            print json.dumps(vehicle, indent=2)

if __name__ == '__main__':
    scraper = DemonTweeksScraper()
    scraper.scrape()
    
