import subprocess
import argparse
import re

DEFAULT_RELAY_SERVER  = '' # relay server's IP or domain, At most of time, It is a public address
DEFAULT_RELAY_USER    = '' # relay server's username, the user exist on relay server
DEFAULT_RELAY_AUTH    = '' # authentication information, if you use a private.key, leave it as '-i {~/.ssh/path/to/private.key}'
                           # if you use a password string, just leave it as it should be

ALIAS = {
        # 'Remote Host Label' : ('remote host, domain name or ip', 'remote host port')
        'jupyter':('192.168.1.20', '8888'),
        'tb':('tensorboard.example.net','6006'),
        }


def run_command(command, **kwarg):
    out = subprocess.run(command, **kwarg,encoding='utf-8', stdout=subprocess.PIPE).stdout
    return out
    
    
def make_connection(args):
    if args.remote_host is None:
        print('Need a remote_host! (Use --remote_host {hostname}/{ALIAS})')
        exit()
    elif args.remote_host in ALIAS:
        remote_host = ALIAS[args.remote_host][0]
        remote_port = ALIAS[args.remote_host][1]
    else:
        remote_host = args.remote_host
        remote_port = None
    if remote_port is None:
        if args.remote_port is None:
            print('Need a remote_port')
            exit()
        else:
            remote_port = args.remote_port
    else:
        if args.remote_port is not None and remote_port != int(args.remote_port):
            remote_port = int(args.remote_port)
    if args.relay_ssh_port is None:
        relay_ssh_port = ''
    else:
        print('Relay server is using port:{} for ssh connection.'.format(args.relay_ssh_port))
        relay_ssh_port = '-p {} '.format(args.relay_ssh_port)
    if args.relay_auth[:2] == '-i':
        to_relay = 'ssh {}{} {}@{}'.format(relay_ssh_port, args.relay_auth, args.relay_user, args.relay_server)
    else:
        to_relay = 'sshpass -p {} ssh {}{}@{}'.format(args.relay_auth, relay_ssh_port, args.relay_user, args.relay_server)
    if args.local_port is None:
        for i in range(12000, 20000):
            if i not in localhost_port_in_use:
                local_port = i
                break
    elif int(args.local_port) not in localhost_port_in_use:
        local_port = args.local_port
    else:
        for i in range(int(args.local_port), 65535):
            if i not in localhost_port_in_use:
                local_port = i
                break
        print('The port:{} is in use, use {} instead'.format(args.local_port, local_port))

    for _,exist_port,exist_remote in get_exist_connection():
        if '{}:{}'.format(remote_host, remote_port) == exist_remote:
            print(exist_remote, 'is already connected!')
            print('\nAccessing:\nhttp://localhost:{}\n'.format(exist_port))
            exit()

    fowarding_command = f'{to_relay} -fNL {local_port}:{remote_host}:{remote_port}'
    if args.mode == 'state':
        print('$ {}'.format(fowarding_command))
    tmp = run_command(fowarding_command, shell=True)
    print('Mapping {}:{} -->> ({}@{}) -->> localhost:{}'.format(remote_host, remote_port, args.relay_user, args.relay_server, local_port))
    print('\nAccessing:\nhttp://localhost:{}\n'.format(local_port))

def get_exist_connection():
    tmp = [i for i in run_command('ps -ax | grep ssh', shell=True).split('\n') if 'ps -ax' not in i and '-fN' in i]
    res = []
    for i in tmp:
        pid = i[:i.find(' ??')]
        tunnel = i[i.find('-fNL')+5:]
        l = tunnel[:tunnel.find(':')]
        remote = tunnel[tunnel.find(':')+1:]
        res.append((pid, l, remote))
    return res


def show_tunnels():
    res = [i for i in run_command('ps -ax | grep ssh', shell=True).split('\n') if 'ps -ax' not in i and '-fN' in i]
    res = get_exist_connection()
    if not res:
        print('NO TUNNEL IS RUNNING!')
    else:
        for i in res:
            print(i)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='specify some info')

    parser.add_argument('-m',   '--mode', default='state')
    parser.add_argument('-lp',  '--local_port', default=None)
    parser.add_argument('-rmp', '--remote_port', default=None)
    parser.add_argument('-rmh', '--remote_host', default=None)
    parser.add_argument('-rls', '--relay_server', default=DEFAULT_RELAY_SERVER)
    parser.add_argument('-rlu', '--relay_user', default=DEFAULT_RELAY_USER)
    parser.add_argument('-rla', '--relay_auth', default=DEFAULT_RELAY_AUTH)
    parser.add_argument('-rsp', '--relay_ssh_port', default=None)
    args = parser.parse_args()

    ip_port_pattern = '127\.0\.0\.1\.[0-9]{1,5}'
    localhost_port_in_use = set()
    for i in run_command('netstat -natp tcp | grep 127.0.0.1 | grep LISTEN', shell=True).split('\n'):
        search_res = re.search(ip_port_pattern, i)
        if search_res is None:
            continue
        span = search_res.span()
        localhost_port_in_use.add(int(i[span[0]:span[1]][10:]))

    if args.mode == 'kill':
        while True:
            show_tunnels()
            command = input('Which tunnel do you want to shutdown? \nCancel:\t\t-->"" (Leave empty)\nClose one:\t-->{pid}\nClose several:\t-->{pid1} {pid2} {local_port1}...(space split)\nClose all:\t-->"all"\n--------> ')
            if command == '':
                print('Cancelling')
                break
            elif command.lower() == 'all':
                print('Closing all connection!')
                for pid_to_kill, _, _ in get_exist_connection():
                    run_command('kill {}'.format(pid_to_kill), shell=True)

            elif ' ' in command:
                memo = {}
                for pid, lp, _ in get_exist_connection():
                    memo[pid] = pid
                    memo[lp] = pid
                for pid_or_port in command.split(' '):
                    if pid_or_port in memo:
                        run_command('kill {}'.format(memo[pid_or_port]), shell=True)
            else:
                memo = {}
                for pid, lp, _ in get_exist_connection():
                    memo[pid] = pid
                    memo[lp] = pid
                if command in memo:
                    run_command('kill {}'.format(memo[command]), shell=True)

        pass
    elif args.mode == 'state':
        print('Port in use:',localhost_port_in_use)
        show_tunnels()
        make_connection(args)
    elif args.mode == 'silent':
        make_connection(args)

