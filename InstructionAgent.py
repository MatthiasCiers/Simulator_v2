from datetime import datetime
import TransactionAgent
import SettlementModel
import InstitutionAgent
import Account
from mesa import Agent

class InstructionAgent (Agent):
    def __init__(self,model: SettlementModel, uniqueID: str, motherID: str, institution: InstitutionAgent, securitiesAccount: Account, cashAccount: Account, securityType: str, amount: float, isChild: bool, status: str, linkcode: str, creation_time: datetime, linkedTransaction: TransactionAgent = None):
        super.__init__(model)
        self.model = model
        self.uniqueID = uniqueID
        self.motherID = motherID
        self.institution = institution
        self.securitiesAccount = securitiesAccount
        self.cashAccount = cashAccount
        self.securityType = securityType
        self.amount = amount
        self.isChild = isChild
        self.status = status
        self.linkcode = linkcode
        self.creation_time = datetime.datetime.now() # track creation time for timeout

#getter methods
    def get_model(self):
        """Returns the model associated with the agent."""
        return self.model

    def get_linkedTransaction(self):
        """Returns the linked transaction agent."""
        return self.linkedTransaction

    def get_uniqueID(self):
        """Returns the unique ID of the instruction."""
        return self.uniqueID

    def get_motherID(self):
        """Returns the mother ID of the instruction (if it's a child instruction)."""
        return self.motherID

    def get_institution(self):
        """Returns the institution associated with the instruction."""
        return self.institution

    def get_securitiesAccount(self):
        """Returns the securities account linked to the instruction."""
        return self.securitiesAccount

    def get_cashAccount(self):
        """Returns the cash account linked to the instruction."""
        return self.cashAccount

    def get_securityType(self):
        """Returns the type of security involved in the instruction."""
        return self.securityType

    def get_amount(self):
        """Returns the amount of securities or cash involved in the instruction."""
        return self.amount

    def get_isChild(self):
        """Returns whether the instruction is a child instruction."""
        return self.isChild

    def get_status(self):
        """Returns the current status of the instruction."""
        return self.status

    def get_linkcode(self):
        """Returns the link code associated with the instruction."""
        return self.linkcode

    def get_creation_time(self):
        """Returns the creation time of the instruction."""
        return self.creation_time