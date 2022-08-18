from os import access
import requests
import json
from urllib.error import HTTPError
from time import sleep 

def makeRequest(method, session, url, data=None, exceptionMessage=None, handling=None):
    """makes a request and handles exceptions 

    Args:
        method (str): ['GET', 'POST', 'PATCH', 'DELETE'] request method
        session (requests.Session):
        url (str): url of the request
        data (dict, optional): data attached to the request. Defaults to None.
        exceptionMessage (str, optional): text added to the exception message. Defaults to None.
        handling (str, optional): [None, 'exit']. what to do in case of exception, if None script moves on. Defaults to None.
    """
    headers = session.headers
    request = requests.Request(method=method, url=url, data=data, headers=headers)
    preped = request.prepare()

    try:
        sleep(1)
        response = session.send(preped)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        if handling == 'exit':
            raise SystemExit(exceptionMessage + '\n', errh)
        raise errh


    return(response)

def get_software_version(machine_id, access_token, handling=None):
    """gets software version of a machine

    Args:
        machine_id (int): machine_id of the machines
        access_token (str): Bearer token with the write access for target machines
    """

    if type(machine_id) != int:
        raise TypeError('machine_id must be an integer')
        

    update_session = requests.Session()
    update_session.headers.update({'Accept': 'application/json', 'Authorization': 'Bearer '+access_token})
    
    baseUrl = 'https://api.eversys-telemetry.com/v3/machines/'
    url = baseUrl + 'software-infos/{machine_id}'.format(machine_id=machine_id)
    exceptionMessage = 'Coud not get software version of machine'
    try:
        getRequest = makeRequest('GET', update_session, url, exceptionMessage=exceptionMessage, handling=handling)
        
    except SystemExit as err:
        raise SystemExit(err)
    except requests.exceptions.HTTPError as err:
        return(err)
    return(getRequest.json()['version'])


    

def software_update(machine_list, access_token, software_id, software_version, execType='WITHOUT_NOTIFICATION', handling=None):
    """updates software on a machine

    Args:
        machine_list (list): list of machine_id of the machines we want to update
        access_token (str): Bearer token with the write access for target machines
        software_id (str): software_id of the software we want to update
        execType (str): how to execute the update. ['WITHOUT_NOTIFICATION', 'WITH_NOTIFICATION']
        side (str, optional): ['LEFT', 'RIGHT', 'CENTER']. Defaults to 'LEFT'. 
    """

    if type(machine_list) == int:
        machine_list = [machine_list]
    else:
        machine_list = list(machine_list)


    update_session = requests.Session()
    update_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer '+access_token})

    for machine_id in machine_list:

        
        if get_software_version(machine_id, access_token) != software_version:

            baseUrl = 'https://api.eversys-telemetry.com/v3/machines/'

            
            
            url = baseUrl + '{machine_id}/software-updates'.format(machine_id=machine_id)
            data = {'execType': execType, 'machineId': machine_id, 'softwareId': software_id}
            data = json.dumps(data, indent=4)
            exceptionMessage = 'Coud not update software on machine'
            try: 
                updateRequest = makeRequest('POST', update_session, url, data=data, exceptionMessage=exceptionMessage, handling=handling)
            except SystemExit as err:
                raise SystemExit(err)
            except requests.exceptions.HTTPError as err:
                print(err)
                continue
            print('Software update on machine {machine_id} started'.format(machine_id=machine_id))
        else:
            print('Software on machine {machine_id} is already up to date'.format(machine_id=machine_id))


def package_update(machine_list, access_token, package_id, execType='WITHOUT_NOTIFICATION', handling=None):
    """updates data package on a machine

    Args:
        machine_list (list): list of machine_id of the machines we want to update
        access_token (str): Bearer token with the write access for target machines
        package_id (str): package_id of the software we want to update
        execType (str): how to execute the update. ['WITHOUT_NOTIFICATION', 'WITH_NOTIFICATION']
        side (str, optional): ['LEFT', 'RIGHT', 'CENTER']. Defaults to 'LEFT'. 
    """

    if type(machine_list) == int:
        machine_list = [machine_list]
    else:
        machine_list = list(machine_list)


    update_session = requests.Session()
    update_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer '+access_token})

    for machine_id in machine_list:


        baseUrl = 'https://api.eversys-telemetry.com/v3/machines/'
        url = baseUrl + '{machine_id}/data-packages'.format(machine_id=machine_id)
        data = {'execType': execType, 'machineId': machine_id, 'packageId': package_id}
        data = json.dumps(data, indent=4)
        exceptionMessage = 'Coud not update package on machine'
        try: 
            updateRequest = makeRequest('POST', update_session, url, data=data, exceptionMessage=exceptionMessage, handling=handling)
        except SystemExit as err:
            raise SystemExit(err)
        except requests.exceptions.HTTPError as err:
            print(err)
            continue
        print('Package update on machine {machine_id} started'.format(machine_id=machine_id))



def download_display_settings(sourceMachine, accessToken, side='LEFT'):
    """dowload display settings from source machine and uploads it to all target machines

    Args:
        sourceMachine (str): machineId of the machine with the settings we want to distribute 
        accessToken (str): Bearer token with the write access for target machines and read access to source machine
        side (str, optional): ['LEFT', 'RIGHT', 'CENTER'] 
    """

    baseUrl = 'https://api.eversys-telemetry.com/v3/machines/'

    downloadSession = requests.Session()
    downloadSession.headers.update({'Accept': 'application/json', 'Authorization': 'Bearer '+accessToken})

    url = baseUrl + '{machineId}/display-parameters/{side}'.format(machineId=sourceMachine, side=side)
    exceptionMessage = 'Coud not download setting from source machine'
    downloadRequest = makeRequest('GET', downloadSession, url, exceptionMessage=exceptionMessage, handling='exit')
    displaySettings = downloadRequest.json()


def distribute_product_settings(sourceMachine, targetMachines, accessToken, side='LEFT'):
    """dowload product settings from source machine and uploads it to all target machines

    Args:
        sourceMachine (str): machineId of the machine with the settings we want to distribute 
        targetMachines (list): list of machineIds we want to upload settings to 
        accessToken (str): Bearer token with the write access for target machines and read access to source machine
        side (str, optional): ['LEFT', 'RIGHT', 'CENTER'] 
    """

    baseUrl = 'https://api.eversys-telemetry.com/v3/machines/'

    downloadSession = requests.Session()
    downloadSession.headers.update({'Accept': 'application/json', 'Authorization': 'Bearer '+accessToken})

    url = baseUrl + '{machineId}/product-parameters/{side}'.format(machineId=sourceMachine, side=side)
    exceptionMessage = 'Coud not download setting from source machine'
    try: 
        downloadRequest = makeRequest('GET', downloadSession, url, exceptionMessage=exceptionMessage, handling='exit')
    except SystemExit as err:
        raise SystemExit(err)
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
        except HTTPError as err:
            print(err)
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

