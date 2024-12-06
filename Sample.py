
import win32com.client
import pythoncom
import time
import sys

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QMainWindow, QApplication
from loguru import logger


class Sample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.realtime_data_scrnum = 5000
        self.using_condition_name = ""
        self.realtime_registed_codes = []

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self._set_signal_slots()
        self._login_()

    def _login_(self):
        ret = self.kiwoom.dynamicCall("CommConnect()")
        if ret == 0:
            logger.info("로그인 창 열기 성공")
            
    def _set_signal_slots(self):
        self.kiwoom.OnEventConnect.connect(self._event_connect_)
        self.kiwoom.OnReceiveTrData.connect(self._get_stock_info_)
        
    def _event_connect_(self, errCode):
        if errCode == 0:
            logger.info("로그인 성공")
            self._after_login_()
        else:
            logger.info("로그인 실패")

    def _after_login_(self):
        self.kiwoom.dynamicCall("SetInputValue(QString,QString)", "종목코드", "000020")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식기본정보요청", "OPT10001", 0, "0101")

    def _get_stock_info_(self):
        result = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", "OPT10001", "주식기본정보요청", 0, "종목명")
        logger.info(result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom_api = Sample()
    sys.exit(app.exec())