import xml.etree.ElementTree as ET
import urllib.request
import optparse

API = 'https://pub.orcid.org/v3.0'

p = optparse.OptionParser()
p.add_option('--output', '-o')
options, arguments = p.parse_args()

textFile = options.output
if(textFile):
  f = open(textFile, "w", encoding="utf-8")

def printAndSave(tag, value):
  print(tag + ": " + value)
  if(textFile):
    f.write(tag + ": " + value + "\n")

id = arguments[0] if len(arguments) > 0 else '0000-0001-5173-8230'
print(API + '/' + id)
try:
  request = urllib.request.urlopen(API + '/' + id)
  xml = request.read()
  myTree = ET.fromstring(xml)

  person = myTree.find('{http://www.orcid.org/ns/person}person').find('{http://www.orcid.org/ns/person}name')
  printAndSave('First name', person.find('{http://www.orcid.org/ns/personal-details}given-names').text)
  printAndSave('Last name', person.find('{http://www.orcid.org/ns/personal-details}family-name').text)
  printAndSave('Publications:','')

  for child in myTree[4][11].findall('{http://www.orcid.org/ns/activities}group'):
      printAndSave('---------------------------------------','')
      printAndSave('Title',child[2][3][0].text)
      path = child.find('{http://www.orcid.org/ns/work}work-summary').attrib.get('path')

      print(API + path)
      try:
        workInfoResponce = urllib.request.urlopen(API + path)
        if(workInfoResponce):
          xml = workInfoResponce.read()
          workTree = ET.fromstring(xml)
          printAndSave('Contributors', ", ".join(c.text for c in workTree.findall('{http://www.orcid.org/ns/work}contributor')))
          printAndSave('Publication Date', workTree.find('{http://www.orcid.org/ns/common}created-date').text)
          printAndSave('Journal:', '')
          printAndSave('- Name', workTree.find('{http://www.orcid.org/ns/work}journal-title').text)

          citation = workTree.find('{http://www.orcid.org/ns/work}citation')
          if(citation):
            printAndSave('- Metadata', citation[1].text)
          
          externalIds = workTree.find('{http://www.orcid.org/ns/common}external-ids')
          for id in externalIds.findall('{http://www.orcid.org/ns/common}external-id'):
            printAndSave(id.find('{http://www.orcid.org/ns/common}external-id-type').text, id.find('{http://www.orcid.org/ns/common}external-id-value').text)

          printAndSave('PDF', workTree.find('{http://www.orcid.org/ns/common}url').text)
      except:
        print ('work network error')   

except:
    print ('network error')

if(textFile):
  f.close()