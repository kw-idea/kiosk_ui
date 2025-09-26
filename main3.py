import flet as ft
import json
import os
from datetime import datetime
from typing import List, Dict
import hashlib

# 메뉴 데이터
MENU_DATA = {
    "메인 메뉴": [
        {"name": "스테이크", "price": 32000, "image": "🥩"},
        {"name": "파스타 알리오올리오", "price": 14000, "image": "🍝"},
        {"name": "파스타 까르보나라", "price": 15000, "image": "🍝"},
        {"name": "리조또", "price": 16000, "image": "🍚"},
        {"name": "피자 마르게리타", "price": 18000, "image": "🍕"},
        {"name": "피자 페퍼로니", "price": 20000, "image": "🍕"},
        {"name": "햄버거", "price": 13000, "image": "🍔"},
        {"name": "치킨 그릴", "price": 22000, "image": "🍗"},
    ],
    "사이드 메뉴": [
        {"name": "감자튀김", "price": 5000, "image": "🍟"},
        {"name": "어니언링", "price": 6000, "image": "🧅"},
        {"name": "치즈스틱", "price": 7000, "image": "🧀"},
        {"name": "샐러드", "price": 8000, "image": "🥗"},
        {"name": "수프", "price": 6000, "image": "🍲"},
        {"name": "갈릭브레드", "price": 4000, "image": "🥖"},
    ],
    "음료": [
        {"name": "콜라", "price": 3000, "image": "🥤"},
        {"name": "사이다", "price": 3000, "image": "🥤"},
        {"name": "오렌지주스", "price": 4000, "image": "🧃"},
        {"name": "커피", "price": 3500, "image": "☕"},
        {"name": "아이스티", "price": 3500, "image": "🧋"},
        {"name": "맥주", "price": 5000, "image": "🍺"},
        {"name": "와인", "price": 8000, "image": "🍷"},
    ]
}

class OrderManager:
    """주문 데이터 관리 클래스"""
    def __init__(self):
        self.orders_file = "orders.json"
        self.load_orders()
    
    def load_orders(self):
        """저장된 주문 불러오기"""
        if os.path.exists(self.orders_file):
            with open(self.orders_file, 'r', encoding='utf-8') as f:
                self.orders = json.load(f)
        else:
            self.orders = []
    
    def save_order(self, order_data):
        """새 주문 저장"""
        self.orders.append(order_data)
        with open(self.orders_file, 'w', encoding='utf-8') as f:
            json.dump(self.orders, f, ensure_ascii=False, indent=2)
    
    def get_next_order_number(self):
        """다음 주문번호 생성"""
        if not self.orders:
            return 1
        return max([order.get('order_number', 0) for order in self.orders]) + 1

class KioskApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "양식점 키오스크"
        self.page.window.width = 1024
        self.page.window.height = 768
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        
        # 주문 관리자
        self.order_manager = OrderManager()
        
        # 장바구니
        self.cart = []
        self.order_type = "매장"  # 매장/포장
        
        # 현재 페이지
        self.current_page = "menu"  # menu, cart, payment, complete
        
        # UI 컴포넌트
        self.main_container = ft.Container()
        self.cart_badge = ft.Text("0", color=ft.Colors.WHITE)
        
        # 관리자 모드
        self.is_admin = False
        self.admin_password = hashlib.sha256("admin1234".encode()).hexdigest()
        
        self.setup_ui()
    
    def setup_ui(self):
        """메인 UI 설정"""
        self.page.add(
            ft.Container(
                content=ft.Column([
                    self.create_header(),
                    self.main_container,
                ], spacing=0),
                padding=0,
                expand=True,
            )
        )
        self.show_menu_page()
    
    def create_header(self):
        """헤더 생성"""
        return ft.Container(
            content=ft.Row([
                ft.Text("🍽️ 양식점 키오스크", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Row(spacing=10),  # 여백
                ft.Row([
                    ft.Container(
                        content=ft.Stack([
                            ft.IconButton(
                                icon=ft.Icons.SHOPPING_CART,
                                icon_color=ft.Colors.WHITE,
                                icon_size=30,
                                on_click=self.go_to_cart,
                            ),
                            ft.Container(
                                content=self.cart_badge,
                                bgcolor=ft.Colors.RED,
                                border_radius=10,
                                padding=5,
                                right=0,
                                top=0,
                            ),
                        ]),
                        width=60,
                        height=60,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                        icon_color=ft.Colors.WHITE,
                        icon_size=30,
                        on_click=self.show_admin_login,
                    ),
                ]),
            ], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=ft.Colors.BLUE_700,
            padding=20,
            height=80,
        )
    
    def show_menu_page(self):
        """메뉴 페이지 표시"""
        self.current_page = "menu"
        
        # 메뉴 컨텐츠 영역
        menu_content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.update_menu_display(menu_content, "메인 메뉴")
        
        self.main_container.content = ft.Row([
            # 카테고리 선택 영역
            ft.Container(
                content=ft.Column([
                    ft.Text("카테고리", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    *[
                        ft.ElevatedButton(
                            text=category,
                            width=180,
                            height=60,
                            on_click=lambda e, c=category: self.update_menu_display(menu_content, c),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            )
                        )
                        for category in MENU_DATA.keys()
                    ],
                    ft.Divider(),
                    ft.Text("주문 방식", size=18, weight=ft.FontWeight.BOLD),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value="매장", label="매장 식사"),
                            ft.Radio(value="포장", label="포장 주문"),
                        ]),
                        value="매장",
                        on_change=self.change_order_type,
                    ),
                ], spacing=15),
                width=220,
                padding=20,
                bgcolor=ft.Colors.GREY_100,
            ),
            
            # 메뉴 표시 영역
            ft.Container(
                content=menu_content,
                expand=True,
                padding=20,
            ),
        ], expand=True, spacing=0)
        
        self.page.update()
    
    def show_cart_page(self):
        """장바구니 페이지 표시"""
        self.current_page = "cart"
        
        # 장바구니 아이템 목록
        cart_items = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        total = 0
        
        for item in self.cart:
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            
            cart_items.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(item["image"], size=40),
                            width=60,
                        ),
                        ft.Column([
                            ft.Text(item["name"], size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"개당 {item['price']:,}원", size=14, color=ft.Colors.GREY_600),
                        ], expand=True, spacing=5),
                        ft.Container(
                            content=ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE_CIRCLE,
                                    on_click=lambda e, i=item: self.update_quantity(i, -1),
                                    icon_size=30,
                                    icon_color=ft.Colors.RED_400,
                                ),
                                ft.Container(
                                    content=ft.Text(str(item["quantity"]), size=18, weight=ft.FontWeight.BOLD),
                                    width=40,
                                    alignment=ft.alignment.center,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.ADD_CIRCLE,
                                    on_click=lambda e, i=item: self.update_quantity(i, 1),
                                    icon_size=30,
                                    icon_color=ft.Colors.GREEN_400,
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            width=140,
                        ),
                        ft.Container(
                            content=ft.Text(f"{subtotal:,}원", size=18, weight=ft.FontWeight.BOLD),
                            width=100,
                            alignment=ft.alignment.center_right,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    padding=20,
                )
            )
        
        # 빈 장바구니 처리
        if not self.cart:
            cart_items.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=80, color=ft.Colors.GREY_400),
                        ft.Text("장바구니가 비어있습니다", size=20, color=ft.Colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        self.main_container.content = ft.Column([
            # 페이지 제목과 뒤로가기
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=30,
                        on_click=lambda e: self.show_menu_page(),
                    ),
                    ft.Text("장바구니", size=24, weight=ft.FontWeight.BOLD),
                ]),
                padding=ft.padding.all(20),
            ),
            
            # 장바구니 내용
            ft.Container(
                content=cart_items,
                expand=True,
                padding=ft.padding.symmetric(horizontal=20),
            ),
            
            # 하단 총액 및 버튼
            ft.Container(
                content=ft.Column([
                    ft.Divider(thickness=2),
                    ft.Row([
                        ft.Text("총 결제금액", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{total:,}원", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.ElevatedButton(
                            "계속 주문",
                            height=50,
                            width=150,
                            on_click=lambda e: self.show_menu_page(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREY_400,
                                color=ft.Colors.WHITE,
                            )
                        ),
                        ft.ElevatedButton(
                            "결제하기",
                            height=50,
                            width=200,
                            on_click=lambda e: self.show_payment_page(),
                            disabled=len(self.cart) == 0,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREEN_700,
                                color=ft.Colors.WHITE,
                            )
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=15),
                bgcolor=ft.Colors.GREY_50,
                padding=20,
            ),
        ], expand=True, spacing=0)
        
        self.page.update()
    
    def show_payment_page(self):
        """결제 페이지 표시"""
        self.current_page = "payment"
        
        total = sum(item["price"] * item["quantity"] for item in self.cart)
        
        # 주문 요약
        order_summary = ft.Column([
            ft.Text(f"주문 방식: {self.order_type}", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
        ])
        
        for item in self.cart:
            order_summary.controls.append(
                ft.Row([
                    ft.Text(f"{item['image']} {item['name']}", size=16),
                    ft.Text(f"x {item['quantity']}", size=16),
                    ft.Text(f"{item['price']*item['quantity']:,}원", size=16, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        
        # 결제 수단 선택
        payment_method = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="card", label="💳 카드 결제"),
                ft.Radio(value="cash", label="💵 현금 결제"),
            ]),
            value="card",
        )
        
        self.main_container.content = ft.Column([
            # 페이지 제목과 뒤로가기
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=30,
                        on_click=lambda e: self.show_cart_page(),
                    ),
                    ft.Text("주문 확인", size=24, weight=ft.FontWeight.BOLD),
                ]),
                padding=ft.padding.all(20),
            ),
            
            # 주문 내용
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=order_summary,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                        padding=20,
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("결제 수단 선택", size=18, weight=ft.FontWeight.BOLD),
                            payment_method,
                        ]),
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                        padding=20,
                    ),
                ], spacing=20),
                expand=True,
                padding=ft.padding.symmetric(horizontal=20),
            ),
            
            # 하단 총액 및 버튼
            ft.Container(
                content=ft.Column([
                    ft.Divider(thickness=2),
                    ft.Row([
                        ft.Text("총 결제금액", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{total:,}원", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.ElevatedButton(
                            "이전",
                            height=50,
                            width=150,
                            on_click=lambda e: self.show_cart_page(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREY_400,
                                color=ft.Colors.WHITE,
                            )
                        ),
                        ft.ElevatedButton(
                            "결제 완료",
                            height=50,
                            width=200,
                            on_click=lambda e: self.complete_order(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREEN_700,
                                color=ft.Colors.WHITE,
                            )
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=15),
                bgcolor=ft.Colors.GREY_50,
                padding=20,
            ),
        ], expand=True, spacing=0)
        
        self.page.update()
    
    def show_completion_page(self, order_number):
        """주문 완료 페이지 표시"""
        self.current_page = "complete"
        
        self.main_container.content = ft.Container(
            content=ft.Column([
                ft.Container(height=50),  # 상단 여백
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=120),
                ft.Text("주문이 완료되었습니다!", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(height=30),
                ft.Container(
                    content=ft.Column([
                        ft.Text("주문번호", size=16, color=ft.Colors.GREY_600),
                        ft.Text(f"{order_number}", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                        ft.Text(f"{self.order_type} 주문", size=18, color=ft.Colors.GREY_600),
                        ft.Text(f"주문 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}", size=14, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(2, ft.Colors.BLUE_700),
                    border_radius=15,
                    padding=30,
                ),
                ft.Container(height=50),
                ft.ElevatedButton(
                    "새 주문 시작",
                    height=60,
                    width=200,
                    on_click=lambda e: self.start_new_order(),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                        text_style=ft.TextStyle(size=18),
                    )
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        self.page.update()
    
    def update_menu_display(self, menu_content, category):
        """선택된 카테고리의 메뉴 표시"""
        menu_content.controls.clear()
        
        # 카테고리 제목
        menu_content.controls.append(
            ft.Text(category, size=24, weight=ft.FontWeight.BOLD)
        )
        menu_content.controls.append(ft.Divider())
        
        # 메뉴 아이템 그리드
        menu_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=200,
            child_aspect_ratio=0.8,
            spacing=20,
            run_spacing=20,
        )
        
        for item in MENU_DATA[category]:
            menu_grid.controls.append(self.create_menu_item(item))
        
        menu_content.controls.append(menu_grid)
        self.page.update()
    
    def create_menu_item(self, item):
        """메뉴 아이템 카드 생성"""
        return ft.Container(
            content=ft.Column([
                ft.Text(item["image"], size=50),
                ft.Text(item["name"], size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(f"{item['price']:,}원", size=14, color=ft.Colors.BLUE_700),
                ft.ElevatedButton(
                    "담기",
                    on_click=lambda e, i=item: self.add_to_cart(i),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                    )
                ),
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=15,
            alignment=ft.alignment.center,
        )
    
    def add_to_cart(self, item):
        """장바구니에 아이템 추가"""
        # 이미 있는 아이템인지 확인
        for cart_item in self.cart:
            if cart_item["name"] == item["name"]:
                cart_item["quantity"] += 1
                break
        else:
            self.cart.append({
                "name": item["name"],
                "price": item["price"],
                "quantity": 1,
                "image": item["image"]
            })
        
        self.update_cart_badge()
        
        # 알림 표시
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"{item['name']}이(가) 장바구니에 추가되었습니다."),
            duration=1000,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def update_cart_badge(self):
        """장바구니 배지 업데이트"""
        total_items = sum(item["quantity"] for item in self.cart)
        self.cart_badge.value = str(total_items)
        self.page.update()
    
    def update_quantity(self, item, change):
        """아이템 수량 업데이트"""
        item["quantity"] += change
        if item["quantity"] <= 0:
            self.cart.remove(item)
        
        self.update_cart_badge()
        self.show_cart_page()  # 페이지 새로고침
    
    def go_to_cart(self, e):
        """장바구니 페이지로 이동"""
        self.show_cart_page()
    
    def complete_order(self):
        """주문 완료 처리"""
        order_number = self.order_manager.get_next_order_number()
        
        # 주문 데이터 생성
        order_data = {
            "order_number": order_number,
            "timestamp": datetime.now().isoformat(),
            "order_type": self.order_type,
            "items": self.cart.copy(),
            "total": sum(item["price"] * item["quantity"] for item in self.cart)
        }
        
        # 주문 저장
        self.order_manager.save_order(order_data)
        
        # 장바구니 초기화
        self.cart.clear()
        self.update_cart_badge()
        
        # 완료 페이지 표시
        self.show_completion_page(order_number)
    
    def start_new_order(self):
        """새 주문 시작"""
        self.cart.clear()
        self.update_cart_badge()
        self.order_type = "매장"
        self.show_menu_page()
    
    def change_order_type(self, e):
        """주문 방식 변경"""
        self.order_type = e.control.value
    
    def show_admin_login(self, e):
        """관리자 로그인 다이얼로그"""
        password_field = ft.TextField(
            label="비밀번호",
            password=True,
            autofocus=True,
        )
        
        def verify_password(e):
            entered_password = hashlib.sha256(password_field.value.encode()).hexdigest()
            if entered_password == self.admin_password:
                self.is_admin = True
                self.close_dialog(login_dialog)
                self.show_admin_panel()
            else:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("비밀번호가 올바르지 않습니다."))
                self.page.snack_bar.open = True
                self.page.update()
        
        login_dialog = ft.AlertDialog(
            title=ft.Text("관리자 로그인"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("관리자 비밀번호를 입력하세요:"),
                    password_field,
                    ft.Text("(기본 비밀번호: admin1234)", size=12, color=ft.Colors.GREY_600),
                ]),
                width=300,
                height=150,
            ),
            actions=[
                ft.TextButton("취소", on_click=lambda e: self.close_dialog(login_dialog)),
                ft.ElevatedButton("로그인", on_click=verify_password),
            ],
        )
        
        self.page.overlay.append(login_dialog)
        login_dialog.open = True
        self.page.update()
    
    def show_admin_panel(self):
        """관리자 패널 표시"""
        orders_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)
        
        # 주문 내역 로드
        self.order_manager.load_orders()
        
        if not self.order_manager.orders:
            orders_list.controls.append(
                ft.Text("주문 내역이 없습니다.", size=16, color=ft.Colors.GREY_600)
            )
        else:
            # 최근 주문부터 표시
            for order in reversed(self.order_manager.orders[-20:]):  # 최근 20개만 표시
                order_time = datetime.fromisoformat(order["timestamp"])
                
                order_card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"주문 #{order['order_number']}", weight=ft.FontWeight.BOLD),
                            ft.Text(order_time.strftime("%Y-%m-%d %H:%M"), color=ft.Colors.GREY_600),
                            ft.Text(f"{order['order_type']}", color=ft.Colors.BLUE_700),
                            ft.Text(f"{order['total']:,}원", weight=ft.FontWeight.BOLD),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text(
                                ", ".join([f"{item['name']} x{item['quantity']}" for item in order['items']]),
                                size=12,
                                color=ft.Colors.GREY_700,
                            )
                        ]),
                    ]),
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=8,
                    padding=10,
                    margin=ft.margin.only(bottom=10),
                )
                orders_list.controls.append(order_card)
        
        # 통계 정보
        total_orders = len(self.order_manager.orders)
        total_revenue = sum(order.get("total", 0) for order in self.order_manager.orders)
        today_orders = [
            order for order in self.order_manager.orders
            if datetime.fromisoformat(order["timestamp"]).date() == datetime.now().date()
        ]
        today_revenue = sum(order.get("total", 0) for order in today_orders)
        
        admin_dialog = ft.AlertDialog(
            title=ft.Text("관리자 패널", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("전체 주문", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{total_orders}건", size=20, weight=ft.FontWeight.BOLD),
                            ]),
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=8,
                            padding=15,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("전체 매출", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{total_revenue:,}원", size=20, weight=ft.FontWeight.BOLD),
                            ]),
                            bgcolor=ft.Colors.GREEN_50,
                            border_radius=8,
                            padding=15,
                            expand=True,
                        ),
                    ]),
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("오늘 주문", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{len(today_orders)}건", size=20, weight=ft.FontWeight.BOLD),
                            ]),
                            bgcolor=ft.Colors.ORANGE_50,
                            border_radius=8,
                            padding=15,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("오늘 매출", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{today_revenue:,}원", size=20, weight=ft.FontWeight.BOLD),
                            ]),
                            bgcolor=ft.Colors.PURPLE_50,
                            border_radius=8,
                            padding=15,
                            expand=True,
                        ),
                    ]),
                    ft.Divider(),
                    ft.Text("최근 주문 내역", size=18, weight=ft.FontWeight.BOLD),
                    orders_list,
                ], scroll=ft.ScrollMode.AUTO),
                width=600,
                height=600,
            ),
            actions=[
                ft.ElevatedButton(
                    "닫기",
                    on_click=lambda e: self.close_dialog(admin_dialog),
                ),
            ],
        )
        
        self.page.overlay.append(admin_dialog)
        admin_dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        """다이얼로그 닫기"""
        dialog.open = False
        self.page.update()

def main(page: ft.Page):
    app = KioskApp(page)

ft.app(target=main)