import requests
import json
from urllib.error import HTTPError 

def makeRequest(method, session, url, data=None, exceptionMessage=None, handling=None):
    """makes a request and handles exceptions 

    Args:
        method (str): ['GET', 'POST', 'PATCH', 'DELETE'] request method
        session (requests.Session):
        url (str): url of the request
        data (dict, optional): data attached to the request. Defaults to None.
        exceptionMessage (str, optional): text added to the exception message. Defaults to None.
        handling (str, optional): [None, 'exit', 'raise']. what to do in case of exception, if None script moves on. Defaults to None.
    """
    headers = session.headers
    request = requests.Request(method=method, url=url, data=data, headers=headers)
    preped = request.prepare()

    try:
        response = session.send(preped)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        if handling == 'exit':
            SystemExit(exceptionMessage + '\n', errh)
        print(exceptionMessage + '\n', errh)
        if handling == 'raise':
            raise HTTPError
        
    return(response)

def distribute_product_settings(sourceMachine, targetMachines, accessToken, side='LEFT'):
    """dowload product settings from source machine and uploads it to all target machines

    Args:
        sourceMachine (str): machineId of the machine with the settings we want to distribute 
        targetMachines (list): list of machineIds we want to upload settings to 
        accessToken (str): Bearer token with the write access for target machines and read access to source machine
        side (str, optional): ['LEFT', 'RIGHT', 'CENTER'] 
    """

    baseUrl = 'https://api.eversys-telemetry.com/v3​/machines​/'

    downloadSession = requests.Session()
    downloadSession.headers.update({'Accept': 'application/json', 'Authorization': 'Bearer '+accessToken})

    url = baseUrl + '{machineId}​/product-parameters​/{side}'.format(machineId=sourceMachine, side=side)
    exceptionMessage = 'Coud not download setting from source machine'
    downloadRequest = makeRequest('GET', downloadSession, url, exceptionMessage=exceptionMessage, handling='exit')
    productSettings = downloadRequest.json()

    #removing machineId from settings file
    for product in productSettings:
        product.pop('machineId', None)
    
    uploadSession = requests.Session()
    uploadSession.headers.update({'Accept': 'application/json', 'Content-Type': 'application/merge-patch+json', 'Authorization': 'Bearer '+accessToken})

    for machineId in targetMachines:

        url = baseUrl + '{machineId}/change-requests'.format(machineId=machineId)
        exceptionMessage = 'Could not create change request for machine {}'.format(machineId)
        try:
            changeRequest = makeRequest('POST', uploadSession, url, exceptionMessage=exceptionMessage, handling='raise')
        except HTTPError:
            continue
        requestId = changeRequest.json()['id']
        
        for product in productSettings:
            productId = product['productId']
            data = json.dumps(product, indent=4)
            url = baseUrl + '{machineId}/change-requests/{requestId}/product-parameters/{side}/{productId}'.format(machineId=machineId, requestId=requestId, side=side, productId=productId)
            exceptionMessage = 'Could not upload product {} for machine {}'.format(productId+1, machineId)
            uploadRequest = makeRequest('PATCH', uploadSession, url, exceptionMessage=exceptionMessage, data=data)

        url = baseUrl + '{machineId}/change-requests/{requestId}/apply'.format(machineId = machineId, requestId=requestId)
        exceptionMessage = 'Could not apply settings for machine {}'.format(machineId)
        applyRequest = makeRequest('POST', uploadSession, url, exceptionMessage=exceptionMessage, handling='exit')

    
