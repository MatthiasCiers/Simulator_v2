from datetime import datetime
import TransactionAgent
import SettlementModel
import InstitutionAgent
import InstructionAgent
import Account

class DeliveryInstructionAgent(InstructionAgent):
    def __init__(self, model: SettlementModel, uniqueID: str, motherID: str, institution: InstitutionAgent, securitiesAccount: Account, cashAccount: Account, securityType: str, amount: float, isChild: bool, status: str, linkcode: str, creation_time: datetime ,linkedTransaction: TransactionAgent = None):
        super().__init__(
            model=model,
            linkedTransaction=linkedTransaction,
            uniqueID=uniqueID,
            motherID=motherID,
            institution=institution,
            securitiesAccount=securitiesAccount,
            cashAccount=cashAccount,
            securityType=securityType,
            amount=amount,
            isChild=isChild,
            status=status,
            linkcode=linkcode,
            creation_time=creation_time
        )

    def createDeliveryChildren(self):
        #implementation to do
        pass