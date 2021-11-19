import re
import bs4
import requests
import svc_config


class Lookup:
    global results
    results = [
        {
            "talos": {
                "blacklist": [],
                "information": []
            },
            "abuseipdb": {
                "summary": [],
                "information": []
            },
            "virustotal": {
                "summary": [],
                "resolutions": [],
                "domain": [],
                "url": []
            },
            # "whois": {
            #     "location": [],
            #     "misc": []
            # },
            "ibm": {
                "summary": [],
                "geo": []
            }
        }
    ]

    def __init__(self, ip, resolved_ip, user_input):
        self.ip = ip
        self.resolved_ip = resolved_ip
        self.user_input = user_input

    def talos(self):

        talos_blacklist = results[0]["talos"]["blacklist"]
        talos_information = results[0]["talos"]["information"]

        if self.ip == "":
            self.ip = self.resolved_ip
        else:
            self.ip = self.ip

        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.90 Safari/537.36',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': f'https://www.talosintelligence.com/reputation_center/lookup?search={self.ip}',
            'authority': 'www.talosintelligence.com',
            'cookie': '<cookie>',
        }

        params = (
            ('query', '/api/v2/details/ip/'),
            ('query_entry', self.ip),
            ('offset', '0'),
            ('order', 'ip asc'),
        )
        # predefine the fields we want so we can keep the code clean
        updated_fields = {'blacklists': 'Blacklists', 'ip': 'IP', 'hostname': 'Hostname', 'dnsmatch': 'DNS Match',
                            'organization': 'Organization', 'email_score_name': 'Email reputation',
                            'web_score_name': 'Web reputation', 'daily_mag': 'Daily spam number',
                            'monthly_spam_name': 'Monthly spam', 'monthly_mag': 'Monthly spam number'}


        try:
            get_query = requests.get('https://www.talosintelligence.com/sb_api/query_lookup',
                                     headers=headers, params=params).json()

            # begin the loop!
            for k, v in updated_fields.items():
                if 'blacklists' in k:
                    # detemine if the blacklist contains the ip
                    for src, rule in get_query[k].items():
                        if len(rule['rules']) > 0:
                            tmp = "Yes"
                        else:
                            tmp = "No"
                        talos_blacklist.append(str(src) + ": " + tmp)
                # determine if there was a reverse dns match
                elif "dnsmatch" in k:
                    if get_query[k] == 1:
                        talos_information.append(v + ": Yes")
                    else:
                        talos_information.append(v + ": No")
                else:
                    # fill out the rest
                    try:
                        talos_information.append(v + ": " + str(get_query[k]))
                    except:
                        talos_information.append(v + ": N/A")

        except:
            pass

    def abuseipdb(self):

        does_exist = False
        abuseipdb_summary = results[0]["abuseipdb"]["summary"]
        abuseipdb_information = results[0]["abuseipdb"]["information"]

        get_abuseipad = requests.get(f"https://www.abuseipdb.com/check/{self.ip}")
        get_html = bs4.BeautifulSoup(get_abuseipad.text, "html.parser")

        try:
            get_desc = get_html.select_one('#report-wrapper > p:nth-child(3)').get_text()

            get_confidence = get_html.select_one('#report-wrapper > div:nth-child(1) > div:nth-child(1) '
                                                 '> div > p:nth-child(2)').get_text()
            get_confidence = get_confidence[:-3]  # remove the trailing '?'

            abuseipdb_summary.append(get_desc)
            abuseipdb_summary.append(get_confidence)
            does_exist = True
        except AttributeError:
            abuseipdb_summary.append("IP address not listed in AbuseIPDB")

        if does_exist:
            all_comments = get_html.find_all('td', attrs={'data-title': 'Comment'})

            new_comments = []

            for comment in all_comments:
                new_comments.append(re.sub(r'\n\s*\n', '\n', comment.text.strip()))

            get_comments = list(filter(None, new_comments))

            for comment in get_comments:
                show_more = re.findall(r"(?<=show more)(.+)((?:\n.+)+)(?=show less)", comment)

                if show_more:
                    for full_comment in show_more:
                        for com in full_comment:
                            abuseipdb_information.append(com)
                else:
                    abuseipdb_information.append(comment)

    # TODO: replace and trim when we get the virustotal private api key
    def virustotal_run(self):
        # set the key from private file
        my_api = svc_config.virustotal_key

        virustotal_summary = results[0]["virustotal"]["summary"]
        virustotal_resolutions = results[0]["virustotal"]["resolutions"]
        virustotal_domain = results[0]["virustotal"]["domain"]
        virustotal_url = results[0]["virustotal"]["url"]

        # ------------------------------------------------------------------------------------------
        # ip resolutions
        # ------------------------------------------------------------------------------------------

        url = 'https://www.virustotal.com/vtapi/v2/ip-address/report'
        params = {'apikey': my_api, 'ip': self.ip}
        report = requests.get(url, params=params)

        if report.status_code == 200:
            resp_format = report.json()
            virustotal_summary.append(resp_format["verbose_msg"])

            if "Missing IP address" in resp_format["verbose_msg"]:
                return
        elif report.status_code == 204:
            virustotal_summary.append(
                "Please wait a minute for VirusTotal API check window to reopen!")
            return
        else:
            virustotal_summary.append(f"HTML Status Code: {report.status_code}")
            return

        # get the domains associated with the IP
        try:
            for hosts in resp_format['resolutions']:
                virustotal_resolutions.append(hosts['hostname'])
        except:
            virustotal_resolutions.append("No resolved URLs associated with IP")

        # ------------------------------------------------------------------------------------------
        # domain report
        # ------------------------------------------------------------------------------------------

        if resp_format["detected_urls"] and len(resp_format["detected_urls"]) > 0:

            url = 'https://www.virustotal.com/vtapi/v2/domain/report'
            params = {'apikey': my_api, 'domain': self.user_input}
            domain_report = requests.get(url, params=params)

            # check the status code first before formatting 
            if domain_report.status_code == 200:
                domain_resp = domain_report.json()

            domain_fields = ["BitDefender category", 'Forcepoint ThreatSeeker category']

            try:
                # loop through the domain fields and append when appropriate
                if len(domain_resp['detected_urls']) > 0:
                    virustotal_domain.append("URL: " + self.user_input)
                    for i in domain_fields:
                        try:
                            virustotal_domain.append(str(i) + ": " + domain_resp[i])
                        except:
                            pass
            except:
                virustotal_domain.append("No category for URL")

        # ------------------------------------------------------------------------------------------
        # url report
        # ------------------------------------------------------------------------------------------

        url = 'https://www.virustotal.com/vtapi/v2/url/report'
        # change user_input to passed in name
        params = {'apikey': my_api, 'resource': self.user_input}
        # params = {'apikey': my_api, 'resource': original_input}
        url_report = requests.get(url, params=params)

        if url_report.status_code == 200:
            url_resp = url_report.json()
        else:
            return

        try:
            virustotal_url.append(
                'Total positive scans for ' + self.user_input + ": " + str(url_resp['positives']) + "/" + str(
                    url_resp['total']))

            for key, val in url_resp['scans'].items():
                if val["detected"]:
                    virustotal_url.append(key + " has detected: " + val['result'])

        except:
            virustotal_url.append("Unable to retrieve URL details")

    # uses the whois libary to mainly get the geo loaction details
    # def whois_dat_boi(self):
    #
    #     if self.ip == "":
    #         self.ip = self.resolved_ip
    #     else:
    #         self.ip = self.ip
    #
    #     whois_location = results[0]["whois"]["location"]
    #     whois_misc = results[0]["whois"]["misc"]
    #
    #     loc_filters = ['country', 'state', 'city', 'address', 'postal_code']
    #     misc_filters = ['cidr', 'name', 'handle', 'range', 'description', 'emails', 'created', 'updated']
    #
    #     try:
    #         # send in the IP
    #         obj = IPWhois(self.ip)
    #         # get the whois info and filter to get what we need
    #         response = obj.lookup_whois()
    #         # response = obj.lookup_rdap(asn_methods=["whois"])
    #         # response = obj.lookup_rdap()
    #
    #         filtered = response['nets'][0]
    #
    #         # reformat the response in the way we want
    #         for key, val in filtered.items():
    #             if isinstance(val, list):
    #                 for x in val:
    #                     if str(key) in loc_filters:
    #                         whois_location.append(key + ': ' + x)
    #                     elif str(key) in misc_filters:
    #                         whois_misc.append(key + ': ' + x)
    #             else:
    #                 if str(key) in loc_filters:
    #                     whois_location.append(key + ': ' + val)
    #                 elif str(key) in misc_filters:
    #                     whois_misc.append(key + ': ' + val)
    #     except:
    #         whois_location.append("NA")
    #         whois_misc.append("NA")

    def ibm_xmen(self):
        # encode the token to appease the security gods!!!!
        # token = base64.b64encode(svc_config.ibm_xforce_key + ":" + svc_config.ibm_xforce_pass) # .... didnt work
        headers = {'Accept': 'application/json',
                   'Authorization': 'Basic <token>'}
        url = 'https://api.xforce.ibmcloud.com/ipr/' + self.ip

        # send that request boi
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            resp_format = response.json()

        # just add it my dude
        xmen_summary = results[0]["ibm"]["summary"]
        xmen_geo = results[0]["ibm"]["geo"]

        # Add the shitaki to the summary
        xmen_summary.append("IP: " + str(resp_format['ip']))
        xmen_summary.append("Reason: " + str(resp_format['reason']))
        xmen_summary.append("Detailed description: " + str(resp_format['reasonDescription']))
        xmen_summary.append("Score: " + str(resp_format['score']))

        # Add more shitaki
        xmen_geo.append("Location: " + str(resp_format["geo"]["country"]))

    def start(self):
        # lookup_funks = ["Lookup.talos", "abuseipdb", "virustotal_run", "whois_dat_boi", "ibm_xmen"]
        #
        # for funk in lookup_funks:
        #     thread = threading.Thread(target=funk, args=(self,), name="Thread")
        #     thread.start()
        #
        # for t in threading.enumerate():
        #     t.join() if t is not threading.currentThread() else None

        self.talos()
        self.abuseipdb()
        self.virustotal_run()
        # self.whois_dat_boi()
        self.ibm_xmen()

        return results

    def reset(self):
        global results
        results = [
            {
                "talos": {
                    "blacklist": [],
                    "information": []
                },
                "abuseipdb": {
                    "summary": [],
                    "information": []
                },
                "virustotal": {
                    "summary": [],
                    "resolutions": [],
                    "domain": [],
                    "url": []
                },
                # "whois": {
                #     "location": [],
                #     "misc": []
                # },
                "ibm": {
                    "summary": [],
                    "geo": []
                }
            }
        ]
