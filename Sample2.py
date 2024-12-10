from flask import Flask
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QAxContainer import QAxWidget
from flask_socketio import SocketIO
import sys
from threading import Thread
from loguru import logger
import uvicorn
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# 전역 변수
login_event_result = None
login_event = threading.Event()  # 로그인 상태를 기다리기 위한 이벤트

@app.route('/')
def _login_():
    # 로그인 작업을 별도의 스레드에서 실행
    login_thread = Thread(target=login_process)
    login_thread.start()

    # 타임아웃을 위한 타이머 설정
    timeout_thread = threading.Timer(15, timeout_callback)
    timeout_thread.start()

    # 로그인 작업이 끝날 때까지 대기
    login_event.wait()  # 로그인 작업이 완료될 때까지 대기

    # 로그인 상태 반환
    return f"로그인 상태: {login_event_result}"

def login_process():
    global login_event_result

    qt_app = QApplication(sys.argv)
    widget = QWidget()
    ax_widget = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')  # 예시로 ActiveX 컨트롤
    ax_widget.OnEventConnect.connect(_event_connect_)
    ret = ax_widget.dynamicCall("CommConnect()")
    if ret == 0:
        logger.info("로그인 창 열기 성공")
    qt_app.exec_()

def _event_connect_(errCode):
    global login_event_result

    if errCode == 0:
        login_event_result = "로그인 성공"
        logger.info("로그인 성공")
    else:
        login_event_result = "로그인 실패"
        logger.info("로그인 실패")

    # 로그인 상태 이벤트 발생
    login_event.set()  # 로그인 결과를 기다리고 있는 Flask 라우트에 알림

    # 클라이언트에게 로그인 상태 전송
    socketio.emit('login_status', {'status': login_event_result})

def run_flask():
    app.run(debug=True, use_reloader=False)  # use_reloader=False는 스레드와 충돌 방지

def timeout_callback():
    global login_event_result  # 전역 변수를 사용하므로 global 키워드 추가
    if login_event_result is None:
        login_event_result = "로그인 실패 (타임아웃)"
        # 타임아웃 발생 시 로그인 상태 이벤트 발생
        login_event.set()
        socketio.emit('login_status', {'status': login_event_result})

# Flask를 별도 스레드로 실행
flask_thread = Thread(target=run_flask)
flask_thread.start()

# Uvicorn을 통해 Flask 실행
uvicorn.run(app, host="0.0.0.0", port=5000)
