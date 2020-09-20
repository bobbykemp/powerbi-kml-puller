import io
import re
import time
import xml.etree.ElementTree as et
import pytz

import pandas as pd
import requests
from dateutil import parser


def get_kml_data(kml_root):
  # index into the kml document structure
  for document in kml_root.findall('{http://www.opengis.net/kml/2.2}Document'):
    for placemark in document.findall('{http://www.opengis.net/kml/2.2}Placemark'):
      for coordinates in placemark.iter('{http://www.opengis.net/kml/2.2}coordinates'):
        doc_dict = {}
        doc_dict['coordinates'] = coordinates.text
      for description in placemark.iter('{http://www.opengis.net/kml/2.2}description'):
        outage_pattern =  re.compile(r'Outage from (?P<start_date>\d{4}-\d{2}-\d{2}) at (?P<start_time>\d\d\:\d\d\:\d\d) to (?P<end_date>\d{4}-\d{2}-\d{2}) at (?P<end_time>\d{2}\:\d{2}\:\d{2}) (?P<timezone>\w+)')
        testing_pattern = re.compile(r'Effective on (?P<start_date>\d{4}-\d{2}-\d{2}) from (?P<start_time>\d{2}\:\d{2}\:\d{2}\.\d) until (?P<end_time>\d{2}\:\d{2}\:\d{2}\.\d) (?P<timezone>\w+)')
        outage_text = description.text
        test_text = description.text
        if testing_pattern.search(test_text) is not None:
          testing_match = testing_pattern.search(test_text)
          st = parser.parse(testing_match.group('start_date') + ' ' + testing_match.group('start_time') + ' ' + testing_match.group('timezone'))
          dt = parser.parse(testing_match.group('start_date') + ' ' + testing_match.group('end_time') + ' ' + testing_match.group('timezone'))
          doc_dict['start_time'] = str(st)
          doc_dict['end_time'] = str(dt)
          yield doc_dict
        if outage_pattern.search(outage_text) is not None:
          outage_match = outage_pattern.search(outage_text)
          st = parser.parse(outage_match.group('start_date') + ' ' + outage_match.group('start_time') + ' ' + outage_match.group('timezone'))
          dt = parser.parse(outage_match.group('end_date') + ' ' + outage_match.group('end_time') + ' ' + outage_match.group('timezone'))
          doc_dict['start_time'] = str(st)
          doc_dict['end_time'] = str(dt)
          yield doc_dict
        doc_dict['description'] = description.text
        yield doc_dict
    for folder in document.findall('{http://www.opengis.net/kml/2.2}Folder'):
      for placemark in folder.findall('{http://www.opengis.net/kml/2.2}Placemark'):
        for coordinates in placemark.iter('{http://www.opengis.net/kml/2.2}coordinates'):
          doc_dict = {}
          doc_dict['coordinates'] = coordinates.text
        for description in placemark.iter('{http://www.opengis.net/kml/2.2}description'):
          outage_pattern =  re.compile(r'Outage from (?P<start_date>\d{4}-\d{2}-\d{2}) at (?P<start_time>\d\d\:\d\d\:\d\d) to (?P<end_date>\d{4}-\d{2}-\d{2}) at (?P<end_time>\d{2}\:\d{2}\:\d{2}) (?P<timezone>\w+)')
          testing_pattern = re.compile(r'Effective on (?P<start_date>\d{4}-\d{2}-\d{2}) from (?P<start_time>\d{2}\:\d{2}\:\d{2}\.\d) until (?P<end_time>\d{2}\:\d{2}\:\d{2}\.\d) (?P<timezone>\w+)')
          outage_text = description.text
          test_text = description.text
          if testing_pattern.search(test_text) is not None:
            testing_match = testing_pattern.search(test_text)
            st = parser.parse(testing_match.group('start_date') + ' ' + testing_match.group('start_time') + ' ' + testing_match.group('timezone'))
            dt = parser.parse(testing_match.group('start_date') + ' ' + testing_match.group('end_time') + ' ' + testing_match.group('timezone'))
            doc_dict['start_time'] = str(st)
            doc_dict['end_time'] = str(dt)
            yield doc_dict
          if outage_pattern.search(outage_text) is not None:
            outage_match = outage_pattern.search(outage_text)
            st = parser.parse(outage_match.group('start_date') + ' ' + outage_match.group('start_time') + ' ' + outage_match.group('timezone'))
            dt = parser.parse(outage_match.group('end_date') + ' ' + outage_match.group('end_time') + ' ' + outage_match.group('timezone'))
            doc_dict['start_time'] = str(st)
            doc_dict['end_time'] = str(dt)
            yield doc_dict
          doc_dict['description'] = description.text
          yield doc_dict

headers = {
  'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Encoding' : 'gzip, deflate, br',
  'Accept-Language' : 'en-US,en;q=0.5',
  'Connection' : 'keep-alive',
  'Host' : 'sapt.faa.gov',
  'Upgrade-Insecure-Requests' : '1',
  'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'
}
url = 'https://sapt.faa.gov/outages.php?outageType=129001450'

session = requests.Session()
try:
  r = session.get(url, headers=headers)
  r.raise_for_status()

except requests.HTTPError:
  print(f'Failed to retrieve initial url: {url}...')
  doc_df = pd.DataFrame(['The request did not complete successfully'], columns=['coordinates'])
  print(doc_df)
  exit()

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
print(f'Requesting server generation of kml file at url: {url}...')

try:
  r = session.get(url, params=parms)
  r.raise_for_status()

except requests.HTTPError:
  print(f'Failed at requesting kml generation at url: {url}...')
  doc_df = pd.DataFrame(['The request did not complete successfully'], columns=['coordinates'])
  exit()

kmlid = r.json()['kmlid']
print(f'Kml file generated on server: id is {kmlid}')

headers = {
  'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Encoding' : 'gzip, deflate, br',
  'Accept-Language' : 'en-US,en;q=0.5',
  'Connection' : 'keep-alive',
  'Host' : 'sapt.faa.gov',
  'Upgrade-Insecure-Requests' : '1',
  'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'
}

url = f'https://sapt.faa.gov/SAPTWS/KmlServlet?request_type=getKml&kmlid={kmlid}'

print(f'Giving the server time to generate the kml file...')
time.sleep(15) #sleep for a bit to prevent requesting the resource from the server too early and having it not exist
print(f'Downloading kml file at url: {url}...')

try:
  r = session.get(url, headers=headers)
  r.raise_for_status()

except requests.HTTPError:
  print(f'Failed to download kml file at: {url}...')
  doc_df = pd.DataFrame(['The request did not complete successfully'], columns=['coordinates'])
  print(doc_df)
  exit()

# kml_file_name = f'outages-{kmlid}-129001450.kml'
# f = open(kml_file_name, "w")
# print(f"Writing retrieved file \"{kml_file_name}\" to disk...")
# f.write(r.text)
# f.close

xml_data = io.StringIO(r.text)
etree = et.parse(xml_data)
# etree = et.parse("outages-1238-129001450.kml")
doc_df = pd.DataFrame(list(get_kml_data(etree.getroot())))

print(doc_df)
