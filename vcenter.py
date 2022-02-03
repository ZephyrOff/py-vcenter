#install pyVim
from pyVim.connect import SmartConnect, Disconnect
#install pyVmomi
from pyVmomi import vim,vmodl
#install sslyze
import ssl
from getpass import getpass
from datetime import datetime

import time

def bytes2human(n):
	symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
	prefix = {}
	for i, s in enumerate(symbols):
		prefix[s] = 1 << (i + 1) * 10
	for s in reversed(symbols):
		if n >= prefix[s]:
			value = float(n) / prefix[s]
			return '%.1f%s' % (value, s)
	return "%sB" % n

class Vcenter():
	def __init__(self,vcenter_ip,vcuser,vcpwd,verbose=False,ssl_connection=True,ssl_protocol=ssl.PROTOCOL_TLSv1_2,ssl_verify=ssl.CERT_NONE):
		self.vcenter_ip = vcenter_ip
		self.vcuser = vcuser
		self.verbose=verbose

		if ssl_connection==True:
			context = ssl.SSLContext(ssl_protocol)
			context.verify_mode = ssl_verify
			#context.verify_mode = ssl.CERT_OPTIONAL
			#context.verify_mode = ssl.CERT_REQUIRED
		else:
			context = ssl._create_unverified_context()

		try:
			self.vcenter_con = SmartConnect(host=self.vcenter_ip,user=self.vcuser,pwd=vcpwd,sslContext=context)
		except:
			self.print_verbose("Connection failed")
			exit()

	def disconnect(self):
		if hasattr(self, 'vcenter_con'):
			Disconnect(self.vcenter_con)

	def wait_for_task(self,task, actionName='job', hideResult=False):
		try:
			time.sleep(0.5)
			while task.info.state == vim.TaskInfo.State.running:
				time.sleep(1)

			if task.info.state == vim.TaskInfo.State.success or task.info.state == vim.TaskInfo.State.queued:
				if task.info.result is not None and not hideResult:
					out = '%s completed successfully, result: %s' % (actionName, task.info.result)
					self.print_verbose(out)
				else:
					out = '%s completed successfully.' % actionName
					self.print_verbose(out)
				return 1, task.info.result
			else:
				out = '%s did not complete successfully: %s' % (actionName, task.info.error)
				self.print_verbose(out)
				return 0, task.info.result

		except:
			return 0, task.info.error

	def print_verbose(self,msg):
		if self.verbose:
			print(msg)

	#Return object of one VM
	def get_obj(self,name):  
		obj = None
		container = self.vcenter_con.content.viewManager.CreateContainerView(self.vcenter_con.content.rootFolder,[vim.VirtualMachine],True)
		for c in container.view:
			if c.name == name:
				obj = c
				break
		return obj

	#Return list of all snapshots
	def check_snapshots(self):
		try:
			result = []

			for data in self.vcenter_con.content.viewManager.CreateContainerView(self.vcenter_con.content.rootFolder,[vim.VirtualMachine],True).view:
				if data.snapshot:
					for snap in data.snapshot.rootSnapshotList:
						result.append([data.snapshot.currentSnapshot.config.name,data.snapshot.currentSnapshot.config.guestFullName,data.snapshot.currentSnapshot.config.version,snap.name,snap.state,snap.description,snap.createTime.strftime("%d/%m/%Y (%H:%M:%S)")])
			return result
		except:
			self.print_verbose("Check_snapshots: Error with informations data")

	#Create snapshot of specific VM  return: 1 if ok, or 0 if error
	def create_snapshot(self,vmname,snap_name=None, description="", dumpMemory=False):
		vm = self.get_obj(vmname)

		if vm!=None:
			quiesce = True

			if snap_name==None:
				Obj = datetime.now()
				date = Obj.strftime("%d/%m/%Y - %H:%M:%S")
				snap_name = vmname + " - " + date

			self.print_verbose("Creating Snapshot...")
			task = vm.CreateSnapshot(snap_name, description, dumpMemory, quiesce)
			status_code, result = self.wait_for_task(task, self.vcenter_con)

			if status_code==1:
				self.print_verbose(f"Snapshot Created: {result}")
				return 1, f"Snapshot Created: {result}"
			else:
				if result!=None:
					self.print_verbose(f"Error with snapshot creation: {result}")
					return 0, f"Error with snapshot creation: {result}"
				else:
					self.print_verbose(f"Error with snapshot creation")
					return 0, f"Error with snapshot creation"
		else:
			self.print_verbose(f"No VMs found")
			return 0, f"No VMs found"


	#Job for delete specific snapshot
	def del_snap(self,snap_obj,remove_subtree):
		self.print_verbose(f"Removing snapshot {snap_obj}")
		task = snap_obj.RemoveSnapshot_Task(remove_subtree)
		status_code, result = self.wait_for_task(task, self.vcenter_con)

		if status_code==1:
			self.print_verbose(f"Snapshot {snap_obj} Deleted")
			return 1, f"Snapshot {snap_obj} Deleted"
		else:
			if result!=None:
				self.print_verbose(f"Error with snapshot deletion: {result}")
				return 0, f"Error with snapshot deletion: {result}"
			else:
				self.print_verbose(f"Error with snapshot deletion")
				return 0, f"Error with snapshot deletion"

	#Delete snapshot of specific VM  (search, last or all)
	def delete_snapshot(self,vmname,target='last',snapshot_name=None, remove_subtree=False):
		vm = self.get_obj(vmname)

		if vm!=None:
			snapshots = vm.snapshot.rootSnapshotList

			if target=='search' and snapshot_name!=None:	
				for snapshot in snapshots:
					child=1
					while child==1:
						if snapshot_name == snapshot.name:
							snap_obj = snapshot.snapshot
							status_code, msg = self.del_snap(snap_obj,remove_subtree)

							return status_code, msg
						else:
							if snapshot.childSnapshotList:
								snapshot = snapshot.childSnapshotList.pop()
							else:
								child=0

			elif target=='last':
				snapshot = snapshots.pop()
				while snapshot.childSnapshotList:
					snapshot = snapshot.childSnapshotList.pop()

				snap_obj = snapshot.snapshot
				status_code, msg = self.del_snap(snap_obj,remove_subtree)

				return status_code, msg

			elif target=='all':
				pipe = []
				return_code = 1
				for snapshot in snapshots:
					child=1
					while child==1:
						snap_obj = snapshot.snapshot
						status_code, msg = self.del_snap(snap_obj,remove_subtree)
						pipe.append([status_code,msg])
						if status_code==0:
							return_code = 0
						if snapshot.childSnapshotList:
							snapshot = snapshot.childSnapshotList.pop()
						else:
							child=0
				return return_code, pipe
		else:
			self.print_verbose(f"No VMs found")
			return 0, "No VMs found"

	#Rename snapshot of specific VM
	def rename_snapshot(self,vmname,snapshot_name, Name=None, Desc=None):
		vm = self.get_obj(vmname)

		if vm!=None:
			snapshots = vm.snapshot.rootSnapshotList

			for snapshot in snapshots:
				child=1
				while child==1:
					if snapshot_name == snapshot.name:
						snap_obj = snapshot.snapshot
						if Name == None:
							Name = snapshot.name
						if Desc == None:
							Desc = snapshot.description

						self.print_verbose(f"Rename snapshot {snap_obj}")
						snap_obj.RenameSnapshot(Name,Desc)

						return 1, f"Snapshot renamed"

					if snapshot.childSnapshotList:
						snapshot = snapshot.childSnapshotList.pop()
					else:
						child=0
		else:
			self.print_verbose(f"No VMs found")
			return 0, "No VMs found"

	#Restore VM with a snapshot
	def reload_snapshot(self,vmname,snapshot_name):
		vm = self.get_obj(vmname)

		if vm!=None:
			snapshots = vm.snapshot.rootSnapshotList

			for snapshot in snapshots:
				child=1
				while child==1:
					if snapshot_name == snapshot.name:
						snap_obj = snapshot.snapshot

						self.print_verbose(f"Reverting snapshot {snap_obj}")
						task = snap_obj.RevertToSnapshot_Task()
						status_code, result = self.wait_for_task(task, self.vcenter_con)

						if status_code==1:
							self.print_verbose(f"Snapshot Reverted")
							return 1, "Snapshot Reverted"
						else:
							if result!=None:
								self.print_verbose(f"Error with snapshot reversion: {result}")
								return 0, f"Error with snapshot reversion: {result}"
							else:
								self.print_verbose(f"Error with snapshot reversion")
								return 0, "Error with snapshot reversion"

					if snapshot.childSnapshotList:
						snapshot = snapshot.childSnapshotList.pop()
					else:
						child=0
		else:
			self.print_verbose(f"No VMs found")
			return 0, "No VMs found"
		return 0

	#Suspend VM
	def suspend_vm(self,vmname):
		vm = self.get_obj(vmname)

		if vm!=None:
			self.print_verbose(f"Suspend {vmname}")
			task = vm.SuspendVM_Task()

			status_code, result = self.wait_for_task(task, self.vcenter_con)
			if status_code==1:
				self.print_verbose(f"VM Suspend")
				return 1, "VM Suspend"
			else:
				if result!=None:
					self.print_verbose(f"Error suspend VM: {result}")
					return 0, f"Error suspend VM: {result}"
				else:
					self.print_verbose(f"Error suspend VM")
					return 0, "Error suspend VM"
		else:
			self.print_verbose(f"No VMs found")
			return 0, "No VMs found"

	#PowerOn VM
	def boot_vm(self,vmname):
		vm = self.get_obj(vmname)

		if vm!=None:
			self.print_verbose(f"Boot {vmname}")
			task = vm.PowerOnVM_Task()

			status_code, result = self.wait_for_task(task, self.vcenter_con)
			if status_code==1:
				self.print_verbose(f"VM Started")
				return 1, "VM Started"
			else:
				if result!=None:
					self.print_verbose(f"Error boot VM: {result}")
					return 0, f"Error boot VM: {result}"
				else:
					self.print_verbose(f"Error boot VM")
					return 0, "Error boot VM"
		else:
			self.print_verbose(f"No VMs found")
			return 0, "No VMs found"
	
	#PowerOff VM
	def shutdown_vm(self,vmname):
		vm = self.get_obj(vmname)

		if vm!=None:
			self.print_verbose(f"Shutdown {vmname}")
			task = vm.PowerOffVM_Task()

			status_code, result = self.wait_for_task(task, self.vcenter_con)
			if status_code==1:
				self.print_verbose(f"VM Shutdown")
				return 1, "VM Shutdown"
			else:
				if result!=None:
					self.print_verbose(f"Error shutdown VM: {result}")
					return 0, f"Error shutdown VM: {result}"
				else:
					self.print_verbose(f"Error shutdown VM")
					return 0, "Error shutdown VM"
		else:
			self.print_verbose(f"No VMs found")
			return 0, "No VMs found"

	#Reboot VM
	def reboot_vm(self,vmname):
		vm = self.get_obj(vmname)

		if vm!=None:
			self.print_verbose(f"Reboot {vmname}")
			task = vm.ResetVM_Task()

			status_code, result = self.wait_for_task(task, self.vcenter_con)
			if status_code==1:
				self.print_verbose(f"VM Rebooted")
				return 1, "VM Rebooted"
			else:
				if result!=None:
					self.print_verbose(f"Error reboot VM: {result}")
					return 0, f"Error reboot VM: {result}"
				else:
					self.print_verbose(f"Error reboot VM")
					return 0, "Error reboot VM"
		else:
			self.print_verbose(f"No VMs found")
			return 0, "No VMs found"

	#Get informations (in a dictionary) of a specific VM
	def get_vm_dict(self,vname):
		vms = {}

		for data in self.vcenter_con.content.viewManager.CreateContainerView(self.vcenter_con.content.rootFolder,[vim.VirtualMachine],True).view:
			if vname in data.name:
				vms[data.name]={}

				if data.summary and data.summary.config:
					vms[data.name]['INFORMATIONS']={}
					if data.summary.config.name:
						vms[data.name]['INFORMATIONS']['VM Name']=data.summary.config.name
					if data.summary.config.annotation:
						vms[data.name]['INFORMATIONS']['Description']=data.summary.config.annotation
					if data.summary.config.guestFullName:
						vms[data.name]['INFORMATIONS']['Version OS']=data.summary.config.guestFullName
					if data.summary.config.numCpu:
						vms[data.name]['INFORMATIONS']['NbCPU']=data.summary.config.numCpu
					if data.summary.config.memorySizeMB:
						vms[data.name]['INFORMATIONS']['Memory']=bytes2human(data.summary.config.memorySizeMB*1048576)

				if data.runtime:
					vms[data.name]['STATUS']={}
					if data.runtime.powerState:
						vms[data.name]['STATUS']['Status']=data.runtime.powerState
					if data.runtime.bootTime:
						vms[data.name]['STATUS']['BootTime']=data.runtime.bootTime.strftime("%d-%b-%Y (%H:%M:%S)")
					if data.runtime.paused:
						vms[data.name]['STATUS']['Paused']=data.runtime.paused
					if data.runtime.suspendTime:
						vms[data.name]['STATUS']['SuspendTime']=data.runtime.suspendTime.strftime("%d-%b-%Y (%H:%M:%S)")
					if data.runtime.snapshotInBackground:
						vms[data.name]['STATUS']['SnapshotBackground']=data.runtime.snapshotInBackground

				if data.guest and data.guest.net:
					vms[data.name]['NETWORK']={}
					n = 0
					for net in data.guest.net:
						n+=1
						if net.network:
							network_name = net.network
						else:
							network_name = "network"+str(n)

						vms[data.name]['NETWORK'][network_name]={}
						if net.connected:
							vms[data.name]['NETWORK'][network_name]['Connected']=net.connected
						if net.macAddress:
							vms[data.name]['NETWORK'][network_name]['Mac Address']=net.macAddress
						if net.dnsConfig and net.dnsConfig.domainName:
							vms[data.name]['NETWORK'][network_name]['DomainName']=net.dnsConfig.domainName
						if net.dnsConfig and net.dnsConfig.dhcp:
							vms[data.name]['NETWORK'][network_name]['DHCP']=net.dnsConfig.dhcp

						if net.ipAddress:
							ip_array = []
							for ip in net.ipAddress:
								ip_array.append(ip)
							vms[data.name]['NETWORK'][network_name]['Ip']=ip_array

						if net.dnsConfig and net.dnsConfig.ipAddress:
							dns_array = []
							for dns in net.dnsConfig.ipAddress:
								dns_array.append(dns)
							vms[data.name]['NETWORK'][network_name]['DNS']=dns_array
				
				vms[data.name]['STORAGE']={}
				if data.storage and data.storage.perDatastoreUsage:
					datastore_array = []
					for datastore in data.storage.perDatastoreUsage:
						if datastore.datastore:
							datastore_array.append(datastore.datastore)
					if len(datastore_array)>0:
						vms[data.name]['STORAGE']['Datastore']=datastore_array

				if data.guest and data.guest.disk:
					disk_array = []
					for disk in data.guest.disk:
						if disk.diskPath and disk.freeSpace and disk.capacity:
							disk_array.append([disk.diskPath,bytes2human(disk.freeSpace),bytes2human(disk.capacity)])
						elif disk.diskPath:
							disk_array.append([disk.diskPath,'N.A','N.A'])
					if len(disk_array)>0:
						vms[data.name]['STORAGE']['Disk']=disk_array

				if data.snapshot:
					vms[data.name]['SNAPSHOT']={}
					num=0
					snap_array = {}
					for snap in data.snapshot.rootSnapshotList:

						child=1
						while child==1:
							num+=1
							snap_array[num] = {}
							if snap.name:
								snap_array[num]['Name'] = snap.name
							if snap.createTime:
								snap_array[num]['CreateTime'] = snap.createTime.strftime("%d/%b/%Y (%H:%M:%S)")
							if snap.state:
								snap_array[num]['State'] = snap.state
							if snap.description:
								snap_array[num]['Description'] = snap.description

							if snap.childSnapshotList:
								snap = snap.childSnapshotList.pop()
							else:
								child=0

					if len(snap_array)>0:
						vms[data.name]['SNAPSHOT']=snap_array
		return vms
