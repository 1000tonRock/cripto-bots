import websocket, json, pprint
import config
import talocal
from binance.client import Client
from binance.enums import *
from datetime import datetime

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 69
RSI_OVERSOLD = 31
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.007
MA_PERIOD = 5
MA2_PERIOD = 10

closes = []
rsi = []
ma = []
in_position = False
hit_rsi_30 = False
hit_rsi_70 = False

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        log = open('RsiMaBotLogETH.txt', 'a')
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
        #print("closes")
        #print(closes)
        
        if len(closes) > MA2_PERIOD:
            #rsi.append(ta.RSI(closes, RSI_PERIOD))
            #print("all rsis calculated so far")
            #print(rsi)
            last_rsi = talocal.RSI(closes, RSI_PERIOD)
            print("the current rsi is {}".format(last_rsi))
            #if last_rsi > 50:
            #    hit_rsi_30 = False
            #if last_rsi < 50:
            #    hit_rsi_70 = False

            #ma.append(ta.MA(closes, MA_PERIOD))
            #print("all MAs calculated so far")
            #print(ma)
            last_ma = talocal.MA(closes, MA_PERIOD)
            print("the current ma is {}".format(last_ma))
            last_ma2 = talocal.MA(closes, MA2_PERIOD)
            print("the current ma2 is {}".format(last_ma2))
                
            if last_rsi > RSI_OVERBOUGHT:
                hit_rsi_70 = True
                hit_rsi_30 = False
                print("RSI IS OVERBOUGHT")

            if last_rsi < RSI_OVERSOLD:
                hit_rsi_30 = True
                hit_rsi_70 = False
                print("RSI IS OVERSOLD")
            
            print("Debug out sell")
            if hit_rsi_70 and last_ma2 > last_ma:
                print("Debug in sell")
                hit_rsi_70 = False
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")

                    log = open('RsiMaBotLogETH.txt', 'a')
                    log.write("Sell! Sell! Sell!: {}\n".format(last_close))
                    log.write("MA1: {}\n".format(last_ma))
                    log.write("MA2: {}\n".format(last_ma2))
                    log.write("Rsi: {}\n".format(last_rsi))
                    log.write("Timestamp: {}\n".format(t))
                    log.close()
                    in_position = False

                    # put binance sell logic here
                    #order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    #if order_succeeded:
                        
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")


            print("debug out buy")
            if hit_rsi_30 and last_ma2 < last_ma:
                print("debug in buy")
                hit_rsi_30 = False
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    
                    print("Oversold! Buy! Buy! Buy!")

                    log = open('RsiMaBotLogETH.txt', 'a')
                    log.write("Buy! Buy! Buy!: {}\n".format(last_close))
                    log.write("MA1: {}\n".format(last_ma))
                    log.write("MA2: {}\n".format(last_ma2))
                    log.write("Rsi: {}\n".format(last_rsi))
                    log.write("Timestamp: {}\n".format(t))
                    log.close()
                    in_position = True

                    # put binance buy order logic here
                    #order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    #if order_succeeded:
                        
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
while True:
    print("New connection")
    ws.run_forever()
    