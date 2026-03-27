ASTU — Advanced Security Tool Utility

ASTU is a multi-purpose Linux command-line utility designed for networking, reconnaissance, and security research.
It provides fast access to Wi-Fi controls, scanning tools, OSINT functions, monitoring modes, and system analysis.

> ⚠️ Disclaimer
ASTU is strictly for educational and research use only.
You are responsible for using it ethically and legally on networks you own.




---

Features

🔧 Basic Networking

astu on — Enable Wi-Fi

astu off — Disable Wi-Fi

astu status — Show Wi-Fi radio status

astu devices — Show connected devices (ARP)

astu interfaces — List network interfaces

astu scan — Scan nearby Wi-Fi networks

astu connect <SSID> <pw> — Connect to Wi-Fi

astu ip — Show local IP

astu publicip — Show public IP

astu restart — Restart NetworkManager



---

🛰️ Advanced Network Tasks

astu monitor-on — Enable monitor mode

astu monitor-off — Disable monitor mode

astu capture <sec> — Capture packets to pcap

astu ping — Check internet connection

astu dnslookup <domain> — DNS lookup

astu traceroute <host> — Route tracing

astu portscan <IP> — Port scanning

astu arpspoof <target> <gateway> — ARP spoofing

astu wpscrack <BSSID> — WPS brute force

astu sniff-traffic — Live packet capture



---

🔍 OSINT & Recon

astu ipinfo <IP> — Geolocation, ISP, ASN

astu whois <domain> — WHOIS lookup

astu deep-scan <target> — Nmap OS/service scan

astu discover — Discover LAN devices



---

🔐 System Analysis

astu hidden — List hidden files

astu suspicious — Detect suspicious processes

astu sshcon — Active SSH sessions

astu macspoof — Random MAC address

astu traffic — Live traffic stats

astu cron — Show user + system cronjobs

astu vturl — VirusTotal URL scan

astu tor — Check Tor anonymity



