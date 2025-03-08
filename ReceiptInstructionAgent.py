from datetime import datetime
from typing import TYPE_CHECKING, Optional
import InstructionAgent

if TYPE_CHECKING:
    from SettlementModel import SettlementModel
    from InstitutionAgent import InstitutionAgent
    from Account import Account
    from TransactionAgent import TransactionAgent


class ReceiptInstructionAgent(InstructionAgent.InstructionAgent):
    def __init__(self, model: "SettlementModel", uniqueID: str, motherID: str, institution: "InstitutionAgent",
                 securitiesAccount: "Account", cashAccount: "Account", securityType: str, amount: float, isChild: bool,
                 status: str, linkcode: str, creation_time: datetime, linkedTransaction: Optional["TransactionAgent"] = None):
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
        # logging ( don't know why is_transaction = True)
        self.model.log_event(
            f"Receipt instruction with ID {uniqueID} created by institution {institution} for {securityType} for amount {amount}",
            self.uniqueID, is_transaction=True)

    def createReceiptChildren(self):
        available_cash = self.cashAccount.checkBalance(self.amount, self.securityType)

        # takes the minimum of available securities of deliverer and available cash of seller
        available_to_settle = min(self.linkedTransaction.securitiesAccount.checkBalance(self.amount, self.securityType),
                                  self.cashAccount.checkBalance(self.amount, self.securityType)
                                  )

        if available_cash > 0:
            # create delivery children instructions

            # instant matching and settlement of first child not yet possible, because receipt_child_1 does not yet exist
            receipt_child_1 = ReceiptInstructionAgent.ReceiptInstructionAgent(self.model, f"{self.uniqueID}_1", self.uniqueID,
                                                self.institution, self.securitiesAccount, self.cashAccount,
                                                self.securityType, available_to_settle, True, "Validated",
                                                f"{self.linkcode}_1", creation_time=datetime.now(), TransactionAgent=None
                                                )
            receipt_child_2 = ReceiptInstructionAgent.ReceiptInstructionAgent(self.model, f"{self.uniqueID}_2", self.uniqueID,
                                                self.institution, self.securitiesAccount, self.cashAccount,
                                                self.securityType, self.amount - available_to_settle, True,
                                                "Validated", f"{self.linkcode}_2", creation_time=datetime.now(), TransactionAgent = None
                                                )
            # add child instructions to the model
            self.model.schedule.add(receipt_child_1)
            self.model.schedule.add(receipt_child_2)

            return receipt_child_1, receipt_child_2
