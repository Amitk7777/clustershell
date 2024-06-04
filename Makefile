clean:
	sudo rm -rf build dist lib/ClusterShell.* groups.conf clush.conf clush.conf.d groups.conf.d groups.d topology.conf.example
run:
	sudo python3 setup.py build 
	sudo python3 setup.py install
check:
	clush -m sshpass -w 10.48.220.55
file:
	clush -m sshpass-file -w 10.48.220.55
pem:
	clush -m sshpass-pem -w ec2-user@10.3.4.[229,244,254]
rem:
	sudo pip uninstall clustershell
aos:
	clush -m aos -w aos-sc-[r0fi8jts,z3k6t72,yz5ncrtv]