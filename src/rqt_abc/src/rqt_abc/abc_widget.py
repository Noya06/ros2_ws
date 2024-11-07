import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QSizePolicy, QSpacerItem
from PyQt5 import uic
from PyQt5.QtGui import QPen
from PyQt5.QtCore import QPoint
from ament_index_python.resources import get_resource
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget
from python_qt_binding.QtGui import QPainter, QFont, QColor
from python_qt_binding.QtCore import Qt, QTimer
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleSimSubscriber(Node):
    def __init__(self, abc_widget):
        super().__init__('twist_subscriber')
        self.abc_widget = abc_widget
        # 機体の情報を購読
        self.subscription = self.create_subscription(Twist, '/geometry_msgs/msg/Twist', self.twist_callback, 10)

    def twist_callback(self, msg):
        # x座標を取得してウィジェットに渡す 要変更
        '''
        self.abc_widget.update_x_position(msg.x)
        self.abc_widget.update_y_position(msg.y)
        '''


class AbcWidget(QWidget):
    def __init__(self):
        super(AbcWidget, self).__init__()

        # パッケージパスとUIファイルのロード
        pkg_name = 'rqt_abc'
        _, package_path = get_resource('packages', pkg_name)
        ui_file = os.path.join(package_path, 'share', pkg_name, 'resource', 'abc_widget.ui')
        loadUi(ui_file, self)
        self.setObjectName('AbcWidget')

        # カウンタ初期化
        self.counter = 0
        self.min_count = 0

        # 1秒ごとにカウントアップするタイマーを設定
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_counter)
        
        # 初期状態ではタイマーを開始
        self.timer.start(1000)  # 1000msごとにカウントアップ

        # x座標の初期化
        self.x_position = 0.0
        self.y_position = 0.0

        # ROS 2の初期化がまだであれば初期化する
        if not rclpy.ok():
            rclpy.init()

        # ROS 2のノードを別スレッドで起動
        self.ros_node = TurtleSimSubscriber(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.spin_ros)
        self.timer.start(100)  # 100msごとにROSノードを実行

        # QStackedWidgetを取得
        self.stacked_widget = self.findChild(QStackedWidget, 'stackedWidget')
        self.stacked_widget.move(0, 0)

        # ページ1のボタンを取得し、クリックイベントを設定
        self.page1_menu_button_1 = self.findChild(QPushButton, 'menu1Button')
        self.page1_Uptime_button_1 = self.findChild(QPushButton, 'Uptime1Button')
        self.page1_Uptime_button_1.clicked.connect(self.show_page2)
        self.page1_Mileage_button_1 = self.findChild(QPushButton, 'Mileage1Button')
        self.page1_Mileage_button_1.clicked.connect(self.show_page3)

        # ページ2のボタンを取得し、クリックイベントを設定
        self.page2_menu_button_2 = self.findChild(QPushButton, 'menu2Button')
        self.page2_menu_button_2.clicked.connect(self.show_page1)
        self.page2_Uptime_button_2 = self.findChild(QPushButton, 'Uptime2Button')
        self.page2_Mileage_button_2 = self.findChild(QPushButton, 'Mileage2Button')
        self.page2_Mileage_button_2.clicked.connect(self.show_page3)

        # ページ3のボタンを取得し、クリックイベントを設定
        self.page3_menu_button_3 = self.findChild(QPushButton, 'menu3Button')
        self.page3_menu_button_3.clicked.connect(self.show_page1)
        self.page3_Uptime_button_3 = self.findChild(QPushButton, 'Uptime3Button')
        self.page3_Uptime_button_3.clicked.connect(self.show_page2)
        self.page3_Mileage_button_3 = self.findChild(QPushButton, 'Mileage3Button')

        # ボタンのサイズを固定
        self.page1_menu_button_1.setFixedSize(100, 50)
        self.page1_Uptime_button_1.setFixedSize(100, 50)  # 幅100、高さ50
        self.page1_Mileage_button_1.setFixedSize(100, 50)
        self.page2_menu_button_2.setFixedSize(100, 50)
        self.page2_Uptime_button_2.setFixedSize(100, 50)
        self.page2_Mileage_button_2.setFixedSize(100, 50)
        self.page3_menu_button_3.setFixedSize(100, 50)
        self.page3_Uptime_button_3.setFixedSize(100, 50)
        self.page3_Mileage_button_3.setFixedSize(100, 50)

        # ボタンのフォントを設定
        font = QFont()
        font.setPointSize(15)  # 文字サイズを15ポイントに設定

        self.page1_menu_button_1.setFont(font)
        self.page1_Uptime_button_1.setFont(font)
        self.page1_Mileage_button_1.setFont(font)
        self.page2_menu_button_2.setFont(font)
        self.page2_Uptime_button_2.setFont(font)
        self.page2_Mileage_button_2.setFont(font)
        self.page3_menu_button_3.setFont(font)
        self.page3_Uptime_button_3.setFont(font)
        self.page3_Mileage_button_3.setFont(font)

        self.set_page1_layout()
        self.set_page2_layout()
        self.set_page3_layout()

        # ページ1を表示
        self.stacked_widget.setCurrentIndex(0)

    def resizeEvent(self, event):
        super(AbcWidget, self).resizeEvent(event)  # 親クラスのresizeEventを呼び出す
        rect = self.rect()  # AbcWidgetの矩形を取得
        self.stacked_widget.setFixedSize(int(rect.width() / 4), rect.height())  # QStackedWidgetのサイズを設定    

    def spin_ros(self):
        # ROSのノードを実行
        rclpy.spin_once(self.ros_node, timeout_sec=0.1)

    def update_x_position(self, x):
        # 亀のx座標を更新し、再描画
        self.x_position = x
        self.update()  # ウィジェットを再描画（paintEventが呼ばれる）

    def update_y_position(self, y):
        # 亀のy座標を更新し、再描画
        self.y_position = y
        self.update()  # ウィジェットを再描画（paintEventが呼ばれる）

    
    def set_page1_layout(self):
        # ページ1のウィジェットを取得
        page1_widget = self.stacked_widget.widget(0)

        # 既存のレイアウトを削除
        if page1_widget.layout() is not None:
            old_layout = page1_widget.layout()
            QWidget().setLayout(old_layout)  # 古いレイアウトを解除

        # ページ1のレイアウトを作成
        self.page1_layout = QVBoxLayout()

        # menuButtonを1/5の位置に配置
        self.page1_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        menu_button_1_layout = QHBoxLayout()
        menu_button_1_layout.addStretch(1)
        menu_button_1_layout.addWidget(self.page1_menu_button_1, alignment=Qt.AlignCenter)
        menu_button_1_layout.addStretch(1)
        self.page1_layout.addLayout(menu_button_1_layout)

        # UptimeButtonを2/5の位置に配置
        self.page1_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        Uptime_button_1_layout = QHBoxLayout()
        Uptime_button_1_layout.addStretch(1)
        Uptime_button_1_layout.addWidget(self.page1_Uptime_button_1, alignment=Qt.AlignCenter)
        Uptime_button_1_layout.addStretch(1)
        self.page1_layout.addLayout(Uptime_button_1_layout)

        # batteryButtonを3/5の位置に配置
        self.page1_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        Mileage_button_1_layout = QHBoxLayout()
        Mileage_button_1_layout.addStretch(1)
        Mileage_button_1_layout.addWidget(self.page1_Mileage_button_1, alignment=Qt.AlignCenter)
        Mileage_button_1_layout.addStretch(1)
        self.page1_layout.addLayout(Mileage_button_1_layout)

        # 残りのスペースを下に追加
        self.page1_layout.addStretch(1)

        # ページ1に新しいレイアウトを設定
        page1_widget.setLayout(self.page1_layout)

    def set_page2_layout(self):
        # ページ2のレイアウトを作成
        page2_widget = self.stacked_widget.widget(1)
        self.page2_layout = QVBoxLayout()  # 縦方向のレイアウトを作成

        # menuButtonを1/5の位置に配置
        self.page2_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        menu_button_2_layout = QHBoxLayout()
        menu_button_2_layout.addStretch(1)
        menu_button_2_layout.addWidget(self.page2_menu_button_2, alignment=Qt.AlignCenter)
        menu_button_2_layout.addStretch(1)
        self.page2_layout.addLayout(menu_button_2_layout)

        # UptimeButtonを2/5の位置に配置
        self.page2_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        Uptime_button_2_layout = QHBoxLayout()
        Uptime_button_2_layout.addStretch(1)
        Uptime_button_2_layout.addWidget(self.page2_Uptime_button_2, alignment=Qt.AlignCenter)
        Uptime_button_2_layout.addStretch(1)
        self.page2_layout.addLayout(Uptime_button_2_layout)

        # MileageButtonを3/5の位置に配置
        self.page2_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        Mileage_button_2_layout = QHBoxLayout()
        Mileage_button_2_layout.addStretch(1)
        Mileage_button_2_layout.addWidget(self.page2_Mileage_button_2, alignment=Qt.AlignCenter)
        Mileage_button_2_layout.addStretch(1)
        self.page2_layout.addLayout(Mileage_button_2_layout)

        # 残りのスペースを下に追加
        self.page2_layout.addStretch(1)

        # ページ2に新しいレイアウトを設定
        page2_widget.setLayout(self.page2_layout)

    def set_page3_layout(self):
        # ページ3のレイアウトを作成
        page3_widget = self.stacked_widget.widget(2)
        self.page3_layout = QVBoxLayout()  # 縦方向のレイアウトを作成

        # menuButtonを1/5の位置に配置
        self.page3_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        menu_button_3_layout = QHBoxLayout()
        menu_button_3_layout.addStretch(1)
        menu_button_3_layout.addWidget(self.page3_menu_button_3, alignment=Qt.AlignCenter)
        menu_button_3_layout.addStretch(1)
        self.page3_layout.addLayout(menu_button_3_layout)

        # UptimeButtonを2/5の位置に配置
        self.page3_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        Uptime_button_3_layout = QHBoxLayout()
        Uptime_button_3_layout.addStretch(1)
        Uptime_button_3_layout.addWidget(self.page3_Uptime_button_3, alignment=Qt.AlignCenter)
        Uptime_button_3_layout.addStretch(1)
        self.page3_layout.addLayout(Uptime_button_3_layout)

        # MileageButtonを3/5の位置に配置
        self.page3_layout.addSpacerItem(QSpacerItem(20, self.rect().height() // 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        Mileage_button_3_layout = QHBoxLayout()
        Mileage_button_3_layout.addStretch(1)
        Mileage_button_3_layout.addWidget(self.page3_Mileage_button_3, alignment=Qt.AlignCenter)
        Mileage_button_3_layout.addStretch(1)
        self.page3_layout.addLayout(Mileage_button_3_layout)

        # 残りのスペースを下に追加
        self.page3_layout.addStretch(1)

        # ページ3に新しいレイアウトを設定
        page3_widget.setLayout(self.page3_layout)

    def show_page1(self):
        self.stacked_widget.setCurrentIndex(0)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.page1_menu_button_1.setStyleSheet("""
            background-color: white;
            color: red;
            border: 2px solid red;
            border-radius: 10px;
        """)
        self.page1_Uptime_button_1.setStyleSheet("background-color: white; color: black;")
        self.page1_Mileage_button_1.setStyleSheet("background-color: white; color: black;")
        self.update()

    def show_page2(self):
        self.stacked_widget.setCurrentIndex(1)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.page2_menu_button_2.setStyleSheet("background-color: white; color: black;")
        self.page2_Uptime_button_2.setStyleSheet("""
            background-color: white;
            color: red;
            border: 2px solid red;
            border-radius: 10px;
        """)
        self.page2_Mileage_button_2.setStyleSheet("background-color: white; color: black;")
        self.update()

    def show_page3(self):
        self.stacked_widget.setCurrentIndex(2)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.page3_menu_button_3.setStyleSheet("background-color: white; color: black;")
        self.page3_Uptime_button_3.setStyleSheet("background-color: white; color: black;")
        self.page3_Mileage_button_3.setStyleSheet("""
            background-color: white;
            color: red;
            border: 2px solid red;
            border-radius: 10px;
        """)
        self.update()
        
    def update_counter(self):
        self.counter += 1
        if self.counter >= 60:
            self.min_count += 1
            self.counter = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # 背景色を描画
        if self.stacked_widget.currentIndex() == 0:
            painter.setBrush(QColor("#FFFFFF"))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawRect(self.rect())

            # 表示するテキストとカウント
            title = "menu"
            x_title = "X"
            y_title = "Y"
            x_position_str = f"{self.x_position:.2f}"
            y_position_str = f"{self.y_position:.2f}"
            min_str = f"{self.min_count}m"  # カウンタ値を文字列化
            sec_str = f"{self.counter}s"  # カウンタ値を文字列化
            count_str = min_str + "" + sec_str
            subtitle1 = "Mileage"
            subtitle2 = "Uptime"

            # タイトルを中央に描画
            font = QFont()
            font.setPointSize(100)
            painter.setFont(font)
            title_width = painter.fontMetrics().horizontalAdvance(title)
            title_height = painter.fontMetrics().height()
            title_x = (self.rect().width() - title_width) / 2
            painter.setPen(QColor("#000000"))
            painter.drawText(int(title_x), int(self.rect().height() * 0.2), title)

            font.setPointSize(20)
            painter.setFont(font)
            subtitle1_width = painter.fontMetrics().horizontalAdvance(subtitle1)
            subtitle2_width = painter.fontMetrics().horizontalAdvance(subtitle2)
            subtitle1_x = (self.rect().width() - subtitle1_width) * 0.375
            subtitle2_x = (self.rect().width() - subtitle2_width) * 0.625
            painter.setPen(QColor("#000000"))
            painter.drawText(int(subtitle1_x), int(self.rect().height() * 0.25), subtitle1)
            painter.drawText(int(subtitle2_x), int(self.rect().height() * 0.25), subtitle2)

            # ラインを描画する
            painter.setPen(QPen(QColor("#000000"), 2))  # ラインの色を黒、幅を2ピクセルに設定
            start_point = QPoint(475, 510)  # ラインの始点 (x1, y1)
            end_point = QPoint(int(self.rect().width() - 475), 510)  # ラインの終点 (x2, y2)
            painter.drawLine(start_point, end_point)  # ラインを描画
            start_point = QPoint(int(self.rect().width() / 2), 200)  # ラインの始点 (x1, y1)
            end_point = QPoint(int(self.rect().width() / 2), 900)  # ラインの終点 (x2, y2)
            painter.drawLine(start_point, end_point)  # ラインを描画

            font.setPointSize(50)
            painter.setFont(font)

            # Xタイトルの幅を計算
            x_title_width = painter.fontMetrics().horizontalAdvance(x_title)
            y_title_width = painter.fontMetrics().horizontalAdvance(y_title)

            painter.setPen(QColor("#000000"))
            painter.drawText(600, int(self.rect().height() * 0.375), x_title)
            painter.drawText(600, int(self.rect().height() * 0.5), y_title)

            # x座標およびy座標の幅を計算
            x_position_width = painter.fontMetrics().horizontalAdvance(x_position_str)
            y_position_width = painter.fontMetrics().horizontalAdvance(y_position_str)

            # x座標およびy座標の描画位置を計算
            x_position_x = (self.rect().width() - x_position_width) * 0.4
            y_position_x = (self.rect().width() - y_position_width) * 0.4
            
            painter.drawText(int(x_position_x), int(self.rect().height() * 0.375), x_position_str)
            painter.drawText(int(y_position_x), int(self.rect().height() * 0.5), y_position_str)

            font.setPointSize(75)
            painter.setFont(font)
            count_position_width = painter.fontMetrics().horizontalAdvance(count_str)
            count_position_x = (int(subtitle2_x + (subtitle2_width / 2) - (count_position_width / 2)))
            painter.drawText(int(count_position_x), int(self.rect().height() * 0.425), count_str)

        elif self.stacked_widget.currentIndex() == 2:
            painter.setBrush(QColor("#FFFFFF"))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawRect(self.rect())

            # 表示するテキストとカウント
            title = "Mileage"
            x_title = "X"
            y_title = "Y"
            x_position_str = f"{self.x_position:.2f}"
            y_position_str = f"{self.y_position:.2f}"

            # タイトルを中央に描画
            font = QFont()
            font.setPointSize(100)
            painter.setFont(font)
            title_width = painter.fontMetrics().horizontalAdvance(title)
            title_x = (self.rect().width() - title_width) / 2
            painter.setPen(QColor("#000000"))
            painter.drawText(int(title_x), int(self.rect().height() * 0.2), title)

            # Xタイトルの幅を計算
            x_title_width = painter.fontMetrics().horizontalAdvance(x_title)
            y_title_width = painter.fontMetrics().horizontalAdvance(y_title)

            # XおよびYタイトルの描画位置を計算
            x_title_x = (self.rect().width() - x_title_width) * 0.4
            y_title_x = (self.rect().width() - y_title_width) * 0.4

            painter.setPen(QColor("#000000"))
            painter.drawText(int(x_title_x), int(self.rect().height() * 0.45), x_title)
            painter.drawText(int(y_title_x), int(self.rect().height() * 0.65), y_title)  # Yタイトルは50ピクセル下に描画

            # x座標を中央に描画
            font.setPointSize(100)
            painter.setFont(font)

            # x座標およびy座標の幅を計算
            x_position_width = painter.fontMetrics().horizontalAdvance(x_position_str)
            y_position_width = painter.fontMetrics().horizontalAdvance(y_position_str)

            # x座標およびy座標の描画位置を計算
            x_position_x = (self.rect().width() - x_position_width) * 0.55
            y_position_x = (self.rect().width() - y_position_width) * 0.55

            painter.drawText(int(x_position_x), int(self.rect().height() * 0.45), x_position_str)
            painter.drawText(int(y_position_x), int(self.rect().height() * 0.65), y_position_str)  # Y座標は100ピクセル下に描画

        else :
            painter.setBrush(QColor("#FFFFFF"))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawRect(self.rect())

            # 表示するテキストと座標
            title = "Uptime"

            # タイトルを中央に描画
            font = QFont()
            font.setPointSize(100)
            painter.setFont(font)
            title_width = painter.fontMetrics().horizontalAdvance(title)
            title_x = (self.rect().width() - title_width) / 2
            painter.setPen(QColor("#000000"))
            painter.drawText(int(title_x), int(self.rect().height() * 0.2), title)

        painter.end()  # ペインターを終了
       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AbcWidget()
    window.showMaximized()

    sys.exit(app.exec_())