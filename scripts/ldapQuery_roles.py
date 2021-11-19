import ldap3
import os
import svc_config


def get_groupMembers(groups):
    users = []
    groups_dict = {}

    server = ldap3.Server('<ldap_server>')
    connection = ldap3.Connection(server, user=svc_config.svc_account, password=svc_config.svc_ps)
    connection.bind()

    # Verify search_base is correct depending on each group (aka, add elif statement)
    for group in groups:
        if group == "<groups>":
            connection.search(
                search_base=f'OU={group},<tenant_info>',
                search_filter='(objectClass=person)',
                search_scope='SUBTREE',
                attributes=['cn']
            )
        elif group == "<groups>":
            connection.search(
                search_base=f'CN={group},<tenant_info>',
                search_filter='(objectClass=group)',
                search_scope='SUBTREE',
                attributes=['member']
            )
        elif group == "<groups>":
            connection.search(
                search_base=f'CN={group},<tenant_info>',
                search_filter='(objectClass=group)',
                search_scope='SUBTREE',
                attributes=['member']
            )
        elif group == "<groups>":
            connection.search(
                search_base=f'CN={group},<tenant_info>',
                search_filter='(objectClass=group)',
                search_scope='SUBTREE',
                attributes=['member']
            )
        else:
            connection.search(
                search_base=f'CN={group},<tenant_info>',
                search_filter='(objectClass=group)',
                search_scope='SUBTREE',
                attributes=['member']
            )
        # Shouldn't have to change this below
        if group == "<groups>":
            # I believe I did this as to avoid having to make a new search for every user
            for entry in connection.response:
                users.append(entry["attributes"]["cn"])
        else:
            for entry in connection.entries:
                for member in entry.member.values:
                    if ",DC=mc," in member:
                        # tbh I kinda forgot what this was for. Maybe to filter out mc users that are in the ITS Staff OU on the AD side?
                        # use regex to get the first CN which "should" be the account name 
                        tetetetete=42
                    else:
                        connection.search(
                            search_base='<tenant_info>',
                            search_filter=f'(distinguishedName={member})',
                            attributes=[
                                'sAMAccountName'
                            ]
                        )

                        users += connection.entries[0].sAMAccountName.values

        users = list(set(users))
        groups_dict[group] = users

    return groups_dict

def main():
    #get the ldap members by group
    admins = ["<groups>"]
    interns = ["<groups>"]
    helpdesk = ["<groups>"]

    groups_blah = {"ADMIN": admins, "INTERN": interns, "HELPDESK": helpdesk}

    # NOTE: the file exes in the dir where the virtual enviorment is based in (so cybsec root dir for the vm) 
    os_dir = './static/ldap_roles/'

    #loop through the groups and query ldap based on them
    for key, val in groups_blah.items():
        #get the member list
        user_list = get_groupMembers(val)
        temp_list = []

        for i, j in user_list.items():
            temp_list.extend(j)

        temp_list = list(set(temp_list))

        os_path = os_dir + key + ".txt"

        # open/overwrite the file with the new data
        if (os.path.exists(os_path)):
            os.remove(os_path)
        try:
            os.makedirs(os_dir)
        except FileExistsError:
            # directory already exists
            pass

        with open(os_path, mode='w+', encoding='utf-8') as newfile:
            newfile.write('\n'.join(temp_list))

        # change permissions
        os.chmod(os_path, 0o775)


main()
