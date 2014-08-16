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
    local("sysctl -w net.core.rmem_max=212992") #  8388608
    #This sets the max OS send buffer size for all types of connections.
    local("sysctl -w net.core.wmem_max=212992")
    #This sets the default OS receive buffer size for all types of connections.
    local("sysctl -w net.core.rmem_default=212992") 
    #This sets the default OS send buffer size for all types of connections.   
    local("sysctl -w net.core.wmem_default=212992") 

def configure_tcp_only():
    local('sysctl -w net.ipv4.tcp_mem="132324	176434 	264648"') #default: 132324	176434	264648
    local('sysctl -w net.ipv4.tcp_rmem="4096    87380 6291456"') # default:    4096    87380	6291456
    local('sysctl -w net.ipv4.tcp_wmem="4096	16384 4194304"') #default:     4096    16384	4194304
	# local('sysctl -w net.ipv4.tcp_window_scaling="0"')
   	# local('sysctl -w net.ipv4.tcp_congestion_control = "coupled"' )

def configure_mptcp_only():
    local('sysctl -w net.mptcp.mptcp_checksum=1')
    local('sysctl -w net.mptcp.mptcp_debug=0')
    local('sysctl -w net.mptcp.mptcp_enabled=1') #be sure it's running
    #local('sysctl -w net.mptcp.mptcp_ndiffports=2') # not supported by v0.89
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
            #if("net.mptcp.mptcp_ndiffports" == n[0]):
            #    local("sysctl -w net.mptcp.mptcp_ndiffports=" + n[2])
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

# Create all file tests concerned by the connection level
def create_connection_tests():
	import random
	sock =  "+0 socket(..., SOCK_STREAM, IPPROTO_TCP) = 3\n"
	reuse = "+0 setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n"
	bind =  "+0 bind(3, ..., ...) = 0\n"
	listen = "+0 listen(3, 1) = 0\n"
	
	syn =    "+0  < S 0:0(0) win 32792 <mss 1028,sackOK,nop,nop,nop,wscale 7,mp_capable a>\n"
	synack = "+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_capable b>\n"
	ack =    "+0  < . 1:1(0) ack 1 win 257 <mp_capable a b, dss dack4>\n"
	accept = "+0  accept(3, ..., ...) = 4\n"
	
	
	# Server and client side of connection. The goal is to have the same number with checksum and without
	# Create server side of connection
	for nb in range(5):
		filename = "automated_tests/connection/mp_capable_server_"+str(nb)+".pkt"
		fd = open(filename, 'w') 
		if(nb<2):
		  fd.write("+0 `sysctl -w net.mptcp.mptcp_checksum=0`\n")
		fd.write(sock + reuse + bind + listen)
		nb_rand = random.getrandbits(64) #random.randint(1, 10)
		if(nb<2):	# no checksum
		  fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_capable_no_cs a="+str(nb_rand)+">\n") 
		  fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_capable_no_cs b>\n")
		  fd.write("+0 < . 1:1(0) ack 1 win 257 <mp_capable_no_cs a="+str(nb_rand)+" b, dss dack4>\n") 
		else:	# with checksum
		  fd.write("+0 < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_capable a="+str(nb_rand)+">\n") 
		  fd.write(synack)
		  fd.write("+0 < . 1:1(0) ack 1 win 257 <mp_capable a="+str(nb_rand)+" b, dss dack4>\n") 
		fd.write(accept)
		if(nb<2):
		  fd.write("+0  write(4, ..., 1000) = 1000\n")
		  fd.write("+0  > P. 1:1001(1000) ack 1 <dss dack4 dsn4 nocs, nop, nop>\n")
		  fd.write("+.1 < . 1:1(0) ack 1001 win 255 <dss dack4> \n")
		  fd.write("+0 `sysctl -w net.mptcp.mptcp_checksum=1`\n")
		else:
		  fd.write("+0  write(4, ..., 1000) = 1000\n")
		  fd.write("+0  > P. 1:1001(1000) ack 1 <dss dack4 dsn4>\n")
		  fd.write("+.1 < . 1:1(0) ack 1001 win 225 <dss dack4>\n")
		print("Created: "+filename)
		fd.close()
		
		# Create client side of connection
		filename = "automated_tests/connection/mp_capable_client_"+str(nb)+".pkt"
		fd = open(filename, 'w') 
		if(nb<2):
		  fd.write("+0 `sysctl -w net.mptcp.mptcp_checksum=0`\n")
		nonblock = "+0.0 fcntl(3, F_GETFL) = 0x2 (flags O_RDWR)\n+0.000 fcntl(3, F_SETFL, O_RDWR|O_NONBLOCK) = 0\n"
		connect = "+0.0 connect(3, ..., ...) = -1 EINPROGRESS (Operation now in progress)\n"
		blocking = "+0.1 getsockopt(3, SOL_SOCKET, SO_ERROR, [0], [4]) = 0\n+0.0 fcntl(3, F_SETFL, O_RDWR) = 0   // set back to blocking\n"
		fd.write(sock + nonblock + connect)
		
		if(nb<2): 	# no checksum
		  fd.write("+0.0 > S 0:0(0) win 29200 <mss 1460,sackOK,TS val 100 ecr 0,nop,wscale 7,mp_capable_no_cs a>\n") 
		  fd.write("+0.0 < S. 0:0(0) ack 1 win 5792 <mss 1460,sackOK,TS val 700 ecr 100,nop,wscale 7,mp_capable_no_cs b="+str(nb_rand)+">\n")
		  fd.write("+0.0 > . 1:1(0) ack 1 <nop,nop,TS val 100 ecr 700,mp_capable_no_cs a b="+str(nb_rand)+", dss dack4> \n")
		else:  	# with checksum
		  fd.write("+0.0 > S 0:0(0) win 29200 <mss 1460,sackOK,TS val 100 ecr 0,nop,wscale 7,mp_capable a>\n") 
		  fd.write("+0.0 < S. 0:0(0) ack 1 win 5792 <mss 1460,sackOK,TS val 700 ecr 100,nop,wscale 7,mp_capable b="+str(nb_rand)+">\n")
		  fd.write("+0.0 > . 1:1(0) ack 1 <nop,nop,TS val 100 ecr 700,mp_capable a b="+str(nb_rand)+", dss dack4=1>\n")
		fd.write(blocking)
		if(nb<2):
		  fd.write("+0 < P. 1:1001(1000) ack 1 win 450  <dss dack4 dsn4 nocs, nop, nop>\n")
		  fd.write("+0 > . 1:1(0) ack 1001 <nop,nop,TS val 150 ecr 700, dss dack4>\n")
		  fd.write("+0 `sysctl -w net.mptcp.mptcp_checksum=1`\n")
		else:
		  fd.write("+0 < P. 1:1001(1000) ack 1 win 450  <dss dack4 dsn4>\n")
		  fd.write("+0 > . 1:1(0) ack 1001 <nop,nop,TS val 150 ecr 700, dss dack4>\n")
		print("Created: "+filename)
		fd.close()
	
	
	#Tests based on flags
	for nb in range(10):
		flags = ""
		filename = "automated_tests/connection/mp_capable_server_flags_"+str(nb)+".pkt"
		
		nb_rand = random.randint(0, 256)
		with open(filename, 'w') as fd: 
			flag_a_exists = (nb_rand&128) > 0 
			if(not flag_a_exists): # No checksum needed => flag a
				fd.write("+0 `sysctl -w net.mptcp.mptcp_checksum=0`\n\n")
				mp_capable_token = 'mp_capable_no_cs'
			else:
				mp_capable_token = 'mp_capable'
			
			fd.write(sock + reuse + bind + listen)
			
			if (nb_rand&128) > 0 : flags += " flag_a" 
			if (nb_rand&64) > 0 : flags += " flag_b" 
			if (nb_rand&32) > 0 : flags += " flag_c" 
			if (nb_rand&16) > 0 : flags += " flag_d" 
			if (nb_rand&8) > 0 : flags += " flag_e" 
			if (nb_rand&4) > 0 : flags += " flag_f" 
			if (nb_rand&2) > 0 : flags += " flag_g" 
			if (nb_rand&1) > 0 : flags += " flag_h" 
			
			if nb_rand==0 : flags = " no_flags"
			fd.write("+0 < S 0:0(0) win 32792 <mss 1000,sackOK,nop,nop,nop,wscale 7,"+mp_capable_token+" a"+ flags +">\n") 
			if((nb_rand&1) > 0):
				if((nb_rand&64) > 0): # b flag ?
					fd.write("+0 < S 0:0(0) win 32792 <mss 1000,sackOK,nop,nop,nop,wscale 7,"+mp_capable_token+" a>\n")
			
				if(flag_a_exists): 
					fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,sackOK,nop,nop,nop,wscale 7,"+mp_capable_token+" b flag_a flag_h>\n")
				else:
					fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,sackOK,nop,nop,nop,wscale 7,"+mp_capable_token+" b flag_h>\n")
			
				fd.write("+0.15  < . 1:1(0) ack 1 win 257 <"+mp_capable_token+" a b, dss dack4>\n") 
			else: # regular TCP
				if((nb_rand&64) > 0): # b flag ?
					fd.write("+0 < S 0:0(0) win 32792 <mss 1000,sackOK,nop,nop,nop,wscale 7>\n")
				fd.write("+0  > S. 0:0(0) ack 1 win 29200 <mss 1460,sackOK,nop,nop,nop,wscale 7>\n")
				fd.write("+0.1  < . 1:1(0) ack 1 win 257\n")
			
			fd.write("+0  accept(3, ..., ...) = 4\n\n")
			if(not flag_a_exists): # Checksum needed back
				fd.write("+0 `sysctl -w net.mptcp.mptcp_checksum=1`\n")
			
			print("Created: "+filename)
	
def create_mp_join_tests():
	import random
	sock =  "+0 socket(..., SOCK_STREAM, IPPROTO_TCP) = 3\n"
	reuse = "+0 setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n"
	bind =  '+0  bind(3, {sa_family = AF_INET, sin_port = htons(49152), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n'
	listen = "+0 listen(3, 1) = 0\n\n"
	
	syn =    "+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_capable key_a> sock(3)\n"
	synack = "+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7,mp_capable key_b> sock(3)\n"
	ack =    "+0  < . 1:1(0) ack 1 win 257 <mp_capable key_a key_b> sock(3)\n"
	accept = "+0  accept(3, ..., ...) = 4\n\n"
	
	#backup tests
	for nb in range(2):
		filename = "automated_tests/connection/mp_join_server_backup_"+str(nb)+".pkt"
		with open(filename, 'w') as fd: 
			fd.write(sock + reuse + bind + listen)
			fd.write(syn + synack + ack + accept)
			#subflow
			fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
			fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
			fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
			fd.write("+0  listen(5,1) = 0\n")
			fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn backup="+str(nb)+" address_id=0 token=sha1_32(key_b)> sock(5)\n")
			fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
			fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_b)> sock(5)\n")
			fd.write("+0 mp_join_accept(5) = 6\n\n")
			fd.write("+0 > . 1:1(0) ack 1 <...> sock(6)\n") # reliably mp_join_ack
			print("Created: "+filename)
	
	# tests on different class of IPs
	for nb in range(4):
		port_rand = random.randint(49153, 65534)	
		"""
		filename = "automated_tests/connection/mp_join_server_ports_ip_local_classA_"+str(nb)+".pkt"
		with open(filename, 'w') as fd: 
		
			#fd.write("+0 `openvpn --mktun --dev tun10`\n")
			#fd.write("+0 `ip link set tun10 up`\n")
			#fd.write("+0 `ip addr add 10.0.0.1/24 dev tun10`\n")
			#fd.write("+0 `ip tcp_metrics flush all > /dev/null 2>&1`\n")
			
			fd.write(sock + reuse + '+0  bind(3, {sa_family = AF_INET, sin_port = htons('+str(port_rand)+'), sin_addr = inet_addr("10.0.0.1")}, ...) = 0\n' + listen)
			fd.write(syn + synack + ack + accept)
			
			#subflow
			fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
			fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
			fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons('+str(port_rand)+'), sin_addr = inet_addr("10.0.0.1")}, ...) = 0\n')
			fd.write("+0  listen(5,1) = 0\n")
			fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
			fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
			fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_b)> sock(5)\n")
			fd.write("+0 mp_join_accept(5) = 6\n\n")
			fd.write("+0 > . 1:1(0) ack 1 <...> sock(6)\n") # reliably mp_join_ack
			#fd.write("+0 `openvpn --rmtun --dev tun10`\n")
			print("Created: "+filename)
			
		filename = "automated_tests/connection/mp_join_server_ports_ip_local_classB_"+str(nb)+".pkt"
		with open(filename, 'w') as fd: 
			fd.write(sock + reuse + '+0  bind(3, {sa_family = AF_INET, sin_port = htons('+str(port_rand)+'), sin_addr = inet_addr("172.16.0.1")}, ...) = 0\n' + listen)
			fd.write(syn + synack + ack + accept)
			#subflow
			fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
			fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
			fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons('+str(port_rand)+'), sin_addr = inet_addr("172.16.0.1")}, ...) = 0\n')
			fd.write("+0  listen(5,1) = 0\n")
			fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
			fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
			fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_b)> sock(5)\n")
			fd.write("+0 mp_join_accept(5) = 6\n\n")
			fd.write("+0 > . 1:1(0) ack 1 <...> sock(6)\n") # reliably mp_join_ack
			print("Created: "+filename)
			"""
		filename = "automated_tests/connection/mp_join_server_ports_ip_local_classC_"+str(nb)+".pkt"
		with open(filename, 'w') as fd: 
			fd.write(sock + reuse + bind + listen)
			fd.write(syn + synack + ack + accept)
			#subflow
			fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
			fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
			fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons('+str(port_rand)+'), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
			fd.write("+0  listen(5,1) = 0\n")
			fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
			fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
			fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_b)> sock(5)\n")
			fd.write("+0 mp_join_accept(5) = 6\n\n")
			fd.write("+0 > . 1:1(0) ack 1 <...> sock(6)\n") # reliably mp_join_ack
			print("Created: "+filename)
		
		filename = "automated_tests/connection/mp_join_server_ports_ip_multicast"+str(nb)+".pkt"
		with open(filename, 'w') as fd: 
			fd.write(sock + reuse + '+0  bind(3, {sa_family = AF_INET, sin_port = htons('+str(port_rand)+'), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n' + listen)
			fd.write(syn + synack + ack + accept)
			fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
			fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
			fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons('+str(port_rand)+'), sin_addr = inet_addr("224.0.0.1")}, ...) = 0\n')
			fd.write("+0  listen(5,1) = 0\n")
			fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
			fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
			fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_b)> sock(5)\n")
			fd.write("+0 mp_join_accept(5) = 6\n\n")
			fd.write("+0 > . 1:1(0) ack 1 <...> sock(6)\n") # reliably mp_join_ack
			print("Created: "+filename)
	
	# Tests on random values within mp_join option SYN packet
	for nb in range(2):
		filename = "automated_tests/connection/mp_join_server_option_syn_token_"+str(nb)+".pkt"
		with open(filename, 'w') as fd: 
			fd.write(sock + reuse + bind + listen)
			fd.write(syn + synack + ack + accept)
			token_rand = random.getrandbits(32)
			fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
			fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
			fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
			fd.write("+0  listen(5,1) = 0\n")
			fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token="+str(token_rand)+"> sock(5)\n")
			fd.write("+0  > R. 0:0(0) ack 1 win 0 sock(5)\n")
			print("Created: "+filename)
			
		
		filename = "automated_tests/connection/mp_join_server_option_syn_flags"+str(nb)+".pkt"
		with open(filename, 'w') as fd: 
			fd.write(sock + reuse + bind + listen)
			fd.write(syn + synack + ack + accept)
			addr_id_rand = random.getrandbits(8)
			fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
			fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
			fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
			fd.write("+0  listen(5,1) = 0\n")
			fd.write("+0  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn address_id="+str(addr_id_rand)+" token=sha1_32(key_b)> sock(5)\n")
			fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
			fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_b)> sock(5)\n")
			fd.write("+0 mp_join_accept(5) = 6\n\n")
			fd.write("+0 > . 1:1(0) ack 1 <...> sock(6)\n")
			print("Created: "+filename)
	
	# Tests on random values within mp_join option ACK packet
	filename = "automated_tests/connection/mp_join_client_option_ack_hmac_sender_01.pkt"
	with open(filename, 'w') as fd: 
		fd.write(sock + reuse + bind + listen)
		fd.write(syn + synack + ack + accept)
		fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
		fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
		fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
		fd.write("+0  listen(5,1) = 0\n")
		fd.write("+0.1  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
		fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
		fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=auto> sock(5)\n")
		fd.write("+0  > . 1:1(0) ack 1 <dss dack4> sock(5)\n")
		print("Created: "+filename)
	
	filename = "automated_tests/connection/mp_join_client_option_ack_hmac_sender_02.pkt"
	with open(filename, 'w') as fd: 
		fd.write(sock + reuse + bind + listen)
		fd.write(syn + synack + ack + accept)
		token_rand = random.getrandbits(32)
		fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
		fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
		fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
		fd.write("+0  listen(5,1) = 0\n\n")
		fd.write("+0.1  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
		fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
		fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_b)> sock(5)\n")
		fd.write("+0  > . 1:1(0) ack 1 <dss dack4> sock(5)\n")
		print("Created: "+filename)

	filename = "automated_tests/connection/mp_join_client_option_ack_hmac_sender_03.pkt"
	with open(filename, 'w') as fd: 
		fd.write(sock + reuse + bind + listen)
		fd.write(syn + synack + ack + accept)
		token_rand = random.getrandbits(32)
		fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
		fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
		fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
		fd.write("+0  listen(5,1) = 0\n\n")
		fd.write("+0.1  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
		fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
		fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_a key_a)> sock(5)\n")
		fd.write("+0  > R 1:1(0) ack 0 sock(5)\n")
		print("Created: "+filename)
	
	filename = "automated_tests/connection/mp_join_client_option_ack_hmac_sender_04.pkt"
	with open(filename, 'w') as fd: 
		fd.write(sock + reuse + bind + listen)
		fd.write(syn + synack + ack + accept)
		token_rand = random.getrandbits(32)
		fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
		fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
		fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
		fd.write("+0  listen(5,1) = 0\n\n")
		fd.write("+0.1  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
		fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
		fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_b key_a)> sock(5)\n")
		fd.write("+0  > R 1:1(0) ack 0 sock(5)\n")
		print("Created: "+filename)
		
	filename = "automated_tests/connection/mp_join_client_option_ack_hmac_sender_05.pkt"
	with open(filename, 'w') as fd: 
		fd.write(sock + reuse + bind + listen)
		fd.write(syn + synack + ack + accept)
		token_rand = random.getrandbits(32)
		fd.write("+0  socket(..., SOCK_STREAM, IPPROTO_TCP) = 5\n")
		fd.write("+0  setsockopt(5, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n")
		fd.write('+0  bind(5, {sa_family = AF_INET, sin_port = htons(49153), sin_addr = inet_addr("192.168.0.1")}, ...) = 0\n')
		fd.write("+0  listen(5,1) = 0\n\n")
		fd.write("+0.1  < S 0:0(0) win 32792 <mss 1460,sackOK,nop,nop,nop,wscale 7,mp_join_syn token=sha1_32(key_b)> sock(5)\n")
		fd.write("+0  > S. 0:0(0) ack 1 win 28800 <mss 1460,nop,nop,sackOK,nop,wscale 7, mp_join_syn_ack sender_hmac=trunc_l64_hmac(key_b key_a) > sock(5)\n")
		fd.write("+0  < . 1:1(0) ack 1 win 32792 <mp_join_ack sender_hmac=full_160_hmac(key_b key_b)> sock(5)\n")
		fd.write("+0  > R 1:1(0) ack 0 sock(5)\n")
		print("Created: "+filename)
		
def create_data_tests():
  import random
  sock = "+0.0 socket(..., SOCK_STREAM, IPPROTO_TCP) = 3\n"
  reuse = "+0.0 setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0\n"
  bind = "+0.0 bind(3, ..., ...) = 0\n"
  listen = "+0.0 listen(3, 1) = 0\n\n"
  syn = "+0 < S 0:0(0) win 24900 <mss 1460,sackOK,nop,nop,nop,wscale 7, mp_capable a>\n"
  synack = "+0 > S. 0:0(0) ack 1 <mss 1460,sackOK,nop,nop,nop,wscale 7, mp_capable b>\n"
  ack = "+0 < . 1:1(0) ack 1 win 257 <mp_capable a b, dss dack4>\n"
  accept ="+0 accept(3, ..., ...) = 4\n"

  # send and receive at the same time data
  filename = "automated_tests/data/dss_server_both_directions.pkt"
  fd = open(filename, 'w') 
  fd.write(sock+reuse+bind+listen+syn+synack+ack+accept+"\n")
  nb_total = 1
  nb_total_sent = 1
  for nb_i in range(80):
    nb_rand_i = random.randint(1, 1420)
    fd.write("+0.01 write(4, ..., "+str(nb_rand_i)+") = "+str(nb_rand_i)+"\n")
    fd.write("+0.0 > P. "+str(nb_total)+":"+str(nb_rand_i+nb_total)+"("+str(nb_rand_i)+") ack "+str(nb_total_sent)+" <dss dack4 dsn4>\n")
    # fd.write("+0.0 <  . "+str(nb_total_sent)+":"+str(nb_total_sent)+"(0) ack "+str(nb_rand_i+nb_total)+" win 257 <dss dack4>\n\n")
    nb_total = nb_total + nb_rand_i
    
    nb_rand_ii = random.randint(1, 1420)
    fd.write("+0.0 < P. "+str(nb_total_sent)+":"+str(nb_total_sent+nb_rand_ii)+"("+str(nb_rand_ii)+") ack "+str(nb_total)+" win 450 <dss dack4 dsn4 >\n")
    if nb_i%2 == 0:
      fd.write("+0.0 > . "+str(nb_total)+":"+str(nb_total)+"(0) ack "+str(nb_total_sent+nb_rand_ii)+" <dss dack4>\n\n")
    else:
      fd.write("+0.04 > . "+str(nb_total)+":"+str(nb_total)+"(0) ack "+str(nb_total_sent+nb_rand_ii)+" <dss dack4>\n\n")
    nb_total_sent = nb_total_sent + nb_rand_ii
    
  fd.close()
  print("Created: "+filename)

  #send big segments to server -> ack only one
  filename = "automated_tests/data/dss_server_random_big_data.pkt"
  fd = open(filename, 'w') 
  fd.write("+0.0 `ethtool -K tun0 tso off`\n")
  fd.write(sock+reuse+bind+listen+syn+synack+ack+accept+"\n")
  nb_random = random.randint(7100, 14200) #random.getrandbits(32)
  fd.write("+0.0 write(4, ..., "+str(nb_random)+") = "+str(nb_random)+"\n\n")
  nb_total = 1
  for nb in range(nb_random/1440):
    fd.write("+0.0 > . "+str(nb_total)+":"+str(nb_total+1440)+"(1440) ack 1 <dss dack4 dsn4 >\n")
    fd.write("+0.0 < . 1:1(0) ack "+str(nb_total+1440)+" win 257 <dss dack4>\n")
    nb_total += 1420
  fd.write("+0.0 > . "+str(nb_total)+":"+str(nb_random)+"("+str(nb_random - nb_total)+") ack 1 <dss dack4 dsn4 >\n")
  fd.write("+0.0 < . 1:1(0) ack "+str(nb_random)+" win 257 <dss dack4>\n")
  fd.close()
  print("Created: "+filename)


def create_add_address_tests():
	print("Creating add_address tests => Futur work\n")

def create_remove_address_tests():
	print("Creating remove_address tests => Futur work\n")

def create_mp_prio_tests():
	print("Creating mp_prio tests => Futur work\n")

def create_mp_fail_tests():
	print("Creating mp_fail tests => Futur work\n")

def create_mp_fastclose_tests():
	print("Creating mp_fastclose tests => Futur work\n")


@task 
def create_tests():
    import os
    print("Creating file tests in automated_tests folder ...")
    
    #create folder it does not exist
    if not os.path.exists("automated_tests"): os.makedirs("automated_tests")
    if not os.path.exists("automated_tests/connection"): os.makedirs("automated_tests/connection")
    if not os.path.exists("automated_tests/data"): os.makedirs("automated_tests/data")
    #if not os.path.exists("automated_tests/address"): os.makedirs("automated_tests/address")
    #if not os.path.exists("automated_tests/mp_prio"): os.makedirs("automated_tests/mp_prio")
    #if not os.path.exists("automated_tests/mp_fail"): os.makedirs("automated_tests/mp_fail")
    #if not os.path.exists("automated_tests/close"): os.makedirs("automated_tests/close")
    
    create_connection_tests() # OK
    create_mp_join_tests()    # OK
    create_data_tests()       # OK
#    create_add_address_tests() 
#    create_remove_address_tests()
#    create_mp_prio_tests()
#    create_mp_fastclose_tests()
#    create_mp_fail_tests()
#    create_close_tests()
