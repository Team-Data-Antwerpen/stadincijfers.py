from __future__ import print_function
import sys, json, ssl
import pandas as pd

if sys.version_info.major == 2:
    from urllib2 import Request, urlopen
    from urllib import urlencode
if sys.version_info.major >= 3:
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen

class stadincijfers:
    BASE_URLS ={"antwerpen": 'https://stadincijfers.antwerpen.be/databank/',
                "gent": 'https://gent.buurtmonitor.be/',
                "provincies": 'https://provincies.incijfers.be/'}
    CONTEXT = ssl._create_unverified_context() 

    def __init__(self, name_or_url):
        if name_or_url in self.BASE_URLS.keys():
            self.url = self.BASE_URLS[name_or_url]
        elif name_or_url.startswith("http://") or name_or_url.startswith("https://"):
            self.url = name_or_url
        else: 
            raise Exception("name_or_url is not a valid name or url")
         
        if not self.url.endswith("/"): 
            self.url = self.url + '/'
    
    def geolevels(self):
        req = Request( self.url + "jiveservices/odata/GeoLevels")
        resp = urlopen(req, context=self.CONTEXT)
        respjs =  json.load(resp) 
        return {n["ExternalCode"] : n["Name"] for n in respjs["value"]}
        
    def periodlevels(self):
        req = Request( self.url + "jiveservices/odata/PeriodLevels")
        resp = urlopen(req, context=self.CONTEXT)
        respjs =  json.load(resp) 
        return {n["ExternalCode"] : n["Name"] for n in respjs["value"]} 
        
    def _odataVariables(self, skip= 0):
        req =  Request( self.url + "jiveservices/odata/Variables?$skip={}".format(skip) )
        resp = urlopen(req, context=self.CONTEXT)
        return json.load(resp) 
        
    def odataVariables(self, skip_rows= 0 , to_rows=1000):   
        if skip_rows >= to_rows:
            raise Exception("skip_rows must be smaller then to_rows")
        
        data = []
        step = 10
        count = skip_rows
        print( "reading data, lines {} to {} this can take a while".format(skip_rows,to_rows) )
        while count <= to_rows:
            resp = self._odataVariables( count )
            if len( resp["value"] ) > 0:
                data += resp["value"]
            else:
                break
            print(count , end=" ")
            count += step
        return {n["ExternalCode"] : n["Name"] for n in data} 
        
    def selectiontableasjson(self, var, geolevel="sector", periodlevel="year", period='2020', validate=True ):
        if validate:
            geolevels = self.geolevels().keys()
            periodlevels = self.periodlevels().keys()
            if not geolevel in geolevels:
                raise Exception( 'geolevel most be in ' + ", ".join( geolevels )  )       
            if not periodlevel in periodlevels:
                raise Exception( 'periodlevel most be in ' + ", ".join( periodlevels )  )
            
        params = {"var": var, "geolevel": geolevel, "Periodlevel": periodlevel, 'period': period }
        req =  Request( self.url + "jive/selectiontableasjson.ashx?" + urlencode(params))
        resp = urlopen(req, context=self.CONTEXT)
        return json.load(resp)

    
    def selectiontableasDataframe(self, var, geolevel="sector", periodlevel="year", period='2020', validate=True ):
        st_js = self.selectiontableasjson(var, geolevel, periodlevel, period, validate)
        header = [ n['name'] for n in st_js['headers'] ]
        dtype = st_js['headers'][2]['type']
        data = st_js['rows']
        
        df = pd.DataFrame(data, columns=header)
        if dtype == 'Numeric':
            df[ header[2] ] = df[header[2]].apply( self._str2flt )
    
        return df

    def _str2flt(self, element):
        try:
            return float(element)
        except ValueError:
            return None
