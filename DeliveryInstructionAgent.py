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
        available_securities = self.securitiesAccount.checkSufficientBalance(self.amount, self.securityType)
        if available_securities > 0:
            #create delivery children instructions

            #instant matching and settlement of first child not yet possible, because receipt_child_1 does not yet exist
            delivery_child_1 = InstructionAgent(self.model, f"{self.uniqueID}_1", self.uniqueID,
                                                self.institution, self.securitiesAccount, self.cashAccount,
                                                self.securityType, available_securities, True, "Validated", f"{self.linkcode}_1", datetime, None
                                                )
            delivery_child_2 = InstructionAgent(self.model, f"{self.uniqueID}_2", self.uniqueID,
                                                self.institution, self.securitiesAccount, self.cashAccount,
                                                self.securityType, self.amount - available_securities, True, "Validated", f"{self.linkcode}_1", datetime, None
                                                )
            #add child instructions to the model
            self.model.schedule.add(delivery_child_1)
            self.model.schedule.add(delivery_child_2)