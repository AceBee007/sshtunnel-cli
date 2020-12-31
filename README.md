# sshtunnel-cli
a simple ssh tunnel client program wrote in python3


I AM TOO LAZY TO MAKE THIS PICE OF S..T

## USAGE

First of all, fill the DEFAULT information

edit the `sshtunnel.py`

```python
DEFAULT_RELAY_SERVER  = '' # relay server's IP or domain, At most of time, It is a public address
DEFAULT_RELAY_USER    = '' # relay server's username, the user exist on relay server
DEFAULT_RELAY_AUTH    = '' # authentication information, if you use a private.key, leave it as '-i {~/.ssh/path/to/private.key}'
                           # if you use a password string, just leave it as it should be
ALIAS = {
        # 'Remote Host Label' : ('remote host, domain name or ip', 'remote host port')
        'jupyter':('192.168.1.20', '8888'),
        'tb':('tensorboard.example.net','6006'),
}
```
 
### check status tunnel
```
python3 sshtunnel.py
```

### make tunnel
```
python3 sshtunnel.py -rmh LABEL
```
This will create a port fowarding from remotehost:port to localhost:port using relay server, the remotehost information is defined in ALIAS

### make tunnel with specified local port
```
python3 sshtunnel.py -rmh LABEL -lp 12345
```
This will create a port fowarding from remotehost:port to localhost:12345 using relay server, the remotehost information is defined in ALIAS

### make tunnel with specified remotehost port
```
python3 sshtunnel.py -rmh LABEL -rmp 23456
```
This will create a port fowarding from remotehost:23456 to localhost:port using relay server, the remotehost information is defined in ALIAS, but the remotehost port will be over writen.

or
```
python3 sshtunnel.py -rmh {remotehost_domain_or_ip} -rmp 23456
```
This will create a port fowarding from {remotehost_domain_or_ip}:23456 to localhost:port using default relay server
### close tunnel
```
python3 sshtunnel.py -m kill<Enter>
```
and you will have 4 options
```
Cancel:		-->"" (Leave empty)
Close one:	-->{pid or local_port}
Close several:	-->{pid1} {pid2} {local_port1}...(space split)
Close all:	-->"all"
```
Leave empty to cancel the action, type one or several pid or local_port used for tunnel, type "all" to close all the tunnel.
