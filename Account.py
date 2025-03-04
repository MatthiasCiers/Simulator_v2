class Account:

    #account object class
    def __init__(self, accountID: str, accountType:str,balance:float, creditLimit:float = 0):
        self.accountID = accountID
        self.accountType = accountType
        self.balance = balance
        self.creditLimit = creditLimit
        self.usedCredit = 0



    def getCreditLimit(self):
        return self.creditLimit

    def getBalance(self):
        return self.balance

    def getAccountType(self):
        return self.accountType

    def getUsedCredit(self):
        return self.usedCredit


    def checkBalance(self, amount : float, securityType: str):
        if self.accountType == "Cash" and securityType == "Cash":
           return  self.balance + self.creditLimit >= amount
        elif self.accountType == securityType:
            return self.balance >= amount
        else:
            return False


    def addBalance(self, amount:float, securityType:str):

        #if cash account
        if self.accountType == securityType and self.accountType == "Cash":

            #check whether this account used credit already: condition only satisfies if usedCredit ==0
            if self.creditLimit == (self.creditLimit - self.usedCredit):

                self.balance = self.balance + amount
                return amount

            elif self.creditLimit != self.creditLimit - self.usedCredit:
                #credit used so far, meaning balance should be 0 and credit used for self.usedCredit
                if self.usedCredit >= amount:
                    #reset the used credit with the amount
                    self.usedCredit = self.usedCredit - amount
                    return amount
                else:
                    #set used credit to 0 and add remaining to balance
                    remaining = amount - self.usedCredit
                    self.usedCredit = 0
                    self.balance = self.balance + remaining
                    return amount
        #if security account:
        elif self.accountType == securityType:
            self.balance = self.balance + amount
            return amount

        else:
            print("Error: account doesn't allow to add this type of assets")
            return 0


    def deductBalance(self, amount: float, securityType:str):

        #deduct cash
        if self.accountType == securityType and self.accountType == "Cash":
            total_available = self.balance + (self.creditLimit - self.usedCredit)
            if total_available <= amount:
                deducted = total_available
                self.usedCredit = self.creditLimit
                self.balance = 0
                return deducted

            elif total_available > amount and self.balance == 0:
                #adjust the creditLimit accordingly
                self.usedCredit = self.usedCredit + amount
                return amount

            elif self.balance > 0:
                if self.balance >= amount:
                    self.balance = self.balance - amount
                    return amount
                else:
                    deductedFromBalance = self.balance
                    self.balance = 0
                    self.usedCredit = self.usedCredit + deductedFromBalance
                    return amount

        #deduct securities
        elif self.accountType == securityType:
            if self.balance >= amount:
                self.balance = self.balance -amount
                return amount
            else:
                deducted = self.balance
                self.balance = 0
                return deducted

        else:
            print("Error: account doesn't allow to deduct this type of assets")
            return 0