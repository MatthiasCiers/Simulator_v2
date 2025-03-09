from datetime import datetime
from typing import TYPE_CHECKING, Optional
import InstructionAgent

if TYPE_CHECKING:
    from SettlementModel import SettlementModel
    from InstitutionAgent import InstitutionAgent
    from Account import Account
    #from TransactionAgent import TransactionAgent

import TransactionAgent
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

        MIN_SETTLEMENT_AMOUNT = self.model.min_settlement_amount
        # Calculate the actual available amounts using getBalance(), ensuring correct account types.
        if self.cashAccount.getAccountType() != "Cash":
            available_cash = 0
        else:
            available_cash = self.cashAccount.getBalance()

        deliverer = self.linkedTransaction.deliverer
        if deliverer.securitiesAccount.getAccountType() != self.securityType:
            available_securities = 0
        else:
            available_securities = deliverer.securitiesAccount.getBalance()

        # Compute the amount that can actually be settled.
        available_to_settle = min(self.amount, available_cash, available_securities)

        if available_to_settle > MIN_SETTLEMENT_AMOUNT:
            # Create receipt child instructions with the computed amounts.
            receipt_child_1 = ReceiptInstructionAgent(
                self.model,
                f"{self.uniqueID}_1",
                self.uniqueID,
                self.institution,
                self.securitiesAccount,
                self.cashAccount,
                self.securityType,
                available_to_settle,
                True,
                "Validated",
                f"{self.linkcode}_1",
                creation_time=datetime.now(),
                linkedTransaction=None
            )
            receipt_child_2 = ReceiptInstructionAgent(
                self.model,
                f"{self.uniqueID}_2",
                self.uniqueID,
                self.institution,
                self.securitiesAccount,
                self.cashAccount,
                self.securityType,
                self.amount - available_to_settle,
                True,
                "Validated",
                f"{self.linkcode}_2",
                creation_time=datetime.now(),
                linkedTransaction=None
            )
            # Add the new child instructions to the agents scheduler.
            self.model.agents.add(receipt_child_1)
            self.model.agents.add(receipt_child_2)
            return receipt_child_1, receipt_child_2
        else:
            # Log insufficient funds and return a tuple of Nones.
            self.model.log_event(
                f"ReceiptInstruction {self.uniqueID}: insufficient funds for partial settlement.",
                self.uniqueID,
                is_transaction=True
            )
            return (None, None)

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
        transaction = TransactionAgent.TransactionAgent(
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
