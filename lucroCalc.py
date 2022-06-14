def d():
    doc = input("Nome do documento: ")
    return doc

def calc(doc):
    
    print(doc)
    print()
    print()

    arc = open( doc , 'r')
    line = arc.readlines()
    arc.close()

    closes = []
    times =[]
    ma1s = []
    ma2s = []
    good = 0
    bad = 0
    perda = 0

    title = line[0]


    for i in range(1,len(line)):
        num1 = line[i].split(": ")
        if num1[0] == "Rsi" or num1[0] == "%K" or num1[0] == "D":
            continue
        
        if num1[0] == "Time" or num1[0] == "TS":
            time = str(num1[1][:-1])
            times.append(time)
        
        if num1[0] == "MACD":
            ma1 = float(num1[1][:-1])
            ma1s.append(ma1)

        elif num1[0] == "Buy! Buy! Buy!" or num1[0] == "Sell! Sell! Sell!":    
            close = float(num1[1][:-1])
            closes.append(close)

    print("Closes:{}".format(closes))
    print()
    print("MACD:{}".format(ma1s))
    print()
    print("Time:{}".format(times))
    print()
    print()
    

    jump = 1
    L = []
    cont = 0
    lost = []
    for c in range(len(closes)):
        if c == jump:
            continue

        try:
            print([closes[c],closes[c+1]])
            dt = times[c]
            print("Time: {}".format(dt))
            dt = times[c + 1]
            print("Time: {}".format(dt))

            lucro = (closes[c+1])/(closes[c]) - 1
            
            if lucro > 0:
                good = good + 1
            else:
                bad = bad + 1
                lost.append(lucro)
                if perda > lucro:
                    perda = lucro


            print("Lucro: {:.2f}%".format(lucro*100))
            print()
            L.append(lucro)

            jump = c+1
            cont = cont +1

        except Exception as e:
            print("fim do array - {}".format(e))


        try:
            antilucro = (closes[c+2]/closes[c+1]) -1
            if antilucro < 0:
                good = good + 1
            else:
                bad = bad + 1
            print("Lucro perdido: {:.2f}%".format(antilucro*100))
            print()
        except Exception as e:
            print("fim do array - {}".format(e))

        

    print()
    use =1
    puse = 1
    for l in range(len(L)):
        use = use + (use * L[l])

        if L[l] > 0:
            puse = puse +(puse * L[l])
    
    media = 0
    for i in lost:
        media = media + i
    media = (media/(len(lost)))


    use = use - 1
    puse = puse - 1
    print("O lucro total é: {:.2f}%".format(use*100))
    lucro0 = (closes[-1]/closes[0]) - 1
    print("O lucro sem trade é: {:.2f}%".format(lucro0*100))
    print("O lucro somente positivo é: {:.2f}%".format(puse*100))
    print("Taxa de acerto: {:.2f}%".format((good/(bad+good))*100))
    print("maior perda: {:.2f}%".format(perda*100))
    print("Media de perdas: {:.2f}%".format(media*100))
    print("Numero de Trades: {}".format(cont))

    log = open('calculos.txt', 'a')
    log.write("{}".format(title))
    log.write("O lucro total eh: {:.2f}%\n".format(use*100))
    log.write("O lucro sem trade eh: {:.2f}%\n".format(lucro0*100))
    log.write("O lucro somente positivo eh: {:.2f}%\n".format(puse*100))
    log.write("Taxa de acerto: {:.2f}%\n".format((good/(bad+good))*100))
    log.write("maior perda: {:.2f}%\n".format(perda*100))
    log.write("Media de perdas: {:.2f}%\n".format(media*100))
    log.write("Numero de Trades: {}\n".format(cont))
    log.write("\n")
    log.close

if __name__ == '__main__':
    calc(d())
    
