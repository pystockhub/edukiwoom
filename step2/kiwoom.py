import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        if err_code == 0:
            print("로그인 성공")
        else:
            print("로그인 실패", err_code)

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if rqname == "opt10001_req":
            self._opt10001(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt10001(self, rqname, trcode):
        self.name = self._comm_get_data(trcode, "", rqname, 0, "종목명")
        self.volume = self._comm_get_data(trcode, "", rqname, 0, "거래량")
        self.pbr = self._comm_get_data(trcode, "", rqname, 0, "PBR")
        self.per = self._comm_get_data(trcode, "", rqname, 0, "PER")
        self.roe = self._comm_get_data(trcode, "", rqname, 0, "ROE")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    kiwoom.set_input_value("종목코드", "000660")
    kiwoom.comm_rq_data("opt10001_req", "opt10001",  0, "0101")
    print(kiwoom.roe)

