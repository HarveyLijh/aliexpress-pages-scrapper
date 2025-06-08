from Bcolors import Bcolors as bc

class Product:
    def __init__(self, title, rev_rate, Sold, shipping, price, image_link=None):
        self.title = title
        self.rev_rate = rev_rate
        self.Sold = Sold
        self.shipping = shipping
        self.price = price
        self.image_link = image_link

    def description(self):
        print()
        print(f"{bc.FAIL}--------------------------{bc.DEFAULT}")
        print(f"Title : {self.title}")
        print(f"Sold : {self.Sold}")
        print(f"Review Rate : {self.rev_rate}")
        print(f"Shipping : {self.shipping}")
        print(f"Price : {self.price}")
        if self.image_link:
            print(f"Image Link : {self.image_link}")
        else:
            print("Image Link : Not available")
        print(f"{bc.FAIL}--------------------------{bc.DEFAULT}")