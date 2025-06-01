from Bcolors import Bcolors as bc

class Product:
    def __init__(self, title, rev_rate, Sold, shipping, price):
        self.title = title
        self.rev_rate = rev_rate
        self.Sold = Sold
        self.shipping = shipping
        self.price = price

    def description(self):
        print()
        print(f"{bc.FAIL}--------------------------{bc.DEFAULT}")
        print(f"Title : {self.title}")
        print(f"Sold : {self.Sold}")
        print(f"Review Rate : {self.rev_rate}")
        print(f"Shipping : {self.shipping}")
        print(f"Price : {self.price}")
        print(f"{bc.FAIL}--------------------------{bc.DEFAULT}")