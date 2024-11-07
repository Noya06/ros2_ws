# coding: UTF-8

from qt_gui.plugin import Plugin
from python_qt_binding.QtCore import QTimer

from rqt_abc.abc_widget import AbcWidget


# クラス名は参照されるので書き間違えないこと
# Abc とか書くとつらいです
class Abc(Plugin):

    def __init__(self, context):
        super(Abc, self).__init__(context)
        # オブジェクト名は間違えても動く？未調査
        self.setObjectName('Abc')

        self._context = context

        # ここでAbcWdigetをセットして楽しくなろう
        self._widget = AbcWidget()
        if context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

        # AbcWidgetは一定周期で更新したいのでQTimerを使う
        self._timer = QTimer()
        self._timer.timeout.connect(self._widget.update)
        # 16 msec 周期で更新させる
        self._timer.start(16)


    def shutdown_plugin(self):
        # 終了時はタイマーを止める
        self._timer.stop()
        pass


    def save_settings(self, plugin_settings, instance_settings):
        # セーブ機能は何もしない
        pass


    def restore_settings(self, plugin_settings, instance_settings):
        # リストア機能は何もしない
        pass

