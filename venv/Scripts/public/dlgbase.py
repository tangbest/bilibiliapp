# -*- coding: utf-8 -*-


class CDlgBase(object):
    # 界面按钮消息
    def onBtnMsg(self, *args):
       pass

    # 可勾选消息
    def onBoxMsg(self, *args):
       pass

    # 菜单按钮消息
    def onActionMsg(self, *args):
       pass

    # 居中
    def Center(self):
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 窗口置顶
    def setWindowTop(self, bTop):
        if bTop:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(Qt.Widget)
            self.show()

    # 点击关闭按钮
    def closeEvent(self, event):
        from PyQt5.QtWidgets import QMessageBox
        iReply = QMessageBox.question(self, "关闭", "确定退出?", QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.Yes)
        if iReply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

