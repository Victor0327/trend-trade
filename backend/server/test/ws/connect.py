import websocket
import json
import time

class Binance_websocket:
    def __init__(self, symbol):
        self.symbol = symbol.lower()  # 转成小写
        self.wss_url = "wss://stream.binance.com:9443/stream?streams={}".format(self.symbol)

    def on_open(self, ws):
        print("on_open")  # 连接成功
        data = {
            "method": "SUBSCRIBE",
            "params": ["{}@trade".format(self.symbol)],
            "id": 1
        }
        ws.send(json.dumps(data))  # 以json格式发送

    def on_close(self, ws):
        print("on_close")  # 连接关闭

    def on_error(self, ws, error):
        print("on_error")  # 连接错误
        print(error)  # 返回错误信息

    def on_message(self, ws, msg):
        msg = json.loads(msg)  # msg 返回的是字符串要转成json格式

        if 'data' in msg:  # 因为第一行不是数据，排除掉非数据的打印
            data = msg['data']
            event_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['E'] / 1000))
            print(f"Event Time: {event_time}, Symbol: {data['s']}")

    def run(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.wss_url,
                                    on_open=self.on_open,
                                    on_close=self.on_close,
                                    on_error=self.on_error,
                                    on_message=self.on_message)

        ws.run_forever()


# 使用示例
symbol = "btcusdt"
ws_client = Binance_websocket(symbol)
ws_client.run()
