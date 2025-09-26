#tcp 통신 샘플
import socket
import json
import threading
import time
import flet as ft

class TCPOrderSender:
    """TCP 통신으로 주문 데이터를 전송하는 클래스"""
    
    def __init__(self, server_host="localhost", server_port=9999, timeout=5):
        self.server_host = server_host
        self.server_port = server_port
        self.timeout = timeout
    
    def send_order(self, order_data):
        """
        주문 데이터를 TCP로 전송
        
        Args:
            order_data (dict): 주문 정보
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 소켓 생성
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                
                # 서버 연결
                sock.connect((self.server_host, self.server_port))
                
                # 주문 데이터를 JSON으로 변환
                order_json = json.dumps(order_data, ensure_ascii=False, indent=2)
                
                # 데이터 길이를 먼저 전송 (헤더)
                data_length = len(order_json.encode('utf-8'))
                length_header = f"{data_length:010d}".encode('utf-8')
                
                # 헤더 + 데이터 전송
                sock.sendall(length_header)
                sock.sendall(order_json.encode('utf-8'))
                
                # 서버 응답 받기
                response_length = int(sock.recv(10).decode('utf-8'))
                response_data = sock.recv(response_length).decode('utf-8')
                response = json.loads(response_data)
                
                if response.get('status') == 'success':
                    return True, response.get('message', '주문이 성공적으로 전송되었습니다.')
                else:
                    return False, response.get('message', '서버에서 오류가 발생했습니다.')
                    
        except socket.timeout:
            return False, "서버 응답 시간이 초과되었습니다."
        except ConnectionRefusedError:
            return False, "서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요."
        except Exception as e:
            return False, f"전송 중 오류가 발생했습니다: {str(e)}"

# KioskApp 클래스에 추가할 메서드들
def init_tcp_sender(self):
    """TCP 전송기 초기화 (KioskApp.__init__에 추가)"""
    # TCP 서버 설정 (필요에 따라 변경)
    self.tcp_sender = TCPOrderSender(
        server_host="192.168.1.100",  # 주방 시스템 IP
        server_port=9999,             # 포트 번호
        timeout=10                    # 타임아웃 (초)
    )

def complete_order(self):
    """주문 완료 처리 (기존 메서드 대체)"""
    order_number = self.order_manager.get_next_order_number()
    
    # 주문 데이터 생성
    order_data = {
        "order_number": order_number,
        "timestamp": time.datetime.now().isoformat(),
        "order_type": self.order_type,
        "items": self.cart.copy(),
        "total": sum(item["price"] * item["quantity"] for item in self.cart),
        "kitchen_info": {
            "special_instructions": "",
            "priority": "normal"  # normal, high, urgent
        }
    }
    
    # 로컬 저장
    self.order_manager.save_order(order_data)
    
    # TCP로 주방 시스템에 전송
    def send_to_kitchen():
        success, message = self.tcp_sender.send_order(order_data)
        
        # UI 스레드에서 결과 처리
        def update_ui():
            if success:
                # 성공 시 스낵바 표시
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ 주방에 주문이 전달되었습니다!"),
                    bgcolor=ft.Colors.GREEN_600,
                )
            else:
                # 실패 시 경고 스낵바 표시
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"⚠️ 주방 전송 실패: {message}"),
                    bgcolor=ft.Colors.ORANGE_600,
                )
            self.page.snack_bar.open = True
            self.page.update()
        
        # UI 업데이트는 메인 스레드에서 실행
        self.page.run_thread(update_ui)
    
    # 백그라운드에서 TCP 전송 (UI 블로킹 방지)
    threading.Thread(target=send_to_kitchen, daemon=True).start()
    
    # 장바구니 초기화
    self.cart.clear()
    self.update_cart_badge()
    
    # 완료 페이지 표시
    self.show_completion_page(order_number)