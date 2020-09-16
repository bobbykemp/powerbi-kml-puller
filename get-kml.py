import requests
import xml.etree.ElementTree as et

parms = {}

parms['request_type']     = 'generateKml'
parms['outageType']       = '129001450'
parms['outageResolution'] = '1.0'
parms['lookAheadMins']    = '360'
parms['minLat']           = '-90'
parms['maxLat']           = '90'
parms['minLon']           = '-180'
parms['maxLon']           = '180'

url = 'https://sapt.faa.gov/SAPTWS/KmlServlet'

try:
    r = requests.get(url, params=parms)
    r.raise_for_status()
    kmlid = r.json()['kmlid']

    print(kmlid)

    url = 'https://sapt.faa.gov/SAPTWS/KmlServlet?request_type=getKml&kmlid=' + str(kmlid)

    r = requests.get(url, allow_redirects=True)
    kml = r.text

    xtree = et.fromstring(kml)
    

except HTTPError:
    print("The response did not complete successfully")
    exit