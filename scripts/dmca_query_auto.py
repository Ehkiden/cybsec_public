import svc_config
import requests
import json

def curl_yo_self(dmca_data):
    url = 'https://cybsec.<tenant_id>.edu/api/dmca'
    api_key = 'SoZVrdjTpNp49uQ4U7y4fg'
    dmca_format = json.dumps(dmca_data)

    data = {
        'email_body': dmca_format,
        'key': api_key
    }


    # headers = {'Content-type': 'application/json'}
    resp = requests.post(url, data=data, verify=False, auth=(svc_config.splunk_user, svc_config.splunk_ps))


def main():
    results_data = {
        "output_mode": "json"
    }
    # setup a search to run for the last hour
    data = {
        'search': f'search index=its_security sourcetype=dmca earliest=-1h@h latest=@h '
        '| table _raw',
        'output_mode': 'json'
    }

    # attack! (aka. create the job)
    saved_search = requests.post('https://<ten_id>.splunkcloud.com:8089/services/search/jobs', data=data, verify=False,
                             auth=(svc_config.splunk_user, svc_config.splunk_ps))
    # get the job sid
    job = json.loads(saved_search.text)
    
    # keep checking until be get a response
    # NOTE: might want to go ahead and wait 1 sec so we arent bombarding splunk
    flag = False
    while flag != True:
        results = requests.get(f'https://<ten_id>.splunkcloud.com:8089/services/search/jobs/{job["sid"]}/results',
                               data=results_data, verify=False,
                               auth=(svc_config.splunk_user, svc_config.splunk_ps))
        if results.status_code == 200:
            flag = True


    results_json = json.loads(results.text)
    curl_yo_self(results_json["results"])


main()