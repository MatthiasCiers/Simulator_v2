#InstitutionAgent
import time
import random
from datetime import datetime
import SettlementModel
from mesa import Agent, Model
import ReceiptInstructionAgent
import InstructionAgent
import DeliveryInstructionAgent
import Account




class InstitutionAgent(Agent):

    def __init__(self, model:SettlementModel, institutionID:str, accounts:list[Account] = [],allowPartial:bool = True):
        super().__init__(model)

        self.institutionID = institutionID
        self.accounts = accounts
        self.allowPartial = allowPartial

    def opt_out_partial(self):
        if not self.allowPartial:
            print("Institution Already opted out, cannot opt out again")
        else:
            self.allowPartiala = False
            print("Institution opted out of partial settlement")

    def opt_in_partial(self):
        if self.allowPartial:
            print("Institution Already opted in, cannot opt in again")
        else:
            self.allow_partial = True
            print("Institution opted in of partial settlements")

    def check_partial_allowed(self):
        if self.allowPartial == True:
            return True
        else:
            return False

    def getSecurityAccounts(self, securityType:str):
        security_accounts = []
        for account in self.accounts:
            if account.accountType == securityType:
                security_accounts.append(account)

        return security_accounts

    def create_instruction(self):
        instruction_type = random.choice(['delivery', 'receipt'])

        cash_account = self.getSecurityAccounts(self, securityType= "Cash")
        random_security = random.choice(["Bond-A", "Bond-B", "Bond-C", "Bond-D"])
        security_account = self.getSecurityAccounts(self, securityType= random_security)
        amount = round(random.uniform(100, 10000), 2)
        model = self.model
        linkedTransaction = None
        uniqueID = len(self.model.instructions) + 1
        otherID = len(self.model.instructions) + 2
        motherID = "mother"
        institution = self
        other_institution = random.choice([inst for inst in self.model.institutions if inst != self])
        securityType = random_security
        other_institution_cash_account= other_institution.getSecurityAccounts(securityType= "Cash")
        other_institution_security_account = other_institution.getSecurityAccounts(securityType=securityType)
        isChild = False
        status = "Exists"
        linkcode = "LINK-"+ uniqueID + "L" + otherID
        instruction_creation_time = datetime.now()
        counter_instruction_creation_time = self.model.random_timestamp()

        if instruction_type == 'delivery':
            new_instructionAgent = DeliveryInstructionAgent.DeliveryInstructionAgent(uniqueID=uniqueID, model = model, linkedTransaction = linkedTransaction, motherID=motherID, institution= institution, securitiesAccount = security_account, cashAccount = cash_account, securityType=securityType, amount= amount, isChild=isChild, status=status, linkcode=linkcode, creation_time = instruction_creation_time)
            counter_instructionAgent = ReceiptInstructionAgent.ReceiptInstructionAgent(uniqueID=otherID, model = model, linkedTransaction = linkedTransaction, motherID=motherID, institution= other_institution, securitiesAccount = other_institution_security_account, cashAccount = other_institution_cash_account, securityType=securityType, amount= amount, isChild=isChild, status=status, linkcode=linkcode, creation_time = counter_instruction_creation_time)
            self.model.instructions.append(new_instructionAgent)
            self.model.instructions.append(counter_instructionAgent)
        else:
            new_instructionAgent = ReceiptInstructionAgent.ReceiptInstructionAgent(uniqueID=uniqueID, model = model, linkedTransaction = linkedTransaction, motherID=motherID, institution= institution, securitiesAccount = security_account, cashAccount = cash_account, securityType=securityType, amount= amount, isChild=isChild, status=status, linkcode=linkcode, creation_time = instruction_creation_time)
            counter_instructionAgent = DeliveryInstructionAgent.DeliveryInstructionAgent(uniqueID=otherID, model = model, linkedTransaction = linkedTransaction, motherID=motherID, institution= other_institution, securitiesAccount = other_institution_security_account, cashAccount = other_institution_cash_account, securityType=securityType, amount= amount, isChild=isChild, status=status, linkcode=linkcode, creation_time = counter_instruction_creation_time)
            self.model.instructions.append(new_instructionAgent)
            self.model.instructions.append(counter_instructionAgent)




    def create_cancelation_instruction(self):

        #to implement later on
        return


    def create_account(self):
        #not really relevant so far
        return

    def step(self):

        #if selected create an instruction and with low probability allow/ disallow partial settlements

        if random.random() <0.5:
            self.create_instruction()
        if random.random() <0.05:
            self.create_cancelation_instruction()

        if random.random() < 0.01:
            if self.allow_partial:
                self.opt_out_partial()
            else:
                self.opt_in_partial()



