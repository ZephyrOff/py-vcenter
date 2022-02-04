import vcenter
from getpass import getpass
from color import fg,bg,attr

#Display informations of specific VM
def get_vm_info(vc,vname):
	result = vc.get_vm_dict(vname)

	for obj in result:
		if len(result)>1:
			print("\n")

		if "INFORMATIONS" in result[obj]:
			print("\n--- %sINFORMATIONS%s ---" % (fg(245),attr('reset')))
			data = result[obj]['INFORMATIONS']
			if "VM Name" in data:
				print(" VM Name: {}".format(data['VM Name']))
			if "Description" in data:
				print(" Description: {}".format(data['Description']))
			if "Version OS" in data:
				print(" Version OS: {}".format(data['Version OS']))
			if "NbCPU" in data:
				print(" NbCPU: {}".format(data['NbCPU']))
			if "Memory" in data:
				print(" Memory: {}".format(data['Memory']))

		if "STATUS" in result[obj]:
			data = result[obj]['STATUS']
			print("\n--- %sSTATUS%s ---" % (fg(245),attr('reset')))
			if "Status" in data:
				print(" Status: {}".format(data['Status']))
			if "BootTime" in data:
				print(" BootTime: {}".format(data['BootTime']))
			if "Paused" in data:
				print(" Paused: {}".format(data['Paused']))
			if "SuspendTime" in data:
				print(" SuspendTime: {}".format(data['SuspendTime']))
			if "SnapshotBackground" in data:
				print(" SnapshotBackground: {}".format(data['SnapshotBackground']))

		if "NETWORK" in result[obj]:
			data = result[obj]['NETWORK']
			print("\n--- %sNETWORK%s ---" % (fg(245),attr('reset')))
			for net in result[obj]['NETWORK']:
				print(" Network: {}".format(net))
				net = result[obj]['NETWORK'][net]
				if "Connected" in net:
					print(" Connected: {}".format(net['Connected']))
				if "Mac Address" in net:
					print(" Mac Address: {}".format(net['Mac Address']))
				if "DomainName" in net:
					print(" DomainName: {}".format(net['DomainName']))
				if "DHCP" in net:
					print(" DHCP: {}".format(net['DHCP']))

				if "Ip" in net:
					print(" Ip Address:")
					for ip in net['Ip']:
						print("	- {}".format(ip))
				if "DNS" in net:
					print(" DNS Address:")
					for dns in net['DNS']:
						print("	- {}".format(dns))
		
		if "STORAGE" in result[obj]:
			data = result[obj]['STORAGE']
			print("\n--- %sSTORAGE%s ---" % (fg(245),attr('reset')))
			if "Datastore" in data:
				print(" Datastore:")
				for datastore in data['Datastore']:
					print("	- {}".format(datastore))

			if "Datastore" in data:
				print(" Disk:")
				for disk in data['Disk']:
					if disk[1]!='N.A' and disk[2]!='N.A':
						print("	- {} ({}/{})".format(disk[0],disk[1],disk[2]))
					else:
						print("	- {}".format(disk[0]))

		print("\n--- %sSNAPSHOT%s ---" % (fg(245),attr('reset')))
		if "SNAPSHOT" in result[obj]:
			data = result[obj]['SNAPSHOT']
			for snap in data:
				if snap>1:
					print("")
				print(" Snap N°{}".format(snap))
				snap = data[snap]
				if "Name" in snap:
					print("   Name: {}".format(snap['Name']))
				if "CreateTime" in snap:
					print("   CreateTime: {}".format(snap['CreateTime']))
				if "State" in snap:
					print("   State: {}".format(snap['State']))
				if "Description" in snap:
					print("   Description: {}".format(snap['Description']))
		else:
			print("No Snapshot Found")


vc = vcenter.Vcenter(VCENTER_IP,ACCOUNT_USERNAME,getpass('\tPassword:'))
get_vm_info(vc,VMNAME)
