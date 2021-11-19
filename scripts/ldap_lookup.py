import base64, json, requests
import svc_config
from cybsec.le_routes.importTest import get_user

# not initializing a class as this is a short script that doesnt require modifying specific elements 
def user_lookup(form):
    # initialize and set variables 
    results = {}
    resultsFinal = []
    search_for = form.user_input.data
    type_input = form.type_input.data
    domain = type_input.lower()

    # set svc account creds
    svc_account = svc_config.svc_account
    password = svc_config.svc_ps

    # set attr list
    attr_list = [ "<attributes>"]
    
    out = get_user(domain, svc_account, password, attr_list, search_for)

    # check the bool val of the flag
    if (out):
        # define the values we want to look for to build out the table
        attr_table = ['<attributes>']

        # loop through results and match obj key with attr table then assign to value
        for obj in out:
            if (obj.key in attr_table):
                results[obj.key] = out[obj.key].value

        # loop through attr table and check if the key exists
        for j in attr_table:
            if not (j in results.keys()):
                results[j] = "null"

        #get the mcas score and status
        results.update(mcas_score(search_for))

        # required for the ajax side of things... for some reason?
        resultsFinal = [results]

    return resultsFinal



def mcas_score(linkblue):
    status = "NA"   # set default var

    # setup the json string and then convert using base64
    entity_pre = '{"id":"'+linkblue.lower()+'@<tenant_suffix>'+'","saas":11161,"inst":0}'
    entity_pre2 = entity_pre.encode("utf-8")
    entity_id = base64.b64encode(entity_pre2)
    entity_id2 = entity_id.decode('ascii')
    # the following token is used to connect to the mcas api
    token = 'token'
    headers = {
    'Authorization': 'Token {}'.format(token),
    }

    url = '<mcas_link>'+entity_id2+'/'
    temp4 = json.loads(requests.post(url, headers=headers).content)
    # status: 2 = active, 3 = inactive/disabled user
    try:
        score = temp4['threatScore']
        if temp4['status'] == 2:
            status = 'Active'
        elif temp4['status'] == 3:
            status = 'Inactive/Disabled'

    except:
        score = "Unable to find by linkblue"
        status = "NA"

    final = {'MCAS_Score': score, 'MCAS_Status': status}
    return final
