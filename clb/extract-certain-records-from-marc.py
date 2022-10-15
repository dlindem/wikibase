# import lxml
from xml.etree import ElementTree as ET

import re
import os
import csv
import sys
import json
import time

marcxml_file = '/home/d3d/Downloads/aut.xml'
extractxml_file = marcxml_file.replace('.xml','_extract_150_151_155.xml')
with open(extractxml_file, 'w') as outfile:
    outfile.write('<collection>\n')
xmlns = "{http://www.loc.gov/MARC21/slim}"
count = 0
for event, element in ET.iterparse(marcxml_file, events=["start"]):
    if element.tag == xmlns+"record":
        recordstring = ET.tostring(element).decode('utf-8').replace('xmlns:ns0="http://www.loc.gov/MARC21/slim" ','').replace('ns0:','').replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"','')
        #print(recordstring)
        count+=1

        # if 'tag="148"' in recordstring or 'tag="150"' in recordstring or 'tag="151"' in recordstring or 'tag="155"' in recordstring:
        if 'tag="150"' in recordstring or 'tag="151"' in recordstring or 'tag="155"' in recordstring:
            print(str(count),'FOUND TERM CONTAINING RECORD')
            with open(extractxml_file, 'a') as outfile:
                outfile.write(recordstring)
        else:
            print(str(count))
    element.clear()


with open(extractxml_file, 'a') as outfile:
    outfile.write('</collection>\n')
