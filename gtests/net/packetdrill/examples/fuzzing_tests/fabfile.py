from __future__ import print_function  # used to ignore cariage return in print function (,end="")
from fabric.api import *
from fabric.operations import local

######################################################################
# $ fab -l               // list all possible tasks  
# $ fab save_all_values  // it will execute save_all_values task
# $ fab configure_mptcp  // Should be executed before each test
# $ fab restore_mptcp    // Should be executed after each test
# $ fab restore_all_values   // Should be executed at the end of all tests
# 
# Made by redward
#######################################################################

""" # These are environnemental variables
env.hosts=["localhost"] 
env.roledefs={"server":["webserver.local"],"workstation":["10.10.10.10"]}
env.user="hng"
env.password="password"
env.parallel=True
env.skip_bad_hosts=True
env.timeout=1
env.warn_only=True
"""
env.warn_only=True

# first step: saves all default data to sysctl_values.default file
@task
def save_all_values(): 
    #setup_user()
    #print("Hello World!: " + get_sysctl('net.mptcp.mptcp_enabled'))
    print("Saving all values in 'sysctl_values.default' file ...")
    print(local('sysctl -a > sysctl_values.default'))

# from: http://wwwx.cs.unc.edu/~sparkst/howto/network_tuning.php
def configure_core_only():
    #This sets the max OS receive buffer size for all types of connections.
    local("sysctl -w net.core.rmem_max=8388608")
    #This sets the max OS send buffer size for all types of connections.
    local("sysctl -w net.core.wmem_max=8388608")
    #This sets the default OS receive buffer size for all types of connections.
    local("sysctl -w net.core.rmem_default=65536") 
    #This sets the default OS send buffer size for all types of connections.   
    local("sysctl -w net.core.wmem_default=65536") 

def configure_tcp_only():
    local('sysctl -w net.ipv4.tcp_mem="8388608 8388608 8388608"') #default: 132324	176434	264648
    local('sysctl -w net.ipv4.tcp_rmem="4096 87380 8388608"') # default:    4096    87380	6291456
    local('sysctl -w net.ipv4.tcp_wmem="4096 65536 8388608"') #default:     4096    16384	4194304
   # local('sysctl -w net.ipv4.tcp_congestion_control = "coupled"' )

def configure_mptcp_only():
    local('sysctl -w net.mptcp.mptcp_checksum=1')
    local('sysctl -w net.mptcp.mptcp_debug=0')
    local('sysctl -w net.mptcp.mptcp_enabled=1') #be sure it's running
    local('sysctl -w net.mptcp.mptcp_ndiffports=2')
    local('sysctl -w net.mptcp.mptcp_path_manager=fullmesh')
    local('sysctl -w net.mptcp.mptcp_syn_retries=3')

@task
def configure_mptcp():
    import os.path
    if(os.path.isfile("sysctl_values.default")):
        #print("Configuring mptcp ...")
        configure_core_only()
        configure_tcp_only()
        configure_mptcp_only()
        #This will ensure that immediately subsequent connections use these values.
        local('sysctl -w net.ipv4.route.flush=1')   
    else:
        print("You should first save sysctl values: $ fab save_sysctl_values ")

@task 
def restore_mptcp():
    #print("Restoring mptcp values ...")
    with open("sysctl_values.default") as fd_def:
        for i, line in enumerate(fd_def.readlines()):
            n = line.split()
            
            # Core values restore from file
            if("net.core.rmem_max" == n[0]):
                local("sysctl -w net.core.rmem_max=" + n[2])
            if("net.core.wmem_max" == n[0]):
                local("sysctl -w net.core.wmem_max=" + n[2])                
            if("net.core.rmem_default" == n[0]):
                local("sysctl -w net.core.rmem_default=" + n[2])                 
            if("net.core.wmem_default" == n[0]):
                local("sysctl -w net.core.wmem_default=" + n[2])               
           
            # TCP option put back from file
            if("net.ipv4.tcp_mem" == n[0]):
                local('sysctl -w net.ipv4.tcp_mem="' + n[2] +' '+ n[3] +' '+ n[4] + '"')              
            if("net.ipv4.tcp_rmem" == n[0]):
                local('sysctl -w net.ipv4.tcp_rmem="' + n[2] +' '+ n[3] +' '+ n[4] + '"')                   
            if("net.ipv4.tcp_wmem" == n[0]):
                local('sysctl -w net.ipv4.tcp_wmem="' + n[2] +' '+ n[3] +' '+ n[4] + '"')
            
            # MPTCP values see http://multipath-tcp.org/pmwiki.php/Users/ConfigureMPTCP
            if("net.mptcp.mptcp_checksum" == n[0]):
                local("sysctl -w net.mptcp.mptcp_checksum=" + n[2])
            if("net.mptcp.mptcp_enabled" == n[0]):
                local("sysctl -w net.mptcp.mptcp_enabled=" + n[2])
            if("net.mptcp.mptcp_debug" == n[0]):
                local("sysctl -w net.mptcp.mptcp_debug=" + n[2])            
            if("net.mptcp.mptcp_ndiffports" == n[0]):
                local("sysctl -w net.mptcp.mptcp_ndiffports=" + n[2])
            if("net.mptcp.mptcp_path_manager" == n[0]):
                local("sysctl -w net.mptcp.mptcp_path_manager=" + n[2])
            if("net.mptcp.mptcp_syn_retries" == n[0]):
                local("sysctl -w net.mptcp.mptcp_syn_retries=" + n[2])

@task
def restore_all_values(): # last step
    print("\nRestoring all values ...")
    
    with open("sysctl_values.default") as fd_def:
        for i, line in enumerate(fd_def.readlines()):
            n = line.split()
            #print(n[0] + " "+n[1]+" : ", end=" ")
            vals = n[0]+n[1]+'"'
            for index in range(len(n)-2):
                vals += str(n[index+2])+' '
               # print(str(n[index+2]), end=" ")
            vals += '"'   
            if(n[0] != "dev.cdrom.info" and len(n)>2):
                local("sysctl -w " + vals)
    fd_def.close()

@task 
def create_tests():
    print("Creating file tests in automated_tests folder ...")

    #create folder it does not exist
    if not os.path.exists("automated_tests"): os.makedirs("automated_tests")

#    with open("sysctl_values.default") as fd_def:


