import requests
import json
import xml.etree.ElementTree as ET
from Configs.config import configs
import base64

class WorkQueues:

    def __init__(self):
        
        '''
        BluePrism work queue API setup
        Limitations: 
        - Item tag can not be changed until mark as completed or exception stage
        - Item state can not be changed until mark as completed or exception stage
        '''
        cred_string = f"""{configs['BP_USERNAME']}:{configs['BP_PASSWORD']}"""
        bp_cred = base64.b64encode(cred_string.encode('ascii')).decode("ascii")
        cred = f"""Basic {bp_cred}"""
        
        self.headers = {
            'Authorization': cred,
            'Content-Type': 'text/plain'
        }

        self.url = f"""http://{configs['host_machine']}:{configs['port']}/ws/workqueues"""

        self.QueueName = configs['Queue_Name']
    
    def add_to_queue(self,QueueItems,KeyName):

        '''
        Add item to blue prism work queue, input data type: list of dicts
        '''
        QueueItems = json.dumps(QueueItems)

        payload = f"""
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:blueprism:webservice:workqueues">
            <soapenv:Header/>
            <soapenv:Body>
                <urn:addtoqueue soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                    <bpInstance xsi:type="xsd:string">auto</bpInstance>
                    <QueueName xsi:type="xsd:string">{self.QueueName}</QueueName>
                    <QueueItems xsi:type="xsd:string">{base64.b64encode(QueueItems.encode('ascii')).decode("ascii")}</QueueItems>
                    <KeyName xsi:type="xsd:string">{KeyName}</KeyName>
                </urn:addtoqueue>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        response = requests.request("POST", url = self.url, headers=self.headers, data=payload)

        fault = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find(r'{http://schemas.xmlsoap.org/soap/envelope/}Fault')

        if response.status_code == requests.codes.ok and not fault:
            return True
        elif fault:
            e = fault.find(r'{http://schemas.xmlsoap.org/soap/envelope/}faultstring').text
            raise Exception(e)
        else:
            raise Exception("Error: unsuccessfull HTTP request")

    def get_next_item(self):

        '''
        Get next pending item from blue prism work queue
        Output: 
        - queue item in a dictionary 
        - item id as string
        '''

        payload = f"""
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:blueprism:webservice:workqueues">
            <soapenv:Header/>
            <soapenv:Body>
                <urn:getnextitem soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                    <bpInstance xsi:type="xsd:string">auto</bpInstance>
                    <QueueName xsi:type="xsd:string">{self.QueueName}</QueueName>
                </urn:getnextitem>
            </soapenv:Body>
        </soapenv:Envelope>
        """

        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        
        fault = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find(r'{http://schemas.xmlsoap.org/soap/envelope/}Fault')

        if response.status_code == requests.codes.ok and not fault:
            data = json.loads(ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find('getnextitem').find('Data').text)
            queue_ID = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find('getnextitem').find('ItemID').text
            if len(data)>0:
                return data[0], queue_ID
            else:
                return None, None
        elif fault:
            e = fault.find(r'{http://schemas.xmlsoap.org/soap/envelope/}faultstring').text
            raise Exception(e)
        else:
            raise Exception("Error: unsuccessfull HTTP request")


    def mark_item_as_completed(self,Item_ID,status="",tag=""):

        '''
        Mark blue prism work item as completed 
        Input: 
        - item id as string (required)
        - item status as string (optional)
        - item tag as string (optional)
        Output:
        - Bool: Success or Failed
        '''

        payload = f"""
            <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:blueprism:webservice:workqueues">
            <soapenv:Header/>
            <soapenv:Body>
                <urn:markcompleted soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                    <bpInstance xsi:type="xsd:string">auto</bpInstance>
                    <ItemID xsi:type="xsd:string">{Item_ID}</ItemID>
                    <QueueName xsi:type="xsd:string">{self.QueueName}</QueueName>
                    <Status xsi:type="xsd:string">{base64.b64encode(status.encode('ascii')).decode("ascii")}</Status>
                    <Tag xsi:type="xsd:string">{base64.b64encode(tag.encode('ascii')).decode("ascii")}</Tag>
                </urn:markcompleted>
            </soapenv:Body>
            </soapenv:Envelope>
        """

        response = requests.request("POST", self.url, headers=self.headers, data=payload)

        fault = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find(r'{http://schemas.xmlsoap.org/soap/envelope/}Fault')

        if response.status_code == requests.codes.ok and not fault:
            return True
        elif fault:
            e = fault.find(r'{http://schemas.xmlsoap.org/soap/envelope/}faultstring').text
            raise Exception(e)
        else:
            raise Exception("Error: unsuccessfull HTTP request")


    def mark_item_as_exception(self,Item_ID,Exception_Reason,status="",tag=""):
        '''
        Mark blue prism work item as completed 
        Input: 
        - item id as string (required)
        - exception reason (required)
        - item status as string (optional)
        - item tag as string (optional)
        Output:
        - Bool: success or failed
        '''

        payload = f"""
            <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:blueprism:webservice:workqueues">
                <soapenv:Header/>
                <soapenv:Body>
                    <urn:markexception soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                        <bpInstance xsi:type="xsd:string">auto</bpInstance>
                        <ItemID xsi:type="xsd:string">{Item_ID}</ItemID>
                        <ExceptionReason xsi:type="xsd:string">{base64.b64encode(Exception_Reason.encode('ascii')).decode("ascii")}</ExceptionReason>
                        <QueueName xsi:type="xsd:string">{self.QueueName}</QueueName>
                        <Status xsi:type="xsd:string">{base64.b64encode(status.encode('ascii')).decode("ascii")}</Status>
                        <Tag xsi:type="xsd:string">{base64.b64encode(tag.encode('ascii')).decode("ascii")}</Tag>
                    </urn:markexception>
                </soapenv:Body>
            </soapenv:Envelope>
        """
        response = requests.request("POST", self.url, headers=self.headers, data=payload)

        fault = ET.fromstring(response.text).find(r'{http://schemas.xmlsoap.org/soap/envelope/}Body').find(r'{http://schemas.xmlsoap.org/soap/envelope/}Fault')

        if response.status_code == requests.codes.ok and not fault:
            return True
        elif fault:
            e = fault.find(r'{http://schemas.xmlsoap.org/soap/envelope/}faultstring').text
            raise Exception(e)
        else:
            raise Exception("Error: unsuccessfull HTTP request")

