
import xml.etree.ElementTree as ET
my_xml="""

<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="urn:nornik.ru:sbox:po:sentukov" targetNamespace="urn:nornik.ru:sbox:po:sentukov">
   <xsd:complexType name="ListUrls">
      <xsd:sequence>
         <xsd:element name="response">
            <xsd:complexType>
               <xsd:sequence>
                  <xsd:element name="total_files" minOccurs="0">
                     <xsd:annotation>
                        <xsd:documentation>
                        dsf
                        </xsd:documentation>
                     </xsd:annotation>
                     <xsd:simpleType>
                        <xsd:restriction base="xsd:string">
                           <xsd:maxLength value="30" />
                        </xsd:restriction>
                     </xsd:simpleType>
                  </xsd:element>
                  <xsd:element name="max_banch" type="xsd:string" minOccurs="0" />
                  <xsd:element name="file_banch">
                     <xsd:complexType>
                        <xsd:sequence>
                           <xsd:element name="people" type="xsd:string" maxOccurs="unbounded" />
                           <xsd:element name="company" type="xsd:string" minOccurs="0" maxOccurs="unbounded" />
                        </xsd:sequence>
                     </xsd:complexType>
                  </xsd:element>
               </xsd:sequence>
            </xsd:complexType>
         </xsd:element>
      </xsd:sequence>
   </xsd:complexType>
</xsd:schema>
"""

s = ET.fromstring(my_xml)
for k in s.iter():
    if type(k.attrib) == dict and len(k.attrib) > 0:
        dict_temp = k.attrib
        print(dict_temp)


"""
<?xml version="1.0" encoding="UTF-8"?>
<ns0:ListUrlsRequest xmlns:ns0="urn:nornik.ru:sbox:po:sentukov">
   <response>
      <total_files/>
      <max_banch/>
      <file_banch>
         <people/>
         <company/>
      </file_banch>
   </response>
</ns0:ListUrlsRequest>

{number :'1', 'name': 'ListUrlsRequest', 'type': 'ListUrls'}
{number :'1.1', 'name': 'ListUrls'}
{number :'1.1.1', 'name': 'response'}
{number :'1.1.1.1', 'name': 'total_files', 'type': 'xsd:string', 'minOccurs': '0'}
{number :' 1.1.1.2', 'name' : 'max_banch', 'type': 'xsd:string', 'minOccurs': '0'}
{number :'1.1.1.3', 'name': 'file_banch'}
{number :'1.1.1.3.1', 'name': 'people', 'type': 'xsd:string', 'maxOccurs': 'unbounded'}
{number :'1.1.1.3.2', 'name': 'company', 'type': 'xsd:string', 'minOccurs': '0', 'maxOccurs': 'unbounded'}
"""