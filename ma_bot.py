import websocket, json, pprint
import config
import talocal
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.004
MA_PERIOD = 5
MA2_PERIOD = 10

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        log = open('log.txt', 'a')
        log.write("an exception occured - {}\n".format(e))
        log.close()

        return False

    return True

def on_open(ws):
    print('opened connection')



def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position

    print('received message')
    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']
    t = int(candle['T'])

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        last_close = closes[-1]
        print("closes")
        print(closes)
        
        if len(closes) > MA2_PERIOD:
            last_ma = talocal.MA(closes, MA_PERIOD)
            print("the current ma1 is {}".format(last_ma))
            last_ma2 = talocal.MA(closes, MA2_PERIOD)
            print("the current ma2 is {}".format(last_ma2))

                

            if last_ma2 > last_ma:
                if in_position:
                    print("Sell! Sell! Sell!")
                    
                    log = open('MaBotLog.txt', 'a')
                    log.write("Sell! Sell! Sell!: {}\n".format(last_close))
                    log.write("MA1: {}\n".format(last_ma))
                    log.write("MA2: {}\n".format(last_ma2))
                    log.write("Timestamp: {}\n".format(t))
                    log.close()
                    in_position = False

                    # put binance sell logic here
                    #order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    #if order_succeeded:
                    #    in_position = False
                else:
                    print("We don't own any. Nothing to do.")

            if last_ma2 < last_ma:
                if in_position:
                    print("You already own it, nothing to do.")
                else:
                    
                    print("Buy! Buy! Buy!")

                    log = open('MaBotLog.txt', 'a')
                    log.write("Buy! Buy! Buy!: {}\n".format(last_close))
                    log.write("MA1: {}\n".format(last_ma))
                    log.write("MA2: {}\n".format(last_ma2))
                    log.write("Timestamp: {}\n".format(t))
                    log.close()
                    in_position = True

                    # put binance buy order logic here
                    #order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    #if order_succeeded:
                    #    in_position = True

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
while True:
    print("New connection")
    ws.run_forever()
    