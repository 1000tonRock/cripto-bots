import config
import ta
import pandas as pd
import time
from binance.client import Client
from binance.enums import *
import winsound

MA_PERIOD = 20
RSI_PERIOD = 6
LOOKBACK_PERIOD = 25
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.004

in_position = False
sell_position = False
last_buy = 0
sl_value = 0
p_value = 0
doc = 'log.txt'
FrameConnection = True
buyprice = 0


client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    global doc
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        buyprice = float(order['fills'][0]['price'])
    except Exception as e:
        print("an exception occured - {}".format(e))
        frequency = 2500  # Set Frequency To 2500 Hertz
        duration = 1000  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)
        log = open(doc, 'a')
        log.write("an exception occured - {}\n".format(e))
        log.close()
        return [False]

    return [True, buyprice]


def getdata(symbol,interval,lookback):
    global FrameConnection
    try:
        frame = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback + ' min ago UTC'))
        frame = frame.iloc[:,:6]
        frame.columns = ['Time','Open','High','Low','Close','Volume']
        frame = frame.set_index('Time')
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame = frame.astype(float)
        FrameConnection = True
        return frame

    except Exception as e:
        print("an exception occured - {}".format(e))
        print()
        FrameConnection = False
        return False



def tecnicals(df):
    df['rsi'] = ta.momentum.rsi(df.Close, window=RSI_PERIOD)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df['sma0'] = ta.trend.sma_indicator(df.Close, window=5)
    df['sma1'] = ta.trend.sma_indicator(df.Close, window=10)
    df['sma2'] = ta.trend.sma_indicator(df.Close, window=MA_PERIOD)
    df['K'] = ta.momentum.stoch(df.High,df.Low,df.Close, window=RSI_PERIOD, smooth_window=3)
    df['D'] = df['K'].rolling(3).mean()
    df['bolll'] = ta.volatility.bollinger_lband(df.Close)
    df['bollh'] = ta.volatility.bollinger_hband(df.Close)
    df['bollm'] = ta.volatility.bollinger_mavg(df.Close)
    df.dropna(inplace=True)



def getframe():
    df = getdata(TRADE_SYMBOL, '1m', '100')
    if not FrameConnection:
        return False
    tecnicals(df)
    return df

def strategy(df):
    global in_position, last_buy, doc, sell_position, buyprice,sl_value,p_value

    #diminui o frame
    df = df.iloc[-LOOKBACK_PERIOD:]

    #verifica se existe
    kl = df[df.K < RSI_OVERSOLD]
    kh = df[df.K > RSI_OVERBOUGHT]
    dl = df[df.D < RSI_OVERSOLD]
    dh = df[df.D > RSI_OVERBOUGHT]

    K_low = len(kl.index) > 0
    K_high = len(kh.index) > 0
    D_low = len(dl.index) > 0
    D_high = len(dh.index) > 0

    #define os atuais
    close_now = float(df.Close.iloc[-1])
    macd_now = float(df.macd.iloc[-1])
    rsi_now = float(df.rsi.iloc[-1])
    K = float(df.K.iloc[-1])
    D = float(df.D.iloc[-1])
    time_now = df.index[-1]
        
    print('atual close: {}'.format(close_now))
    print('atual MACD: {}'.format(macd_now))
    print('atual RSI: {}'.format(rsi_now))
    print('atual %K: {}'.format(K))
    print('atual %D: {}'.format(D))
    print('atual time: {}'.format(time_now))
    print()
    print("buy position = {}".format(in_position))
    print("sell position = {}".format(sell_position))
    #print(df)
    print()

    #define as flag booleanas
    rsi = rsi_now > 50
    macd = macd_now > 0
    S_low = K_low and D_low
    S_high = K_high and D_high
    stoch = (K < 70) and (K > 30) and (D < 70) and (D > 30)

    #define stoploss, se nessesario
    if in_position:
        stop_loss = close_now < sl_value
        profit = close_now > p_value
    
    if sell_position:
        stop_loss = close_now > sl_value
        profit = close_now < p_value

    if (not in_position) and (not sell_position):
        stop_loss = False
        profit = False
    

    #estrategia de posicao de venda
    if S_high and stoch and (not rsi) and (not macd) and (not in_position) and (not sell_position):
        sell_position = True  
        sl_value = max(kh.Close)

        if (close_now * (1.0015) ) < sl_value:
            sl_value = close_now*(1.0015)
            
        p_value  = close_now - ((sl_value - close_now) * 1.5)

    
    #estrategia de saida
    if stop_loss or profit:
        if in_position:
            print("Sell! Sell! Sell!")

            # put binance sell logic here
            #order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
            order_succeeded = [True,close_now]

            if order_succeeded[0]:
                sellprice = order_succeeded[1]
                log = open(doc, 'a')
                log.write("Sell! Sell! Sell!: {}\n".format(sellprice))
                log.write("MACD: {}\n".format(macd_now))
                log.write("Rsi: {}\n".format(rsi_now))
                log.write("%K: {}\n".format(K))
                log.write("%D: {}\n".format(D))
                log.write("Time: {}\n".format(time_now))
                log.close()
                in_position = False
                
        else:
            print("We don't own any. Nothing to do.")
            sell_position = False

   
    #esttrategia de posição de compra
    if S_low and stoch and rsi and macd and (not sell_position):
        if in_position:
            print("It is oversold, but you already own it, nothing to do.")
        else:
                    
            print("Oversold! Buy! Buy! Buy!")
            # put binance buy order logic here

            #order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            order_succeeded =[True,close_now]

            if order_succeeded[0]:
                buyprice = order_succeeded[1]
                last_buy = buyprice

                log = open(doc, 'a')
                log.write("Buy! Buy! Buy!: {}\n".format(last_buy))
                log.write("MACD: {}\n".format(macd_now))
                log.write("Rsi: {}\n".format(rsi_now))
                log.write("%K: {}\n".format(K))
                log.write("%D: {}\n".format(D))
                log.write("Time: {}\n".format(time_now))
                log.close()
                in_position = True

                sl_value = min(kl.Close)

                if (close_now * (0.995) ) > sl_value:
                    sl_value = close_now*(0.995)
            
                p_value  = ((close_now-sl_value) * 1.5) + close_now

def main():
    while True:
        gt = getframe()

        if not FrameConnection:
            print("waiting for connection")
            print()
            time.sleep(1)
            continue

        strategy(gt)
        time.sleep(1)

if __name__ == '__main__':
    main()