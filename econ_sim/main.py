import random
import numpy as np


# class Household:
#     def __init__(self, money: float, labor: float, labor_price: float):
#         self.money = money
#         self.labor = labor
#         self.labor_price = labor_price

#     def __str__(self):
#         return f"Household(M={self.money}, L={self.labor}, P={self.labor_price})"

#     def sell_labor(self, firm: "Firm"):
#         labor = firm.labor_wanted()
#         money = labor * self.labor_price
#         while money > firm.money:
#             labor -= 1
#             money = labor * self.labor_price

#         firm.money -= money
#         firm.labor += labor

#         self.money += money

#     def goods_wanted(self):
#         return random.randint(1, 10)

#     # def populate(self, a=1.1):
#     #     self.labor *= a

#     def update_price(self):
#         self.labor_price += 1


# class Firm:
#     def __init__(self, money: float, goods_price: float):
#         self.money = money
#         self.goods_price = goods_price

#         self.labor = 0
#         self.goods = 0

#     def __str__(self):
#         return f"Firm(M={self.money}, Q={self.goods}, P={self.goods_price})"
 
#     def produce_goods(self):
#         self.goods += self.labor  # use all labor to turn into goods, 1 labor == 1 goods
#         self.labor = 0

#     def labor_wanted(self):
#         return random.randint(1, 10)

#     def sell_goods(self, household: Household):
#         goods = household.goods_wanted()
#         money = goods * self.goods_price
#         while money > household.money:
#             goods -= 1
#             money = goods * self.labor_price

#         household.money -= money
#         # household.goods += goods

#         self.goods = 0
#         self.money += money

#     def update_price(self):
#         self.goods_price += 1


# class Economy:
#     def __init__(self):
#         self.household = Household(1000, 10, 10)
#         self.firm = Firm(1000, 11)

#     def simulate(self):
#         for i in range(20):
#             self.household.sell_labor(self.firm)
#             self.firm.produce_goods()
#             self.firm.sell_goods(self.household)
#             # self.household.populate()

#             self.household.update_price()
#             self.firm.update_price()

#             print(i, self.household, self.firm)



class Seller:
    def __init__(self):
        self.price = random.randint(1, 10)

    def ask(self):
        return round(random.uniform(7, 14), 2)


class Buyer:
    def __init__(self):
        pass

    def bid(self):
        return round(random.uniform(8, 12), 2)
    


class Economy:
    def __init__(self):
        self.buyers = [Buyer() for _ in range(5)]
        self.sellers = [Seller() for _ in range(5)]

    def simulate(self):
        for i in range(5):
            bids = [(i, b.bid()) for i, b in enumerate(self.buyers)]
            bids.sort(key=lambda x: x[1])
            asks = [(i, s.ask()) for i, s in enumerate(self.sellers)]
            asks.sort(key=lambda x: x[1])

            print(i)
            print("bid", bids)
            print("ask", asks)


def main():
    random.seed(42)
    economy = Economy()
    economy.simulate()


if __name__ == "__main__":
    main()
