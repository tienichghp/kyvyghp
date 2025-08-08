from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock

import random
import string
import datetime


class ProxyConfigPopup(Popup):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.title = "Cấu hình Proxy"
        self.size_hint = (0.9, 0.5)
        self.main_app = main_app

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.proxy_input = TextInput(text="\n".join(main_app.proxies),
                                     multiline=True,
                                     size_hint_y=0.8,
                                     background_color=[1, 0.9, 0.95, 1],
                                     foreground_color=[0.4, 0, 0.2, 1])
        btn_save = Button(text="Lưu Proxy", size_hint_y=0.2, background_color=[1, 0.4, 0.7, 1])
        btn_save.bind(on_release=self.save_proxy)

        layout.add_widget(self.proxy_input)
        layout.add_widget(btn_save)

        self.content = layout


class MainLayout(BoxLayout):
    account_type = StringProperty("")
    running = BooleanProperty(False)
    proxy_mode = BooleanProperty(False)
    proxies = ListProperty([])
    log_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=15, padding=15, **kwargs)

        # Header
        header = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=[10, 10])
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1, 0.75, 0.85, 1)  # hồng pastel
            self.rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_rect, pos=self._update_rect)

        title = Label(text="[b]Tool Reg Clone FB - TikTok[/b]",
                      markup=True,
                      font_size=24,
                      color=[0.7, 0.1, 0.4, 1],
                      size_hint_x=0.8,
                      valign='middle',
                      halign='left')
        self.label_account_type = Label(text="Loại tài khoản: [color=#a8004a][Chưa chọn][/color]",
                                        markup=True,
                                        font_size=16,
                                        size_hint_x=0.2,
                                        valign='middle',
                                        halign='right')
        header.add_widget(title)
        header.add_widget(self.label_account_type)
        self.add_widget(header)

        # Input số lượng
        qty_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        qty_label = Label(text="Số lượng:", size_hint_x=0.3, color=[0.6, 0.1, 0.3, 1], bold=True)
        self.input_quantity = TextInput(text="1", multiline=False, input_filter='int', size_hint_x=0.7,
                                        background_color=[1, 0.9, 0.95, 1],
                                        foreground_color=[0.5, 0, 0.2, 1])
        qty_layout.add_widget(qty_label)
        qty_layout.add_widget(self.input_quantity)
        self.add_widget(qty_layout)

        # Nút chọn loại tài khoản
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.btn_fb = Button(text="Tạo Facebook",
                             background_color=[1, 0.6, 0.8, 1],
                             color=[0.5, 0, 0.2, 1],
                             bold=True)
        self.btn_tiktok = Button(text="Tạo TikTok",
                                 background_color=[1, 0.6, 0.8, 1],
                                 color=[0.5, 0, 0.2, 1],
                                 bold=True)
        self.btn_fb.bind(on_release=lambda x: self.set_account_type("Facebook"))
        self.btn_tiktok.bind(on_release=lambda x: self.set_account_type("TikTok"))
        btn_layout.add_widget(self.btn_fb)
        btn_layout.add_widget(self.btn_tiktok)
        self.add_widget(btn_layout)

        # Nút bắt đầu / dừng / lưu
        control_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.btn_start = Button(text="Bắt đầu",
                                background_color=[1, 0.4, 0.7, 1],
                                color=[1, 1, 1, 1],
                                bold=True)
        self.btn_stop = Button(text="Dừng",
                               background_color=[0.9, 0.1, 0.4, 1],
                               color=[1, 1, 1, 1],
                               bold=True,
                               disabled=True)
        self.btn_save = Button(text="Lưu acc",
                               background_color=[1, 0.7, 0.9, 1],
                               color=[0.5, 0, 0.2, 1],
                               bold=True)
        self.btn_start.bind(on_release=self.start_creation)
        self.btn_stop.bind(on_release=self.stop_creation)
        self.btn_save.bind(on_release=self.save_accounts)
        control_layout.add_widget(self.btn_start)
        control_layout.add_widget(self.btn_stop)
        control_layout.add_widget(self.btn_save)
        self.add_widget(control_layout)

        # Checkbox proxy
        proxy_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.checkbox_proxy = CheckBox()
        self.checkbox_proxy.bind(active=self.on_proxy_checkbox)
        proxy_label = Label(text="Chạy bằng Proxy",
                            color=[0.6, 0.1, 0.3, 1],
                            bold=True)
        proxy_layout.add_widget(self.checkbox_proxy)
        proxy_layout.add_widget(proxy_label)
        self.add_widget(proxy_layout)

        # Log
        self.log_box = TextInput(readonly=True,
                                 multiline=True,
                                 size_hint_y=None,
                                 height=200,
                                 font_name="RobotoMono-Regular",
                                 background_color=[1, 0.95, 0.97, 1],
                                 foreground_color=[0.4, 0, 0.2, 1])
        self.add_widget(self.log_box)

        # Nội dung tạo tài khoản
        self.quantity = 1
        self.created_count = 0

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def log_append(self, text):
        self.log_box.text += text + "\n"
        self.log_box.cursor = (0, len(self.log_box.text))

    def set_account_type(self, acc_type):
        self.account_type = acc_type
        self.label_account_type.text = f"Loại tài khoản: [color=#a8004a]{acc_type}[/color]"
        self.log_box.text = ""
        self.log_append(f"Đã chọn tạo tài khoản {acc_type}")

    def on_proxy_checkbox(self, checkbox, value):
        self.proxy_mode = value
        self.log_append(f"Chạy bằng proxy: {'Bật' if value else 'Tắt'}")

    def start_creation(self, instance):
        if self.running:
            return
        qty_text = self.input_quantity.text.strip()
        if not qty_text.isdigit() or int(qty_text) <= 0:
            self.log_append("[Lỗi] Số lượng không hợp lệ!")
            return
        if not self.account_type:
            self.log_append("[Lỗi] Chưa chọn loại tài khoản!")
            return
        self.quantity = int(qty_text)
        self.created_count = 0
        self.running = True
        self.btn_start.disabled = True
        self.btn_stop.disabled = False
        self.log_box.text = ""
        self.log_append(f"Bắt đầu tạo {self.quantity} tài khoản {self.account_type}...")
        self._event = Clock.schedule_interval(self.create_account_step, 3)  # delay 3 giây

    def stop_creation(self, instance):
        if not self.running:
            return
        self.running = False
        self.btn_start.disabled = False
        self.btn_stop.disabled = True
        if hasattr(self, "_event"):
           self._event.cancel()
        self.log_append("Đã dừng tạo tài khoản.")

    def create_account_step(self, dt):
        if self.created_count >= self.quantity:
            self.log_append(f"[Hoàn thành] Đã tạo {self.created_count} tài khoản {self.account_type}")
            self.running = False
            self.btn_start.disabled = False
            self.btn_stop.disabled = True
            return False

        email = self.fake_email()
        name = self.fake_name()
        dob = self.fake_dob()
        pwd = self.fake_password()

        self.log_append(f"Tạo tài khoản {self.created_count+1}/{self.quantity}:")
        self.log_append(f"  Email ảo: {email}")
        self.log_append(f"  Họ tên: {name}")
        self.log_append(f"  Ngày sinh: {dob.strftime('%d/%m/%Y')} (Tuổi: {self.get_age(dob)})")
        self.log_append(f"  Mật khẩu: {pwd}")

        if self.proxy_mode and self.proxies:
            proxy = random.choice(self.proxies)
            self.log_append(f"  [Proxy] Chạy với proxy: {proxy}")

        self.log_append(f"[Thành công] Tạo tài khoản thành công!\n")

        self.created_count += 1

    def fake_email(self):
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return prefix + "@" + random.choice(domains)

    def fake_name(self):
        ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ"]
        ten_dem = ["Văn", "Thị", "Hữu", "Minh", "Quang", "Hồng", "Thu", "Anh", "Ngọc", "Thanh"]
        ten = ["An", "Bình", "Chi", "Dương", "Giang", "Hải", "Khanh", "Lan", "Mai", "Nam", "Oanh", "Phúc", "Quỳnh", "Sơn", "Thảo"]
        return f"{random.choice(ho)} {random.choice(ten_dem)} {random.choice(ten)}"

    def fake_dob(self):
        today = datetime.date.today()
        start_year = today.year - 52
        end_year = today.year - 18
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return datetime.date(year, month, day)

    def get_age(self, dob):
        today = datetime.date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def fake_password(self):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=8))

    def save_accounts(self, instance):
        if not self.log_box.text.strip():
            self.log_append("[Lỗi] Không có dữ liệu để lưu!")
            return
        try:
            with open("accounts.txt", "w", encoding="utf-8") as f:
                f.write(self.log_box.text)
            self.log_append("[Thành công] Đã lưu log vào file accounts.txt")
        except Exception as e:
            self.log_append(f"[Lỗi] Lỗi khi lưu file: {e}")

    def open_proxy_config(self, instance):
        popup = ProxyConfigPopup(main_app=self)
        popup.open()


class MyApp(App):
    def build(self):
        self.title = "Tool Reg Clone FB - TikTok"
        self.proxies = []
        main_layout = MainLayout()
        main_layout.proxies = self.proxies
        # Đăng ký nút cấu hình proxy vào header
        # Thêm nút cấu hình proxy bên header
        btn_config = Button(text="Cấu hình Proxy",
                            size_hint=(None, None),
                            size=(140, 40),
                            pos_hint={'right': 1, 'top': 1},
                            background_color=[1, 0.4, 0.7, 1],
                            color=[1, 1, 1, 1],
                            bold=True)
        btn_config.bind(on_release=main_layout.open_proxy_config)
        # Thêm nút config vào header (phía phải)
        main_layout.children[0].add_widget(btn_config)
        return main_layout


if __name__ == '__main__':
    MyApp().run()