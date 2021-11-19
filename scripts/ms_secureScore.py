## Visit https://aka.ms/graphsecuritydocs for the Microsoft Graph Security API documention.

import json
import requests
import svc_config
from datetime import datetime, timedelta

# forward the resulting json to the splunk event collector to be stored
def forward_onto_splunk(secureScore_json):
    splunk_url = "https://http-inputs-<ten_id>.splunkcloud.com:443/services/collector"

    # this can be customized more in depth but is unnecessary for this script
    splunk_body = {
        "event":secureScore_json['value'][0],
        "sourcetype": "ms_secureScore"
        # "sourcetype": "ms_secureScore_test"
    }
    splunk_headers = {
    'Authorization': f'Splunk {svc_config.splunk_hec_token}',
    }
    splunk_resp = json.loads(requests.post(splunk_url, headers=splunk_headers, json=splunk_body).content)
    # below was used for testing purposes
    # with open("ms_secureScore_output.txt", "w+") as log_file:
    #     print(f"Timestamp: {datetime.now()},\tSplunk Response Text: {splunk_resp['text']},\tSplunk Response Code: {splunk_resp['code']}", file=log_file)


def make_request(url, headers):
    """
    Makes a GET request. This can be applied to alerts, TI indicators, secure scores.
    :param url: Url of the request.
    :returns: json response.
    :raises HTTPError: raises an exception
    """

    try:
        resp_data = json.loads(requests.get(url, headers=headers).content)
    except requests.exceptions.HTTPError as e:
        raise e

    return resp_data


def main():
    ## Register an Azure Active Directory application with the 'SecurityEvents.ReadWrite.All' Microsoft Graph Permission.
    ## Get your Azure AD tenant administrator to grant administration consent to your application. This is a one-time activity unless permissions change for the application. 
    appId = svc_config.appId
    appSecret = svc_config.appSecret
    tenantId = svc_config.tenantId

    # Azure Active Directory token endpoint.
    url = "https://login.microsoftonline.com/%s/oauth2/v2.0/token" % (tenantId)
    body = {
        'client_id' : appId,
        'client_secret' : appSecret,
        'grant_type' : 'client_credentials',
        'scope': 'https://graph.microsoft.com/.default'
    }

    # ## authenticate and obtain AAD Token for future calls
    resp = json.loads(requests.post(url, data=body).content)

    # Grab the token from the response then store it in the headers dict.
    aadToken = resp["access_token"]
    headers = { 
        'Content-Type' : 'application/json',
        'Accept' : 'application/json',
        'Authorization' : "Bearer " + aadToken
    }

    # get current date and subtract one day to get the previous day for enriched data
    graph_filter = "createdDateTime eq " + (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    # select arg will determine which columns are returned
    graph_select = "activeUserCount,currentScore,enabledServices,licensedUserCount,maxScore,vendorInformation,averageComparativeScores"

    secureScore_url = f"https://graph.microsoft.com/v1.0/security/secureScores?$filter={graph_filter}&$select={graph_select}"

    # hehe
    forward_onto_splunk(make_request(secureScore_url, headers))

main()