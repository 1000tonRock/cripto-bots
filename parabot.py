import ta   
import pandas as pd
import time
import config
from bot import order, doc
from binance.client import Client
from binance.enums import *
import winsound
from beep import exitbeep, upbeep, downbeep
from datetime import datetime

TRADE_SYMBOL = "GMTBUSD"
TRADE_QUANTITY = 0.0008
subtraction = 0.0001
stoploss = False
profit = False
doc = "log.txt"
in_position = False
sell_position = False
p_value = 0
sl_value = 0
FrameConnection = True
error = False
kill = False

client = Client(config.API_KEY, config.API_SECRET)

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



def tec(df):
    df['ema0'] = ta.trend.ema_indicator(df.Close, window=5)
    df['ema1'] = ta.trend.ema_indicator(df.Close, window=10)
    df['ema2'] = ta.trend.ema_indicator(df.Close, window=20)
    df['ema3'] = ta.trend.ema_indicator(df.Close, window=200)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=True)
    df['psar_up'] = ta.trend.psar_up(df.High,df.Low,df.Close)
    df['psar_down'] = ta.trend.psar_down(df.High,df.Low,df.Close)

def getframe():
    df = getdata(TRADE_SYMBOL,'1m','300')
    if not FrameConnection:
        return False
    tec(df)
    #print(df)
    return df


def strategy(df):
    global in_position, last_buy, doc, sell_position, buyprice,sl_value,p_value, error, kill


    close_now = float(df.Close.iloc[-2])
    close_alt = float(df.Close.iloc[-1])
    macd_now = float(df.macd.iloc[-2])
    time_now = df.index[-2]

    print('atual close: {}'.format(close_now))
    print('atual MACD: {}'.format(macd_now))
    print('atual time: {}'.format(time_now))
    print()
    print("buy position = {}".format(in_position))
    print("sell position = {}".format(sell_position))
    print()


    #define flag
    p_down = df.psar_down.iloc[-2] > 0
    p_up = df.psar_up.iloc[-2] > 0

    ema = df.ema.iloc[-2] < close_now
    macd = macd_now > 0

    #define stoploss, se nessesario
    if in_position:
        stoploss = (close_now < sl_value)
        profit = close_now > p_value

    if sell_position:
        stoploss = close_now > sl_value
        profit = close_now < p_value

    if (not in_position) and (not sell_position):
        stoploss = False
        profit = False

    if p_up and macd and (not sell_position):
        #buy
        if in_position:
            print("It is oversold, but you already own it, nothing to do.")
        else:
                        
            print("Oversold! Buy! Buy! Buy!")
            # put binance buy order logic here

            #order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            order_succeeded =[True,close_alt]

            if order_succeeded[0]:
                buyprice = order_succeeded[1]
                last_buy = buyprice

                log = open(doc, 'a')
                log.write("Buy! Buy! Buy!: {}\n".format(last_buy))
                log.write("MACD: {}\n".format(macd_now))
                log.write("Time: {}\n".format(time_now))
                log.write("\n")
                log.close()
                in_position = True

                #sl_value = float(df.psar_up.iloc[-2])

                #if (close_now * (0.9999) ) > sl_value:
                    
                sl_value = close_now#*(0.9999)
                    
                
                p_value  = ((close_now-(close_now*(0.9985))))  + close_now
                #(close_now*(0.9985))

                #upbeep()
                time.sleep(60)


    if (not ema) and p_down and (not in_position) and (not sell_position):
        #sell
        sell_position = True  
        sl_value = float(df.psar_down.iloc[-1])

        if (close_now * (1.005) ) < sl_value:
            sl_value = close_now*(1.005)
                
        p_value  = close_now - ((sl_value - close_now))

        #downbeep()
        time.sleep(60)
        

    if (stoploss or profit) or (((not macd) or (not p_up)) and in_position):
        if in_position:
            print("Sell! Sell! Sell!")
            if not error:
                k = TRADE_QUANTITY

            # put binance sell logic here
            #order_succeeded = order(SIDE_SELL, k, TRADE_SYMBOL)
            order_succeeded = [True, close_alt ]

            if order_succeeded[0]:
                sellprice = order_succeeded[1]
                log = open(doc, 'a')
                log.write("Sell! Sell! Sell!: {}\n".format(sellprice))
                log.write("MACD: {}\n".format(macd_now))
                log.write("Time: {}\n".format(time_now))
                log.write("\n")
                log.close()
                in_position = False
                #downbeep()
                time.sleep(60)

                if error:
                    kill = True
            if not order_succeeded[0]:
                error = True
                k = k - subtraction


                
        else:
            print("We don't own any. Nothing to do.")
            sell_position = False
            #upbeep()
            time.sleep(60)

def main():
    log = open(doc, 'a')
    log.write("{}\n".format(TRADE_SYMBOL))
    log.write("{}\n".format(str(datetime.now())))
    log.write("\n")
    log.close()
    while True:

        if kill:
            exitbeep()

            exit()

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
    
