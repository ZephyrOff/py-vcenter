# py-VCenter
## <ins>Prérequis</ins>
- Python 3
- Module Python 3:
   - pyVim
   - pyVmomi
   - sslyze
<br/>

***
## <ins>Connexion/Déconnexion</ins>
### Connexion
Avant toutes actions, il est nécessaire d'initialiser la classe Vcenter()

```python
vc = Vcenter(VCENTER_IP,ACCOUNT_USER,ACCOUNT_PASSWORD)
```

>En paramètre supplémentaire, nous pouvons mettre:<br/>
>- verbose = _True_ ou _False_   pour afficher le logs des actions<br/>
>- ssl_connection = _True_ ou _False_   pour lancer une connexion sécurisée ou non<br/>
>- ssl_protocol = ssl.PROTOCOL_TLSv1_2   pour spécifier le protocole utilisé<br/>
>- ssl_verify = ssl.CERT_NONE, ssl.CERT_OPTIONAL, ssl.CERT_REQUIRED   pour contrôler ou non le certificat<br/>

<kbd><samp>quitte si erreur</samp></kbd>
### Déconnexion
Pour se déconnecter, il suffit d'utiliser la fonction disconnect
```python
vc.disconnect()
```
<kbd><samp>retourne 1 si déconnecté, 0 si échec</samp></kbd>
<br/><br/>
## <ins>Snapshot</ins>
### Listing des snapshots existants
Pour récupérer la liste des snapshots de toutes les VM (aucun argument est nécessaire)<br/>
```python
vc.check_snapshots()
```

<details close>
<summary><kbd><samp>renvoie un tableau avec les informations</samp></kbd></summary>

* Nom de la VM
* Nom de l'OS
* Version
* Nom du snapshot
* Etat de la VM lors du snapshot
* Description
* Date de création

</details>

### Création de snapshot
Pour faire le snapshot d'une VM, lancer la fonction create_snapshot avec comme paramètre le nom de la VM
```python
vc.create_snapshot(vmname)
```
>En paramètre supplémentaire, nous pouvons mettre:<br/>
>- snap_name = Pour définir un nom au snapshot (Par défaut il prend le format "VmName - %d/%m/%Y - %H:%M:%S")
>- description = Pour définir la description du snapshot
>- dumpMemory = _True_ ou _False_  Permet d'ajouter le dump de la mémoire au snapshot (par défaut sur False)

<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
### Suppression de snapshot
Pour supprimer le snapshot d'une VM, lancer la fonction delete_snapshot avec comme paramètre le nom de la VM et la cible
```python
vc.delete_snapshot(vmname,target)
```
>En paramètre cible, plusieurs choix sont possibles:
>- target = _search_ ou _last_ ou _all_
>   * search: permet de cibler un snapshot spécifique
>   * last: supprime le dernier snapshot
>   * all: supprime tous les snapshots présent sur la VM
>- snapshot_name = Nom du snapshot   (si target sur search)
>- remove_subtree = _True_ ou _False_   pour prendre en compte les snapshots fils

<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
### Renommage de snapshot
```python
vc.rename_snapshot(vmname,snapshot_name)
```
>En paramètre, nous pouvons mettre:<br/>
>- name = pour définir un nouveau nom de snapshot
>- desc = pour définir une nouvelle description de snapshot

<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
### Rollback VM depuis un snapshot
Pour restaurer la configuration d'un VM à partir d'un snapshot
```python
vc.reload_snapshot(vmname,snapshot_name)
```

<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
<br/><br/>
## <ins>VM</ins>
### Démarrer une VM
```python
vc.boot_vm(vmname)
```
<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
### Arrêter une VM
```python
vc.shutdown_vm(vmname)
```
<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
### Redémarrer une VM
```python
vc.reboot_vm(vmname)
```
<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
### Mettre une VM en pause
```python
vc.suspend_vm(vmname)
```
<kbd><samp>retourne 1 si succès, 0 si échec ainsi que le message de retour</samp></kbd>
<br/><br/>
## <ins>Object</ins>
### Récupérer des informations de VM
Récupérer les informations d'une ou plusieurs VM sous forme de dictionnaire
```python
vc.get_vm_dict(vname)
```
<kbd><samp>retourne un dictionnaire</samp></kbd>
