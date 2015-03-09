import gdata.apps.groups.client
groupClient = gdata.apps.groups.client.GroupsProvisioningClient(domain=domain)
groupClient.ClientLogin(email=email, password=password, source='apps')
groupClient.RetrieveAllMembers(group_id)
