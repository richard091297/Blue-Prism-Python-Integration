import base64
import requests
import xml.etree.ElementTree as ET
from Configs.config import configs

class Credentials:

    def __init__(self):

        '''
        blue prism credential api setup
        '''
        cred_string = f"""{configs['BP_USERNAME']}:{configs['BP_PASSWORD']}"""
        bp_cred = base64.b64encode(cred_string.encode('ascii')).decode("ascii")
        cred = f"""Basic {bp_cred}"""

        self.headers = {
            'Authorization': cred,
            'Content-Type': 'text/plain'
        }

        self.url = f"""http://{configs['host_machine']}:{configs['port']}/ws/credentials"""

    def get_credential(self,cred_name):

        '''
        get blue prism credential
        input:
        - credential name as string
        output:
        - username as string
        - password as string
        '''

        payload = f"""
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:blueprism:webservice:credentials">
        <soapenv:Header/>
        <soapenv:Body>
            <urn:getcred soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <bpInstance xsi:type="xsd:string">auto</bpInstance>
                <credname xsi:type="xsd:string">{cred_name}</credname>
            </urn:getcred>
        </soapenv:Body>
        </soapenv:Envelope>
        """
        response = requests.request("POST", url = self.url, headers=self.headers, data=payload)

        fault = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find(r'{http://schemas.xmlsoap.org/soap/envelope/}Fault')
        username = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find('getcred').find('username').text
        password = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find('getcred').find('password').text
        if response.status_code == requests.codes.ok and not fault:
            return username, password
        elif fault:
            return fault.find(r'{http://schemas.xmlsoap.org/soap/envelope/}faultstring').text
        else:
            return "Error: unsuccessfull HTTP request"
