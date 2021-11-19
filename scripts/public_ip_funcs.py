from flask import flash, redirect, url_for, jsonify
import requests, json
import svc_config

class Public_IPs:
    def __init__(self, public_ip_input, comments, contacted_input, tenable_input, group, status, vuln, contact_info):
        self.public_ip_input = public_ip_input
        self.comments = comments
        self.contacted_input = contacted_input
        self.tenable_input = tenable_input
        self.group = group
        self.status = status
        self.vuln = vuln
        self.contact_info = contact_info


    def public_ip_new(self):
        # get the kv store data
        public_ips_data = public_ips_Data_script()
        last_id = 0
        # check if the key exists
        for i in public_ips_data.json['data']:
            if self.public_ip_input == i['IP_Address']:
                flash("Warning: Public IP is already in list.", 'warning')
                return redirect(url_for('public_ips'))
            last_id = int(i['ID'])  # just a note/reminder: last_id is used to determine what the next unique id should be

        # below is just a reminder of all the headers the table has:
        # column_head = ["ID", "IP_Address", "VRF", "College_Dept_Group", "Status", "Contact_Info", "Tenable_Agent" "Contacted", "Comments", "DNS_concat", "OS_concat", "Description", "DistinguishedName", "EMailID", "Model", "OU", "UserName", "hostname", "Vulnerability"]
        
        # loop through the array and append to data var
        col_heads = ["VRF", "DNS_concat", "OS_concat", "Description", "DistinguishedName", "EMailID", "Model", "OU", "UserName", "hostname"]
        data = '{'
        for i in col_heads:
            data = data + '"' + str(i) + '": "", '
        last_id = last_id+1
        # append the rest of the data onto the end
        data = data + '"ID": '+str(last_id)+ ', "IP_Address": "'+self.public_ip_input+'", "College_Dept_Group": "'+self.group+'", "Comments": "'+self.comments+'", "Tenable_Agent": "'+self.tenable_input+'", "Contacted": "'+self.contacted_input+'", "Status": "'+self.status+'", "Contact_Info": "'+self.contact_info+'", "Vulnerability": "'+self.vuln+'"}'


        # create new entry
        headers = {'Content-Type': 'application/json'}
        response = requests.post('https://<ten_id>.splunkcloud.com:8089/servicesNS/nobody/ITS-security/storage/collections/data/PublicIPv8', headers=headers, data=data, verify=False, auth=(svc_config.splunk_user, svc_config.splunk_ps))

        # make sure it was successfully created
        if response.status_code == 201:
            flash("Public IP has been added.", 'success')
            return redirect(url_for('public_ips'))

        else:
            flash("Error: Recieved Status Code: " + response.status_code + ", Reason: " + response.reason, 'warning')
            return redirect(url_for('public_ips'))


    # naming convention might seem a lil weird but its due to moving these functions from routes.py to here... that and mixed with my laziness
    def public_ips_update_func(self, key_val, action, request):
        # loop through the array and append to data var
        col_heads = ["ID", "VRF", "DNS_concat", "OS_concat", "Description", "DistinguishedName", "EMailID", "Model", "OU", "UserName", "hostname"]
        data = '{'
        for i in col_heads:
            data = data + '"' + i + '": "' + request.form[i] + '", '
        
        # append the rest of the data onto the end
        data = data + '"IP_Address": "'+self.public_ip_input+'", "College_Dept_Group": "'+self.group+'", "Comments": "'+self.comments+'", "Tenable_Agent": "'+self.tenable_input+'", "Contacted": "'+self.contacted_input+'", "Status": "'+self.status+'", "Contact_Info": "'+self.contact_info+'", "Vulnerability": "'+self.vuln+'"}'

        headers = {'Content-Type': 'application/json'}
        url = 'https://<ten_id>.splunkcloud.com:8089/servicesNS/nobody/ITS-security/storage/collections/data/PublicIPv8/'+key_val

        # determine if we are updating or deleting
        response = None
        if action == 'update':
            # update splunk kv store
            response = requests.post(url, headers=headers, data=data, verify=False, auth=(svc_config.splunk_user, svc_config.splunk_ps))

        elif action == 'delete':
            # delete splunk kv store entry by key
            response = requests.delete(url, headers=headers, verify=False, auth=(svc_config.splunk_user, svc_config.splunk_ps))

        if response.status_code == 200:
            flash("Public IP has been " + action + 'd.', 'success')
            return redirect(url_for('public_ips'))

        else:
            flash('Error: Generic unhelpful error. Contact Jared Rigdon.', 'warning')
            return redirect(url_for('public_ips'))




def public_ips_Data_script():
    public_ips_data = {}
    # query splunk for the full kv store list
    headers = {'Content-Type': 'application/json'}
    response = requests.get('https://<ten_id>.splunkcloud.com:8089/servicesNS/nobody/ITS-security/storage/collections/data/PublicIPv8', headers=headers, verify=False, auth=(svc_config.splunk_user, svc_config.splunk_ps))
    column_head = ["ID", "IP_Address", "VRF", "College_Dept_Group", "Status", "Vulnerability", "Contact_Info", "Tenable_Agent", "Contacted", "Comments", "DNS_concat", "OS_concat", "Description", "DistinguishedName", "EMailID", "Model", "OU", "UserName", "hostname"]
    temp_data = []
    try:
        if response.status_code == 200:
            public_ips_data = json.loads(response.text)
            for i in public_ips_data:
                for j in column_head:
                    if not(j in i):
                        i.update({j: ""})
                temp_data.append(i)
        else:
            temp_data = {'NA'}
    except:
        temp_data = {'NA'}

    # final pre stuff
    public_ips_dataFinal = {"data": temp_data}
    return jsonify(public_ips_dataFinal)
