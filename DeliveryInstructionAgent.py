from datetime import datetime
from typing import TYPE_CHECKING, Optional
import InstructionAgent

if TYPE_CHECKING:
    from SettlementModel import SettlementModel
    from InstitutionAgent import InstitutionAgent
    from Account import Account
    from TransactionAgent import TransactionAgent

import ReceiptInstructionAgent

class DeliveryInstructionAgent(InstructionAgent.InstructionAgent):
    def __init__(self, model: "SettlementModel", uniqueID: str, motherID: str, institution: "InstitutionAgent", securitiesAccount: "Account", cashAccount: "Account", securityType: str, amount: float, isChild: bool, status: str, linkcode: str, creation_time: datetime ,linkedTransaction: Optional["TransactionAgent"] = None):
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
        self.model.log_event(f"Delivery instruction with ID {uniqueID} created by institution {institution.institutionID} for {securityType} for amount {amount}", self.uniqueID, is_transaction = True)

    def createDeliveryChildren(self):
        available_securities = self.securitiesAccount.checkBalance(self.amount, self.securityType)

        #takes the minimum of available securities of deliverer and available cash of seller
        available_to_settle = min(self.securitiesAccount.checkBalance(self.amount, self.securityType),
                                  self.linkedTransaction.cashAccount.checkBalance(self.amount, self.securityType)
                                  )

        if available_securities > 0:
            #create delivery children instructions

            #instant matching and settlement of first child not yet possible, because receipt_child_1 does not yet exist
            delivery_child_1 = DeliveryInstructionAgent.DeliveryInstructionAgent(self.model, f"{self.uniqueID}_1", self.uniqueID,
                                                self.institution, self.securitiesAccount, self.cashAccount,
                                                self.securityType, available_to_settle, True, "Validated", f"{self.linkcode}_1", datetime.now(), None
                                                )
            delivery_child_2 = DeliveryInstructionAgent.DeliveryInstructionAgent(self.model, f"{self.uniqueID}_2", self.uniqueID,
                                                self.institution, self.securitiesAccount, self.cashAccount,
                                                self.securityType, self.amount - available_to_settle, True, "Validated", f"{self.linkcode}_2", datetime.now(), None
                                                )
            #add child instructions to the model
            self.model.schedule.add(delivery_child_1)
            self.model.schedule.add(delivery_child_2)

            return delivery_child_1, delivery_child_2

    def match(self):
        """Matches this DeliveryInstructionAgent with a ReceiptInstructionAgent
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

        # Find a matching ReceiptInstructionAgent
        other_instruction = None
        for agent in self.model.agents:
            if (
                    isinstance(agent, ReceiptInstructionAgent.ReceiptInstructionAgent)  # Ensure it's a ReceiptInstructionAgent
                    and agent.linkcode == self.linkcode  # Check if linkcodes match
                    and agent.status == "Validated"  # Ensure the status is correct
            ):
                other_instruction = agent
                break
        else:
            self.model.log_event(
                f"ERROR: DeliveryInstruction {self.uniqueID} failed to match, no matching ReceiptInstruction found",
                self.uniqueID,
                is_transaction=True,
            )
            return None

        # Create a transaction
        transaction = TransactionAgent(
            model=self.model,
            transactionID=f"{self.uniqueID}_{other_instruction.uniqueID}",
            deliverer=self,
            receiver=other_instruction,
            status="Matched",
        )

        # Link transaction to both instructions
        self.linkedTransaction = transaction
        other_instruction.linkedTransaction = transaction

        # Update status
        self.set_status("Matched")
        other_instruction.set_status("Matched")

        self.model.log_event(
            f"DeliveryInstruction {self.uniqueID} matched with ReceiptInstruction {other_instruction.uniqueID}",
            self.uniqueID,
            is_transaction=True,
        )
        return transaction