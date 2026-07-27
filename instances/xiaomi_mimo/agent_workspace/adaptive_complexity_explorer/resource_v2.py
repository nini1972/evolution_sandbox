class Resource:
    def __init__(self, amount=1.0, regrowth_rate=0.1):
        self.amount = amount
        self.max_amount = amount
        self.regrowth_rate = regrowth_rate
        
    def consume(self, amount):
        consumed = min(amount, self.amount)
        self.amount -= consumed
        return consumed
        
    def regrow(self):
        self.amount = min(self.max_amount, self.amount + self.regrowth_rate)