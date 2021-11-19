import socket
import re
import ldap3
import os

from cybsec import db, app

from cybsec.models import User, DmcaHistory

from sqlalchemy import text
from datetime import datetime
import pandas as pd
import svc_config

'''
#################################################################################################################################
# Import Testing #
#################################################################################################################################
'''


def get_user(dc, user, password, attr, search):
    server = ldap3.Server('<ldap_prefix>.'+dc+'<ldap_suffix>')
    connection = ldap3.Connection(server, user=user + "@<tenant_suffix>", password=password)
    connection.bind()

    #test to see if the passed in attr var is a list or not
    if not (isinstance(attr, list)):
        attr = [attr]

    # realized we are building and binding a connection to the server everytime so this should keep the connection until the attri list runs out
    for i in attr:
        connection.search(search_base=f'DC={dc},<tenant_info>',
                        search_filter=f'(&(objectClass=user)({i}={search}))',
                        attributes='*')
        
        try:
            entry = connection.entries[0]

            return entry
        except:
            pass

    return False


def ldap_lookup_checkv2(user_search):
    domain = 'AD'
    search_for = user_search

    results = {}

    domain_list = ["ad", "mc"]
    attr_list = ["<attr_vals>"]

    flag = False

    try:
        # check if they are in the system with said attr
        out = get_user("ad", svc_config.svc_account, svc_config.svc_ps, attr_list, search_for)
        flag = True
        
    except IndexError:
        flag = False
        pass
    
    # check the bool val of the flag
    if (not flag):
        return 0


    try:
        results.update({'distinguishedName': out["distinguishedName"].value})
    except:
        pass
    

    try:
        results.update({"memberOf": out["memberOf"].value})
    except:
        pass
    

    return results


def add_user(curr_user):
    groups = ["<group_list>"]

    # check if user is currently in db
    check_user = User.query.filter_by(username=curr_user).first()

    if (not check_user):
        # query ldap server
        temp = ldap_lookup_checkv2(curr_user)

        if temp == 0:
            return False

        if (not ('_DisabledAccounts' in temp['distinguishedName'])):
            # loop through group and add user accourdingly
            # set a flag outside the for loop
            flag = False

            for i in groups:
                for j in temp['memberOf']:
                    if (i in j):
                        flag = True
                        break
                else:
                    continue  # only executed if the inner loop did NOT break
                break  # only executed if the inner loop DID break

            # we assume that all other rolls are already in the db
            if (flag):
                user = User(username=curr_user, role="ADMIN")
            else:
                user = User(username=curr_user, role="USER")

        else:
            user = User(username=curr_user, role="DISABLED_ACCOUNT")

        db.session.add(user)
        db.session.commit()

    return True


def add_content(df, content, users):
    # loop through content, checking if value has been unblocked based on the dup list
    # get the duplicate values
    try:
        dup_removed = df.drop_duplicates(['incidentid'], keep="last")
    except:
        pass

    # get a list of usernames and ids from db
    temp_users = []
    for x in users:
        userid = User.query.filter_by(username=x).first()
        temp_users.append(userid)

    # use fillna to take care of possible errors
    dup_removed.fillna(value="na")

    for index, row in dup_removed.iterrows():
        # just assume this is the first time
        # get user id based on user name
        for stuff in temp_users:
            if (row['user'] == stuff.username):
                internal_id = stuff.id
        # convert timestamp to play nice with db
        timestamp_convert = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
        # check if blocked or not
        if (row['action'] == 'BLOCKED'):
            dmca_db_stuff = DmcaHistory(date_posted=timestamp_convert, offender_ip=row['privateip'],
                                        offender_mac=row['mac'], action=row['action'],
                                        classification=row['reasoncode'], case_id=row['description'],
                                        evidence=row['evidence'], internal_user_id=internal_id)

        else:
            dmca_db_stuff = DmcaHistory(date_posted=timestamp_convert, offender_ip=row['privateip'],
                                        offender_mac=row['mac'], action=row['action'],
                                        classification=row['reasoncode'], case_id=row['description'],
                                        evidence=row['evidence'], internal_user_id=internal_id,
                                        date_closed=timestamp_convert)
        # commit add
        db.session.add(dmca_db_stuff)
        db.session.commit()


def netmgr_import():
    # open sql file with correct encoding and seperate by each line
    with open('scripts/dmca_export_recent.sql', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    # prep arrays
    headers = []
    content = []

    users = []
    for i in lines:
        # extract the headers
        if (i.startswith('INSERT INTO')):
            if (len(headers) < 1):
                # clean and prep it once
                head = i[31:-8].replace('`', '').replace(' ', '')
                headers.append(head.split(','))
                lines.remove(i)

        else:
            # clean and prep each row
            prep = i[1:-2].replace('\'', '')
            content.append(prep.split(',\t'))

    # works!
    try:
        temp_head = ['incidentid', 'user', 'timestamp', 'privateip', 'mac', 'action', 'reasoncode', 'description',
                     'evidence']
        df = pd.DataFrame(content, columns=temp_head)
    except:
        df = pd.DataFrame.from_records(content, columns=headers)

    print(df.head())

    for j in content:
        # if(not('DMCABOT' in j[1])):
        users.append(j[1])

    # get the duplicate values
    try:
        temp_df = pd.concat(g for _, g in df.groupby("incidentid") if len(g) > 1)
    except:
        pass

    users = list(set(users))

    flag_result = False

    for k in users:
        if (not ('DMCABOT' in k)):
            flag_result = add_user(k)
        else:
            user = User(username=k, role="OLD_BOT")

            db.session.add(user)
            db.session.commit()

    add_content(df, content, users)

    return flag_result


def db_macFormat():
    # get the total number of entries in the dmca logs
    count = DmcaHistory.query.filter_by().count()
    entry_test = DmcaHistory.query.filter_by()
    
    for x in entry_test:
        test_re = re.fullmatch("^\S{4}\.\S{4}\.\S{4}$", x.offender_mac)
        if (not(x.offender_mac is None)) and (re.fullmatch("^\S{4}\.\S{4}\.\S{4}$", x.offender_mac)):
            mac = re.sub('[.:-]', '', x.offender_mac).lower()  # remove delimiters and convert to lower case
            mac = ''.join(mac.split())  # remove whitespaces

            # convert mac in canonical form (eg. 00:80:41:ae:fd:7e)
            mac = ":".join(["%s" % (mac[i:i + 2]) for i in range(0, 12, 2)])

            # commit changes
            x.offender_mac = mac

    db.session.commit()
            
            
