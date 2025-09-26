import flet as ft

# --- 1. 메뉴 데이터 정의 ---
# 실제 환경에서는 이 데이터를 외부 파일(JSON)이나 DB에서 관리하는 것이 좋습니다.
MENU_DATA = {
    "파스타": [
        {"name": "까르보나라", "price": 15000, "image": "https://i.ibb.co/6wmh5zC/carbonara.png"},
        {"name": "알리오 올리오", "price": 13000, "image": "https://i.ibb.co/g6z7vLd/aglio-e-olio.png"},
        {"name": "토마토 파스타", "price": 14000, "image": "https://i.ibb.co/kBSxMh6/tomato-pasta.png"},
    ],
    "스테이크": [
        {"name": "안심 스테이크", "price": 35000, "image": "https://i.ibb.co/SRvZbGt/tenderloin-steak.png"},
        {"name": "채끝 스테이크", "price": 32000, "image": "https://i.ibb.co/GcVp7zM/sirloin-steak.png"},
    ],
    "사이드": [
        {"name": "시저 샐러드", "price": 8000, "image": "https://i.ibb.co/r2L2wzV/caesar-salad.png"},
        {"name": "감자튀김", "price": 6000, "image": "https://i.ibb.co/bQdYsvK/french-fries.png"},
        {"name": "오늘의 스프", "price": 5000, "image": "https://i.ibb.co/K7zKx3f/soup.png"},
    ],
    "음료": [
        {"name": "콜라", "price": 3000, "image": "https://i.ibb.co/GWPzF7C/coke.png"},
        {"name": "에이드", "price": 5000, "image": "https://i.ibb.co/P48L2Tf/ade.png"},
        {"name": "하우스 와인", "price": 8000, "image": "https://i.ibb.co/KqL2nC0/wine.png"},
    ]
}

# --- 2. 메인 애플리케이션 ---
def main(page: ft.Page):
    page.title = "레스토랑 키오스크"
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    page.fonts = {
        "NanumSquare": "https://webfontworld.github.io/NanumSquare/NanumSquare.css"
    }
    page.theme = ft.Theme(font_family="NanumSquare")

    # --- 3. 애플리케이션 상태 관리 ---
    # 장바구니 데이터를 page.session에 저장하여 앱 전체에서 접근할 수 있도록 합니다.
    if not page.session.contains_key("cart"):
        page.session.set("cart", []) # [{'name': str, 'price': int, 'quantity': int}, ...]

    # --- 4. UI 컨트롤 정의 ---
    # 중앙 메뉴 그리드
    menu_grid = ft.GridView(
        expand=True, runs_count=4, max_extent=180, child_aspect_ratio=0.9, spacing=10, run_spacing=10
    )
    # 하단 장바구니 리스트 (구버전 호환: Column + scroll)
    cart_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)
    # 총 금액 텍스트
    total_price_text = ft.Text("0원", size=20, weight=ft.FontWeight.BOLD)
    # 식사/포장 선택
    order_type_segment = ft.SegmentedButton(
        segments=[
            ft.Segment(value="dine-in", label=ft.Text("매장 식사"), icon=ft.Icon(ft.Icons.STOREFRONT)),
            ft.Segment(value="take-out", label=ft.Text("포장"), icon=ft.Icon(ft.Icons.SHOPPING_BAG)),
        ]
    )
    order_type_segment.selected = {"dine-in"}

    # --- 5. 핵심 함수들 ---
    def update_cart_display():
        """장바구니 상태(page.session.get('cart'))를 기반으로 UI를 다시 그립니다."""
        cart_data = page.session.get("cart")
        cart_list.controls.clear()
        total_price = 0

        if not cart_data:
            cart_list.controls.append(ft.Text("장바구니가 비어있습니다.", text_align=ft.TextAlign.CENTER, color="grey"))
        else:
            for item in cart_data:
                total_price += item['price'] * item['quantity']
                cart_list.controls.append(create_cart_item_row(item))
        
        total_price_text.value = f"{total_price:,}원"
        page.update()

    def add_to_cart(e):
        """메뉴를 카트에 추가하거나 수량을 늘립니다."""
        menu_item_data = e.control.data
        cart_data = page.session.get("cart")

        # 이미 카트에 있는지 확인
        found = False
        for item in cart_data:
            if item['name'] == menu_item_data['name']:
                item['quantity'] += 1
                found = True
                break
        
        # 카트에 없으면 새로 추가
        if not found:
            cart_data.append({"name": menu_item_data['name'], "price": menu_item_data['price'], "quantity": 1})
        
        page.session.set("cart", cart_data) # 변경된 카트 정보 저장
        update_cart_display()

    def change_quantity(e):
        """장바구니 아이템의 수량을 변경합니다."""
        item_name = e.control.data['name']
        delta = e.control.data['delta']
        cart_data = page.session.get("cart")

        for item in cart_data:
            if item['name'] == item_name:
                item['quantity'] += delta
                if item['quantity'] <= 0: # 수량이 0 이하면 삭제
                    cart_data.remove(item)
                break
        
        page.session.set("cart", cart_data)
        update_cart_display()
        
    def place_order(e):
        """결제 버튼 클릭 시 호출됩니다."""
        if not page.session.get("cart"):
            page.snack_bar = ft.SnackBar(content=ft.Text("장바구니에 메뉴를 담아주세요."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        def close_dialog(e):
            dialog.open = False
            page.session.set("cart", []) # 장바구니 비우기
            update_cart_display()
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("주문 완료"),
            content=ft.Text("주문이 성공적으로 접수되었습니다.\n감사합니다!"),
            actions=[ft.TextButton("확인", on_click=close_dialog)],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- 6. UI 생성 함수들 ---
    def create_cart_item_row(item_data):
        """장바구니에 표시될 각 아이템 행(Row)을 생성합니다."""
        return ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(item_data['name'], size=14, expand=2),
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.IconButton(ft.Icons.REMOVE, on_click=change_quantity, data={'name': item_data['name'], 'delta': -1}, icon_size=16),
                        ft.Text(item_data['quantity'], size=14),
                        ft.IconButton(ft.Icons.ADD, on_click=change_quantity, data={'name': item_data['name'], 'delta': 1}, icon_size=16),
                    ]
                ),
                ft.Text(f"{(item_data['price'] * item_data['quantity']):,}원", size=14, expand=1, text_align=ft.TextAlign.RIGHT),
            ]
        )

    def create_menu_item_card(item_data):
        """중앙 메뉴 영역에 표시될 카드 UI를 생성합니다."""
        return ft.Card(
            elevation=2,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Image(src=item_data["image"], fit=ft.ImageFit.COVER, height=100, border_radius=ft.border_radius.only(top_left=10, top_right=10)),
                        ft.Container(
                            padding=8,
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(item_data["name"], size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{item_data['price']:,}원", size=13, color="grey"),
                                ]
                            )
                        )
                    ],
                    spacing=0
                ),
                on_click=add_to_cart,
                data=item_data,
                border_radius=ft.border_radius.all(10),
            )
        )

    def select_category(e):
        """좌측 카테고리 선택 시 중앙 메뉴를 업데이트합니다."""
        # 모든 카테고리 버튼 스타일 초기화
        for btn in category_buttons.controls:
            btn.style = category_button_style
        # 선택된 버튼 스타일 변경
        e.control.style = selected_category_button_style

        category_name = e.control.text
        menu_grid.controls.clear()
        for item in MENU_DATA[category_name]:
            menu_grid.controls.append(create_menu_item_card(item))
        page.update()

    # --- 7. 레이아웃 구성 ---
    # 카테고리 버튼 스타일
    category_button_style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5), padding=15, bgcolor="whitesmoke", color="black")
    selected_category_button_style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5), padding=15, bgcolor="blue", color="white")

    # 좌측 카테고리 영역
    category_buttons = ft.Column(
        spacing=10,
        controls=[
            ft.ElevatedButton(text=category, on_click=select_category, style=category_button_style)
            for category in MENU_DATA.keys()
        ]
    )
    # 첫 번째 버튼을 선택된 상태로 초기화
    category_buttons.controls[0].style = selected_category_button_style
    # 첫 번째 카테고리 메뉴를 초기에 로드
    initial_category = list(MENU_DATA.keys())[0]
    for item in MENU_DATA[initial_category]:
        menu_grid.controls.append(create_menu_item_card(item))

    # 전체 화면 레이아웃
    page.add(
        ft.Column(
            expand=True,
            controls=[
                # 상단 영역 (카테고리 + 메뉴)
                ft.Row(
                    expand=True,
                    controls=[
                        # 좌측 카테고리
                        ft.Container(
                            category_buttons,
                            width=180,
                            padding=10,
                            bgcolor="#f5f5f5"
                        ),
                        # 중앙 메뉴
                        ft.Container(
                            menu_grid,
                            expand=True,
                            padding=20,
                        )
                    ]
                ),
                # 하단 장바구니
                ft.Container(
                    ft.Column([
                        ft.Text("장바구니", size=22, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=5, color="transparent"),
                        ft.Row(
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                # 장바구니 아이템 리스트 (고정 높이 + 내부 스크롤)
                                ft.Container(
                                    content=cart_list,
                                    expand=True,
                                    height=180,
                                    padding=ft.padding.only(right=20),
                                ),
                                # 결제 정보 및 버튼
                                ft.Column(
                                    width=300,
                                    spacing=15,
                                    controls=[
                                        order_type_segment,
                                        ft.Row([ft.Text("총 주문 금액", size=16), total_price_text]),
                                        ft.ElevatedButton("결제하기", on_click=place_order, height=50, style=ft.ButtonStyle(bgcolor="green", color="white")),
                                    ]
                                )
                            ]
                        )
                    ]),
                    height=250,
                    padding=20,
                    bgcolor="whitesmoke",
                    border=ft.border.only(top=ft.BorderSide(1, "#e0e0e0"))
                )
            ]
        )
    )
    # 앱 시작 시 장바구니 UI 업데이트
    update_cart_display()

if __name__ == "__main__":
    ft.app(target=main)