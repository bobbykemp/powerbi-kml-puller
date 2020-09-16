import requests
import xml.etree.ElementTree as et
import pandas as pd
import io
import time

def get_kml_data(kml_root):
  # index into the kml document structure
  for document in kml_root.findall('{http://www.opengis.net/kml/2.2}Document'):
    for placemark in document.findall('{http://www.opengis.net/kml/2.2}Placemark'):
      for coordinates in placemark.iter('{http://www.opengis.net/kml/2.2}coordinates'):
        doc_dict = {}
        doc_dict['coordinates'] = coordinates.text
        yield doc_dict
    for folder in document.findall('{http://www.opengis.net/kml/2.2}Folder'):
      for placemark in folder.findall('{http://www.opengis.net/kml/2.2}Placemark'):
        for coordinates in placemark.iter('{http://www.opengis.net/kml/2.2}coordinates'):
          doc_dict = {}
          doc_dict['coordinates'] = coordinates.text
          yield doc_dict

        # doc_dict['timespan_begin'] = placemark.find('{http://www.opengis.net/kml/2.2}begin').text
        # doc_dict['timespan_end']   = placemark.find('{http://www.opengis.net/kml/2.2}end').text
        # doc_dict['coordinates']    = placemark.findall('{http://www.opengis.net/kml/2.2}coordinates').text
        # yield doc_dict

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
  print(f'Requesting server generation of kml file at url: {url}...')
  r = requests.get(url, params=parms)
  r.raise_for_status()
  kmlid = r.json()['kmlid']
  print(f'Kml file generated: id is {kmlid}')

  url = f'https://sapt.faa.gov/SAPTWS/KmlServlet?request_type=getKml&kmlid={kmlid}'
  headers = {
    'host' : 'sapt.faa.gov',
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
    'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-language' : 'en-US,en;q=0.5',
    'accept-encoding' : 'gzip, deflate, br',
    'connection' : 'keep-alive',
    'referer' : 'https://sapt.faa.gov/outages.php?outageType=129001450&outageResolution=1.0',
    'upgrade-insecure-requests' : '1'
  }


  print(f'Requesting download of kml file at url: {url}...')
  time.sleep(15) #sleep for a bit to prevent requesting the resource from the server too early and having it not exist
  r = requests.get(url, headers=headers)
  r.raise_for_status()

  kml_file_name = f'outages-{kmlid}-129001450.kml'
  f = open(kml_file_name, "w")
  print(f"Writing retrieved file \"{kml_file_name}\" to disk...")
  f.write(r.text)
  f.close

  xml_data = io.StringIO(r.text)
  etree = et.parse(xml_data)
  # etree = et.parse("outages-1238-129001450.kml")
  doc_df = pd.DataFrame(list(get_kml_data(etree.getroot())))

  print(doc_df)
    
except requests.HTTPError:
  print(f'Failed to retrieve file at: {url}...')
  doc_df = pd.DataFrame(['The request did not complete successfully'], columns=['Error message'])