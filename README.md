# Wrapper VCenter
## Connexion/Deconnexion
### Connexion
Avant toutes actions, il est nécessaire d'initialiser la classe Vcenter()

`` `py
vc = Vcenter(VCENTER_IP,ACCOUNT_USER,ACCOUNT_PASSWORD)
`` ''

En paramètre supplémentaire, nous pouvons mettre:<br/>
- verbose = _True_ ou _False_   <span style="color:red">pour afficher le logs des actions</span><br/>
- ssl_connection = _True_ ou _False_   <span style="color: #DBDBDB">pour lancer une connexion sécurisée ou non</span><br/>
- ssl_protocol = ssl.PROTOCOL_TLSv1_2   <span style="color: #DBDBDB">pour spécifier le protocole utilisé</span><br/>
- ssl_verify = ssl.CERT_NONE   <span style="color: #DBDBDB">pour contrôler ou non le certificat</span><br/>

### Deconnexion
Pour se déconnecter, il suffit d'utiliser la fonction disconnect
```vc.disconnect()```

## Snapshot
### Listing des snapshots existants
Pour récupérer la liste des snapshots de toutes les VM (aucun argument est nécessaire)<br/>
```check_snapshots()```
La fonction renvoie un tableau avec les informations suivantes:
- Nom de la VM
- Nom de l'OS
- Version
- Nom du snapshot
- Etat de la VM lors du snapshot
- Description
- Date de création
### Création de snapshot
```create_snapshot(vmname,snap_name=None, description="", dumpMemory=False)```
### Suppression de snapshot
```delete_snapshot(vmname,target='last',snapshot_name=None, remove_subtree=False)```
### Renommage de snapshot
```rename_snapshot(vmname,snapshot_name, Name=None, Desc=None)```
### Rollback VM depuis un snapshot
```reload_snapshot(vmname,snapshot_name)```

## VM
### Mettre une VM en pause
```suspend_vm(vmname)```
### Démarrer une VM
```boot_vm(vmname)```
### Arrêter une VM
```shutdown_vm(vmname)```
### Redémarrer une VM
```reboot_vm(vmname)```

## Object
### Récupérer des informations sur des VM
```get_vm_dict(vname)```
