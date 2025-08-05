import threading
from scapy.all import sniff, IP, TCP, UDP
import mysql.connector
from mysql.connector import Error as DbError


DB_CONFIG = {
    "host": "",
    "user": "",
    "password": "",
    "database": "",
}

protocol_map = {
    0: "HOPOPT",  # IPv6 Hop-by-Hop Option
    1: "ICMP",  # Internet Control Message Protocol
    2: "IGMP",  # Internet Group Management Protocol
    3: "GGP",  # Gateway-to-Gateway Protocol
    4: "IPv4",  # IPv4 encapsulation
    5: "ST",  # Stream Transport
    6: "TCP",  # Transmission Control Protocol
    8: "EGP",  # Exterior Gateway Protocol
    9: "IGP",  # Interior Gateway Protocol (any private interior gateway)
    17: "UDP",  # User Datagram Protocol
    27: "RDP",  # Reliable Data Protocol
    29: "ISO-TP4",  # ISO Transport Protocol Class 4
    33: "DCCP",  # Datagram Congestion Control Protocol
    36: "XTP",  # Xpress Transport Protocol
    37: "DDP",  # Datagram Delivery Protocol
    41: "IPv6",  # IPv6 encapsulation
    43: "IPv6-Route",  # Routing Header for IPv6
    44: "IPv6-Frag",  # Fragment Header for IPv6
    45: "IDRP",  # Inter-Domain Routing Protocol
    46: "RSVP",  # Reservation Protocol
    47: "GRE",  # Generic Routing Encapsulation
    50: "ESP",  # Encapsulating Security Payload
    51: "AH",  # Authentication Header
    58: "IPv6-ICMP",  # ICMP for IPv6
    59: "IPv6-NoNxt",  # No Next Header for IPv6
    60: "IPv6-Opts",  # Destination Options for IPv6
    88: "EIGRP",  # Enhanced Interior Gateway Routing Protocol
    89: "OSPF",  # Open Shortest Path First
    92: "MTP",  # Multicast Transport Protocol
    94: "IPIP",  # IP-within-IP Encapsulation Protocol
    97: "ETHERIP",  # Ethernet-within-IP Encapsulation
    98: "ENCAP",  # Encapsulation Header
    103: "PIM",  # Protocol Independent Multicast
    108: "IPComp",  # IP Payload Compression Protocol
    112: "VRRP",  # Virtual Router Redundancy Protocol
    115: "L2TP",  # Layer Two Tunneling Protocol
    121: "SMP",  # Simple Message Protocol
    132: "SCTP",  # Stream Control Transmission Protocol
    133: "FC",  # Fibre Channel
    136: "UDPLite",  # UDP-Lite
    137: "MPLS-in-IP",  # MPLS-in-IP
    143: "PTP",  # Protocol Tunnelling Protocol
}

stop_sniffing_event = threading.Event()


# 패킷 캡쳐 후 DB에 저장하는 로직
def sniff_and_save(stop_event):
    db_conn = None  # 초기화

    try:
        # 쓰레드 내에서 새 DB 연결 생성
        db_conn = mysql.connector.connect(**DB_CONFIG)  # 딕셔너리의 언팩 연산자 활용
        cursor = db_conn.cursor()

        insert_query = """
        INSERT INTO log (protocol, src_ip, src_port, dst_ip, dst_port)
        VALUES (%s, %s, %s, %s, %s)
        """

        def process_packet_and_insert(packet):
            if not IP in packet:
                return  # 분석할 수 없는 패킷은 무시

            # 변수 초기화
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            src_port, dst_port = 0, 0
            protocol = ""

            # 프로토콜 및 포트 정보 추출
            if TCP in packet:
                protocol = "TCP"
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
            elif UDP in packet:
                protocol = "UDP"
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
            else:
                proto_num = packet[IP].proto
                protocol = protocol_map.get(proto_num)

            log = (protocol, src_ip, src_port, dst_ip, dst_port)

            try:
                # DB에 실시간으로 로그 저장
                cursor.execute(insert_query, log)
                db_conn.commit()
            except DbError as e:
                # insert 오류가 발생하더라도 에이전트가 종료되지 않도록 로그 처리
                print(f"DB 작업 중 오류 발생: {e}")

        sniff(
            prn=process_packet_and_insert,
            store=0,
            stop_filter=lambda p: stop_event.is_set(),
        )

    except DbError as e:
        print(f"DB 작업 중 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    finally:
        if db_conn and db_conn.is_connected():
            db_conn.close()
            print("\n--- 데이터베이스 커넥션을 종료합니다 ---")


if __name__ == "__main__":
    sniffer_thread = threading.Thread(
        target=sniff_and_save, args=(stop_sniffing_event,)
    )
    sniffer_thread.start()

    print("\n--- 네트워크 트래픽 모니터링 중 ---")
    print("--- 중단하려면 Ctrl + C를 눌러주세요 ---")

    try:
        while sniffer_thread.is_alive():
            sniffer_thread.join(timeout=1.0)
    except KeyboardInterrupt:
        print("\n--- 모니터링을 중단합니다 ---")
        # 쓰레드 종료 요청 후 대기
        stop_sniffing_event.set()
        sniffer_thread.join(timeout=5)
        print("--- 네트워크 트래픽 모니터링을 종료합니다 ---")
