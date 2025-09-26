# kiosk_ui

kiosk user interface using python flet

-   main.py

-   main2.py

# main.py

## 레이아웃

### 페이지 초기 설정 (KioskApp.**init**)

-   타이틀/윈도우 크기/테마/패딩 지정.

-   상태: cart(장바구니 리스트), order_type(매장/포장), is_admin, admin_password(SHA-256 해시).

-   자주 쓰는 UI 핸들: cart_list(장바구니 목록 Column), total_text(합계), cart_badge(헤더 장바구니 개수 표시).

### 전체 컨테이너 (setup_ui)

-   Page에 최상위 Container → Column([ create_header(), create_main_content() ]) 추가.

### 헤더 (create_header)

-   좌측: 제목 텍스트.

-   우측:

    -   장바구니 아이콘 + 배지(Stack으로 겹치기) → on_click = show_cart

    -   관리자 아이콘 → on_click = show_admin_login

    -   배경색 파랑, 높이 80.

### 본문 (create_main_content)

-   전체는 Row 2분할:

    -   좌측 사이드바(고정폭 220)

        -   카테고리 버튼들(각 버튼은 update_menu_display(category) 호출)

        -   주문 방식 RadioGroup(매장/포장) → on_change = change_order_type

    -   우측 컨텐츠 영역(가변, expand)

        -   menu_content(스크롤 Column): 선택 카테고리의 메뉴 그리드가 들어옴

        -   초기 호출: update_menu_display("메인 메뉴")

### 메뉴 카드 (create_menu_item)

-   이모지, 이름, 가격, “담기” 버튼으로 구성된 카드 컨테이너.

-   "담기" 클릭 → add_to_cart(item).

## 팝업/오버레이 구조

이 앱은 팝업을 전부 **AlertDialog + page.overlay**로 띄우고, 닫을 때는 dialog.open=False 후 page.update()를 호출합니다. 일시 알림은 SnackBar 사용.

-   SnackBar

    -   메뉴 담을 때: “~가 장바구니에 추가되었습니다.”

-   장바구니 다이얼로그 (show_cart)

    -   제목 “장바구니”

    -   본문: cart_list(Row들로 품목/수량+/-/소계) + 구분선 + total_text(합계)

    -   액션: “계속 주문”(닫기), “결제하기”(→ proceed_to_payment)

    -   장바구니 내용/합계는 update_cart_display()가 갱신.

-   결제 확인 다이얼로그 (show_payment_dialog)

    -   주문 방식, 품목 요약, 총 결제금액, 결제수단(버튼은 UI만) 표시.

    -   액션: “취소”(닫기), “결제 완료”(→ complete_order)

-   주문 완료 다이얼로그 (complete_order 내부)

    -   체크 아이콘, 주문번호, 주문 접수 안내.

    -   “확인”(닫기).

-   관리자 로그인 다이얼로그 (show_admin_login)

    -   비밀번호 필드 입력 → SHA-256 해시 비교.

    -   성공 시 is_admin=True, 닫고 관리자 패널로.

-   관리자 패널 다이얼로그 (show_admin_panel)

    -   상단에 요약 카드 4개: 전체 주문 수/매출, 오늘 주문 수/매출.

    -   하단에 최근 주문 20건 카드 리스트(시간/주문방식/총액/항목 요약).

    -   데이터는 OrderManager.load_orders()로 로드.

    -   “닫기” 버튼.

## 주문 데이터 저장

데이터의 저장은 orders.json 파일을 활용함

-   load_orders() : 파일 존재 시 로드, 없으면 빈 리스트.

-   save_order(order_data) : 리스트에 append 후 파일로 저장.

-   get_next_order_number() : 기존 최대 주문번호 +1 (없으면 1).

## 주요 메서드와 이벤트 흐름

### 메뉴 / 장바구니

-   update_menu_display(category)

    -   menu_content를 비우고 카테고리 제목 + GridView(runs_count=3, max_extent=200) 구성.

    -   각 메뉴를 create_menu_item으로 카드화해 그리드에 추가.

    -   page.update()로 즉시 반영.

-   add_to_cart(item)

    -   동일 이름 품목 있으면 quantity += 1, 없으면 새 항목 추가.

    -   update_cart_badge()로 헤더 배지 숫자 갱신.

    -   SnackBar로 피드백 표시.

-   update_cart_display()

    -   cart_list를 현재 cart 내용으로 다시 그림.

    -   각 품목 행에는 수량 감소/증가 아이콘(update_quantity)과 소계 표시.

    -   합계 계산해 total_text 갱신.

-   update_quantity(item, change)

    -   수량 증감, 0 이하가 되면 해당 품목 제거.

    -   update_cart_display() + update_cart_badge() 호출.

-   update_cart_badge()

    -   장바구니 품목 수량 합을 배지 텍스트로 반영.

### 주문/결제

-   show_cart → proceed_to_payment → show_payment_dialog → complete_order

    -   장바구니 다이얼로그에서 “결제하기” 누르면 결제 확인 다이얼로그.

    -   “결제 완료” 누르면:

        -   order_number = get_next_order_number()

        -   주문 데이터 구성(시간 ISO8601, 주문방식, 품목, 총액)

        -   save_order(order_data) 호출

        -   장바구니 초기화(cart.clear() → update_cart_badge())

        -   완료 다이얼로그 표시

    -   change_order_type(e)

        -   RadioGroup 변경 이벤트로 order_type(“매장”/“포장”) 갱신.

### 관리자

-   show_admin_login

    -   입력 비밀번호 해시를 admin_password와 비교.

    -   실패 시 SnackBar로 안내.

    -   성공 시 show_admin_panel.

-   show_admin_panel

    -   주문 재로드 후 통계 계산:

        -   total_orders, total_revenue

        -   today_orders, today_revenue (오늘 날짜 기준 필터)

    -   최근 20건을 최신 순으로 카드 렌더링.

### 다이얼로그

-   close_dialog(dialog)

    -   dialog.open = False → page.update().

# main2.py

## 전체 구조

-   데이터: MENU_DATA (카테고리별 메뉴: 이름/가격/이미지 URL).

-   상태 저장: page.session["cart"]에 장바구니 배열 보관(앱 전역 접근).

-   레이아웃:

    -   상단 메인 영역 = Row

        -   좌측: 카테고리 버튼 컬럼(버튼 스타일 토글)

        -   중앙: 메뉴 GridView (카드로 메뉴 노출)

    -   하단 = 장바구니 바

        -   왼쪽: 장바구니 아이템 리스트(스크롤)

        -   오른쪽: 식사/포장 SegmentedButton, 총금액, “결제하기”

    -   팝업:

        -   주문 완료 AlertDialog 1종

        -   빈 카트 결제 시 **SnackBar**로 경고

## 패턴/특징 요약

-   상태 단일화: 장바구니는 전역 상태(page.session["cart"])로만 관리 → 어디서든 동일 소스.

-   이벤트-데이터 연결: control.data에 작업 대상 정보를 넣고 핸들러에서 꺼내 쓰는 패턴(카드 클릭/수량 변경 버튼 모두 동일).

-   스타일 토글: 카테고리 버튼 선택 상태를 스타일 객체 교체로 구현.

-   간결한 팝업 흐름: 주문 완료 시 단일 다이얼로그로 종료. (파일 저장/주문번호/관리자 통계 없음)
