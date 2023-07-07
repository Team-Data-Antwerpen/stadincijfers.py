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
                "provincies": 'https://provincies.incijfers.be/',
                "ima-atlas": 'https://atlas.ima-aim.be/',
                "bevolkingsonderzoek": 'https://bevolkingsonderzoek.incijfers.be/'}

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
    
    def _req_to_json(self, req):
        resp = urlopen(req, context=self.CONTEXT)
        return json.load(resp)

    def _req_to_dict(self, req):
        respjs = self._req_to_json(req)
        return {n["ExternalCode"] : n["Name"] for n in respjs["value"]} 
    
    def geolevels(self, var=None):
        if var:
            req = Request( self.url + f"jiveservices/odata/Variables('{var}')/GeoLevels")
        else:
            req = Request( self.url + f"jiveservices/odata/GeoLevels")
        return self._req_to_dict(req)
    
    def geoitemlevels(self, geolevel=None, var=None):
        if var and geolevel:
            req = Request( self.url + f"jiveservices/odata/Variables('{var}')/GeoLevels('{geolevel}')/GeoItems")
        elif geolevel:
            req = Request( self.url + f"jiveservices/odata/GeoLevels('{geolevel}')/GeoItems")
        else:
            geolevels = self.geolevels(var).keys()
            raise Exception( 'geolevel must be in ' + ", ".join( geolevels )  )               
        return self._req_to_dict(req) 
    
    def periodlevels(self, var=None, geolevel=None):
        if var and geolevel:
            req = Request( self.url + f"jiveservices/odata/Variables('{var}')/GeoLevels('{geolevel}')/PeriodLevels")
        else:
            req = Request( self.url + f"jiveservices/odata/PeriodLevels")
        return self._req_to_dict(req) 
    
    def dim_dict(self, var):
        dim_dict = {}
        req = Request( self.url + f"jiveservices/odata/CubeVariables('{var}')/Dimensions")
        dimensions = self._req_to_dict(req).keys()
        for dim in dimensions:
            try:
                req = Request( self.url + f"jiveservices/odata/CubeVariables('{var}')/DimLevels('{dim}')/DimMembers")
                dimlevels = list(self._req_to_dict(req).keys())
                dim_dict[dim] = dimlevels
            except:
                try:
                    req = Request( self.url + f"jiveservices/odata/Dimensions('{dim}')/DimLevels")
                    dimlevels = list(self._req_to_dict(req).keys())
                    dim_dict[dim] = dimlevels
                except: 
                    raise Exception('incorrect url(s)')
        return dim_dict


    def dimlevels(self, var):
        dim_dict = self.dim_dict(var)
        return [item for sublist in dim_dict.values() for item in sublist]
    
    def _odataVariables(self, skip= 0):
        req =  Request( self.url + "jiveservices/odata/Variables?$skip={}".format(skip) )
        return self._req_to_json(req)
        
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
        
    def selectiontableasjson(self, var, geolevel="sector", geoitem=None, geoitem_codes=None, geocompare=None, 
                             geocompare_item=None, geosplit=None, periodlevel="year", period="mrp", validate=True, 
                             dimlevel=None):
        
        if validate:
            geolevels = self.geolevels(var).keys()
            periodlevels = self.periodlevels(var, geolevel).keys()
            if not geolevel in geolevels:
                raise Exception( 'geolevel must be in ' + ", ".join( geolevels )  )       
            if not periodlevel in periodlevels:
                raise Exception( 'periodlevel must be in ' + ", ".join( periodlevels )  )
            if dimlevel:
              dimlevels = self.dimlevels(var)
              for dimitem in dimlevel.split(','):
                if not dimitem.strip() in dimlevels:
                  raise Exception(f"dimlevel must be in {', '.join(dimlevels)}")
        
        params_dict = {"var": var, "geolevel": geolevel, "geoitem": geoitem, "geoitem_codes": geoitem_codes,
                       "geocompare": geocompare, "geocompare_item": geocompare_item, "geosplit": geosplit,
                       "periodlevel": periodlevel, "period": period, "dimlevel": dimlevel}
        
        params = {}
        for k, v in params_dict.items():
            if v:
                params[k] = v
          
        req =  Request( self.url + "jive/selectiontableasjson.ashx?" + urlencode(params))
        return self._req_to_json(req)

    
    def selectiontableasDataframe(self, var, **kwargs):
        st_js = self.selectiontableasjson(var, **kwargs)
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
