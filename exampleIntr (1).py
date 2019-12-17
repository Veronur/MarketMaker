from backtesting import evaluateIntr
from strategy import Strategy
from order import Order
import numpy as np


class GoldMine(Strategy):
#Odem de compra abaixo do preço do PBR
#Ordem de venda acima do preço do PBR

#Pbr=(Petro/dolar)*2
    def __init__(self):
        self.prices=[]
        self.spread=0.1
        self.counter=0
        self.idOrdens={"Compra":[],"Venda":[]}
        self.orders = []
        
    def push(self, event):
        price = event.price[3]
        self.prices.append(price)
        print(event.instrument)
        if (self.counter%2==0 and self.counter != 0):
            precoPetro = (self.prices[ self.counter-1]/self.prices[self.counter-2])*2

            # if (len(self.idOrdens['Compra'])!=0):
            #     self.cancel(self.id, self.idOrdens['Compra'][-1])
            for i in self.idOrdens['Compra']:
                self.cancel(self.id, i)
            orderComp = Order('PBR', 1, precoPetro - self.spread)
            self.orders.append(orderComp)
            idorderComp = orderComp.id
            self.idOrdens["Compra"].append(idorderComp)
            

            # if (len(self.idOrdens['Venda'])!=0):
            #     self.cancel(self.id, self.idOrdens['Venda'][-1])
            for i in self.idOrdens['Venda']:
                self.cancel(self.id, i)            
            orderVend = Order('PBR', -1, precoPetro + self.spread)
            self.orders.append(orderVend)
            idorderVend = orderVend.id
            self.idOrdens["Venda"].append(idorderVend)


        return self.orders


    def fill(self, id, instrument, price, quantity, status):
        super().fill(id, instrument, price, quantity, status) 
        

        if (quantity != 0 and instrument == 'PBR'):
                dolares=price*(quantity)
                reais= dolares * self.prices[ self.counter-2]
                qnt=reais/self.prices[self.counter-1]
                self.submit(self.id,[Order('USDBRL', -(qnt), reais),Order('PETR3', (2*quantity), 0)])




class BuynHold(Strategy):

    def __init__(self):
        self.bought = {}
        self.orders = []

    def push(self, event):
        # If didnt buy yet, do it
        if event.instrument not in self.bought:
            self.bought[event.instrument] = False

        if not self.bought[event.instrument]:
            self.bought[event.instrument] = True
            # Send one buy order once
            order = Order(event.instrument, 1, event.price[3] - 0.01)
            self.orders.append(order)
            return [order]
        else:
            for order in self.orders:
                self.cancel(self.id, order.id)

        # If you need partial result in case of feedback training
        # result = self.partialResult()

        return []


class MAVG(Strategy):

    def __init__(self):
        self.signal = 0
        self.prices = []
        self.sizeq = 17
        self.sizes = 72
        self.std = 0
        self.ref = 0

    def push(self, event):
        price = event.price[3]
        self.prices.append(price)
        orders = []

        if len(self.prices) >= self.sizeq:
            maq = sum(self.prices[-self.sizeq:])/self.sizeq
        if len(self.prices) == self.sizes:
            mas = sum(self.prices)/self.sizes

            if maq > mas and self.signal != 1:
                if self.signal == -1:
                    orders.append(Order(event.instrument, 1, 0))
                orders.append(Order(event.instrument, 1, 0))
                self.signal = 1
            elif maq < mas and self.signal != -1:
                if self.signal == 1:
                    orders.append(Order(event.instrument, -1, 0))
                orders.append(Order(event.instrument, -1, 0))
                self.signal = -1

            del self.prices[0]

        return orders


# print(evaluateIntr(BuynHold(), {'USDBRL': 'USDBRL.csv', 'PETR3': 'PETR3.csv'}))
# print(evaluateIntr(MAVG(), {'USDBRL': 'USDBRL.csv'}))
print(evaluateIntr(GoldMine(), {'USDBRL': 'USDBRL.csv', 'PETR3': 'PETR3.csv','PBR': 'PBR.csv'}))