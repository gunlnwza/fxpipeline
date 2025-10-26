import random


class Household:
    def __init__(self, money: float, labor: float, labor_price: float):
        self.money = money
        self.labor = labor
        self.labor_price = labor_price

    def __str__(self):
        return f"Household(M={self.money}, L={self.labor}, P={self.labor_price})"

    def sell_labor(self, firm: "Firm"):
        money = self.labor * self.labor_price
        labor = self.labor

        firm.money -= money
        firm.labor += labor

        self.money += money

    # def populate(self, a=1.1):
    #     self.labor *= a


class Firm:
    def __init__(self, money: float, goods_price: float):
        self.money = money
        self.goods_price = goods_price

        self.labor = 0
        self.goods = 0

    def __str__(self):
        return f"Firm(M={self.money}, Q={self.goods}, P={self.goods_price})"
 
    def produce_goods(self):
        self.goods += self.labor  # use all labor to turn into goods, 1 labor == 1 goods
        self.labor = 0

    def sell_goods(self, household: Household):
        money = self.goods * self.goods_price
        goods = self.goods

        household.money -= money
        # household.goods += goods

        self.goods = 0
        self.money += money


class Economy:
    def __init__(self):
        self.household = Household(1000, 10, 10)
        self.firm = Firm(1000, 11)

    def simulate(self):
        for i in range(20):
            self.household.sell_labor(self.firm)
            self.firm.produce_goods()
            self.firm.sell_goods(self.household)
            # self.household.populate()

            print(i, self.household, self.firm)


def main():
    random.seed(42)
    economy = Economy()
    economy.simulate()


if __name__ == "__main__":
    main()
