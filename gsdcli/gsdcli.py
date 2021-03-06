import os
import yaml 
import click
import getpass
import urllib.request

@click.group()
def gsdcli():
    pass

@gsdcli.command()
@click.argument('name')
def install(name):
    serverObj = parseSupported(name)

    if not os.path.exists(serverObj.get('install-path')):
        createDirectories(serverObj)
    createLaunchScript(serverObj)
    createUnitFile(serverObj)

    if serverObj.get('backend') == 'srdcs':
        srdcsInstall(serverObj)
    elif serverObj.get('backend') == 'scp':
        steamCmdInstall(serverObj)
        urllib.request.urlretrieve('https://github.com/Grover-c13/MultiAdmin/releases/download/3.2.5/MultiAdmin.exe', f"{serverObj.get('install-path')}/MultiAdmin.exe")
    elif serverObj.get('backend') == 'unity':
        steamCmdInstall(serverObj)
        urllib.request.urlretrieve('https://github.com/Grover-c13/MultiAdmin/releases/download/3.2.5/MultiAdmin.exe', f"{serverObj.get('install-path')}/MultiAdmin.exe")
    else:
        exit(f"{serverObj.get('backend')} not supported yet.")

##### Private Functions #####

def parseSupported(name):
    serverYaml = open(f'{os.path.dirname(__file__)}/_servers.yaml')
    serverList = yaml.load(serverYaml, Loader=yaml.FullLoader)
    serverObj = serverList.get(name)
    if serverObj :
        configureMetadata(name, serverObj)
        return serverObj
    else:
        exit(f'{name} Not supported')

def configureMetadata(name, serverObj):
    serverObj.update({'friendly-name' : name})
    serverObj.update({'user' : getpass.getuser()})
    serverObj.update({'install-path' : f'{os.path.expanduser("~")}/{name}-server'})
    serverObj.update({'systemd-path' : f'{os.path.expanduser("~")}/.config/systemd/user'})
    serverObj.update({'dryrun' : 'ye'})

def createDirectories(serverObj):
    print('Creating prerequisite directories...')
    os.mkdir(serverObj.get('install-path'))
    if not os.path.exists(serverObj.get('systemd-path')):
        os.mkdir(serverObj.get('systemd-path'))

def createLaunchScript(serverObj):
    print('Creating launch script...')
    launchFilePath = f"{serverObj.get('install-path')}/launch.sh"
    if os.path.exists(launchFilePath):
        os.rename(launchFilePath, f"{launchFilePath}.backup")
    launchFile = open(launchFilePath, "w+")
    launchFile.write(serverObj.get('launchParams'))
    launchFile.close()

def createUnitFile(serverObj):
    print('Creating unit file...')
    unitFilePath = f"{serverObj.get('systemd-path')}/{serverObj.get('friendly-name')}.service"
    if os.path.exists(unitFilePath):
        os.rename(unitFilePath, f"{unitFilePath}.backup")
    launchFile = open(unitFilePath, "w+")
    launchFile.write(f"[Unit]\nAfter=network.target\nDescription=Daemon for {serverObj.get('friendly-name')} dedicated server\n[Install]\nWantedBy=default.target\n[Service]\nType=simple\nWorkingDirectory={serverObj.get('install-path')}\nExecStart=/bin/bash {serverObj.get('install-path')}/launch.sh")
    launchFile.close()

def steamLoginParser(serverObj):
    if not serverObj.get('steamUserName'):
        serverObj.update({'steamUserName' : 'anonymous'})
        serverObj.update({'steamPassword' : ''})
    return f"+login {serverObj.get('steamUserName')} {serverObj.get('steamPassword')}"

def steamCmdInstall(serverObj):
    steamLogin = steamLoginParser(serverObj)
    installCmd = f"{steamLogin} +force_install_dir {serverObj.get('install-path')} +app_update {serverObj.get('appId')} validate +quit"
    os.system(f'steamcmd {installCmd}')

def srdcsInstall(serverObj):
    steamCmdInstall(serverObj)
    logFilePath = f"{serverObj.get('install-path')}/{serverObj.get('name')}/console.log"
    launchFilePath = f"{serverObj.get('install-path')}/launch.sh"

    logFile = open(logFilePath, 'a')
    logFile.close()
    
    launchFile = open(launchFilePath, 'a')
    launchFile.write(f"\ntail -f {logFilePath}")
    launchFile.close()

def unityHandler(serverObj):
    if serverObj.get('name') == 'rust':
        pass
    elif serverObj.get('name') == 'sdtd':
        pass

if __name__ == "__main__":
    # For Snapcraft
    gsdcli()
