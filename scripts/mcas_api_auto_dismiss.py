import requests
import json
import svc_config


# the following mcas_token is used to connect to the mcas api
# mcas_token = svc_config.mcas_token
# headers = {
# 'Authorization': 'Token {}'.format(mcas_token),
# }
# headers_send = {
# 'Authorization': 'Token {}'.format(mcas_token),
# 'Content-Type': 'application/json'
# }

# IPQualityScore vpn check
def vpn_check(ip_str):
    key_val_check = ['proxy', 'vpn', 'tor']
    vpnCheck_token = svc_config.vpnCheck_token
    base_url = f'https://ipqualityscore.com/api/json/ip/{vpnCheck_token}/{ip_str}?strictness=1'

    response = json.loads(requests.post(base_url).content)

    # check if we get results returned
    if response['success']:
        # check if any of the desired field values are True
        for i in key_val_check:
            if response[i]:
                return True

    return False


def alert_parse(alert_list):
    # loop through the results and check the country type to see if we need to add it to the list
    dismissable_alerts = []
    vpn_alerts = []

    for i in alert_list['data']:
        if (i['title'].startswith('Risky sign-in:')) or (i['title'].startswith('Impossible travel activity')):
            # initialize a dict with pre-populated keys 
            temp_info = {'policyRule': [], 'ip': [], 'country': []}
            for j in i['entities']:
                # check the different types and gather the info needed
                if (j['type'] == 'policyRule') or (j['type'] == 'ip') or (j['type'] == "country"):
                    temp_info[j['type']].append(j['label'])
            
            # check the length of the country list for case of multiple IPs and if US or CA
            if (('US' in temp_info['country']) or ('CA' in temp_info['country'])) and (len(temp_info['country']) == 1):
                # add to false alert list
                dismissable_alerts.append(i['_id'])

            else:
                # loop through IPs from alert
                for x in temp_info['ip']:
                    # if it is a vpn, then append id to vpn_alerts list if not already in one 
                    if vpn_check(x) and not(i['_id'] in vpn_alerts) and not(i['_id'] in dismissable_alerts):
                        vpn_alerts.append(i['_id'])

        elif (i['title'].startswith('Activity from a Tor IP address')) or (i['title'].startswith('Activity from an anonymous proxy')):
            vpn_alerts.append(i['_id']) # add to vpn alert list as TOR or proxy isnt against our policies

    temp_lists = [dismissable_alerts, vpn_alerts]
    return temp_lists


def main():
    
    mcas_token = svc_config.mcas_token
    headers = {
    'Authorization': 'Token {}'.format(mcas_token),
    }

    main_url = 'https://<ten_ID>.us.portal.cloudappsecurity.com'

    # set up the filters to only get the risky signin alerts
    # https://docs.microsoft.com/en-us/cloud-app-security/api-alerts#filters
    alert_filter = {
        "filters":{
            # "alertOpen": "true",  # for some reason this filter is causing major issues. resolutionStatus should provide the same results
            "severity": {"eq": [0, 1, 2]},
            "resolutionStatus": {"eq": 0},
            },
            "limit": 50 #set limit to 50 as this is going to run every 15 mins
        }

    alert_list = main_url+'/api/v1/alerts/'
    alert_response = json.loads(requests.post(alert_list, headers=headers, json=alert_filter).content)

    # parse through the alerts to gather them into a set of lists 
    temp_lists = alert_parse(alert_response)    

    # check if the either lists are empty
    for i in temp_lists:
        if len(i) != 0:
            # dismissable alerts
            if temp_lists.index(i) == 0:
                # only call this AFTER we get the list of alerts
                closing_filter = {
                    "filters":{
                        "id": {
                            "eq":i
                        }
                    },
                    "comment": "Auto-dismiss for US and CA.",
                    "reasonId": 0,
                }
                closing_call = main_url+'/api/v1/alerts/close_false_positive/'

            # vpn alerts
            if temp_lists.index(i) == 1:
                closing_filter = {
                    "filters":{
                        "id": {
                            "eq":i
                        }
                    },
                    "comment": "Auto-dismiss. VPN or Proxy detected.",
                    "reasonId": 4,
                }
                closing_call = main_url+'/api/v1/alerts/close_benign/'

            '''
            could make another call to mark all alerts which dont appear in either list and have them marked as read
            '''

            # closing_call = main_url+'/api/v1/alerts/close_false_positive/'
            closing_response = json.loads(requests.post(closing_call, headers=headers, json=closing_filter).content)

    # debug breakpoint
    # x=42

main()