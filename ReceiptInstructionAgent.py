from datetime import datetime
from typing import TYPE_CHECKING, Optional
import InstructionAgent

if TYPE_CHECKING:
    from SettlementModel import SettlementModel
    from InstitutionAgent import InstitutionAgent
    from Account import Account
    from TransactionAgent import TransactionAgent

import DeliveryInstructionAgent


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
            f"Receipt instruction with ID {uniqueID} created by institution {institution.institutionID} for {securityType} for amount {amount}",
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



    def match(self):
        """Matches this ReceiptInstructionAgent with a DeliveryInstructionAgent
        that has the same link code and creates a TransactionAgent."""

        self.model.log_event(
            f"Instruction {self.uniqueID} attempting to match",
            self.uniqueID,
            is_transaction=True
        )

        if self.status != "Validated":
            self.model.log_event(
                f"Error: Instruction {self.uniqueID} in wrong state, cannot match",
                self.uniqueID,
                is_transaction=True,
            )
            return None

        # Find a matching DeliveryInstructionAgent
        other_instruction = None
        for agent in self.model.agents:
            if (
                    isinstance(agent, DeliveryInstructionAgent.DeliveryInstructionAgent)  # Ensure it's a DeliveryInstructionAgent
                    and agent.linkcode == self.linkcode  # Check if linkcodes match
                    and agent.status == "Validated"  # Ensure the status is correct
            ):
                other_instruction = agent
                break
        else:
            self.model.log_event(
                f"ERROR: ReceiptInstruction {self.uniqueID} failed to match, no matching DeliveryInstruction found",
                self.uniqueID,
                is_transaction=True,
            )
            return None

        # Create a transaction
        transaction = TransactionAgent(
            model=self.model,
            transactionID=f"{self.uniqueID}_{other_instruction.uniqueID}",
            deliverer=other_instruction,
            receiver=self,
            status="Matched",
        )

        # Link transaction to both instructions
        self.linkedTransaction = transaction
        other_instruction.linkedTransaction = transaction

        # Update status
        self.set_status("Matched")
        other_instruction.set_status("Matched")

        self.model.log_event(
            f"ReceiptInstruction {self.uniqueID} matched with DeliveryInstruction {other_instruction.uniqueID}",
            self.uniqueID,
            is_transaction=True,
        )
        return transaction
