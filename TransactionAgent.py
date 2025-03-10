from mesa import Agent
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from ReceiptInstructionAgent import ReceiptInstructionAgent
    from DeliveryInstructionAgent import DeliveryInstructionAgent


class TransactionAgent(Agent):
    def __init__(self, model, transactionID: str, deliverer: "DeliveryInstructionAgent", receiver: "ReceiptInstructionAgent", status: str):
        super().__init__(model)
        self.transactionID = transactionID
        self.deliverer = deliverer
        self.receiver = receiver
        self.status = status

        #logging ( don't know why is_transaction = True)
       # self.model.log_event(f"Transaction {self.transactionID} created from account {self.deliverer.get_securitiesAccount().getAccountID()} to account {self.receiver.get_cashAccount().getAccountID()}", self.transactionID, is_transaction = True)

    def get_transactionID(self):
        return self.transactionID

    def get_status(self):
        return self.status

    def set_status(self, new_status: str):
        self.status = new_status

    def settle(self):
        #logging
        self.model.log_event(f"Transaction {self.transactionID} attempting to settle.", self.transactionID, is_transaction = True)
        if self.deliverer.get_status() == "Matched" and self.receiver.get_status() == "Matched" and self.status == "Matched":
            if (self.deliverer.securitiesAccount.checkBalance(self.deliverer.get_amount(), self.deliverer.get_securityType())
                    and self.receiver.cashAccount.checkBalance(self.receiver.get_amount(), "Cash")
            ):
                if self.deliverer.get_amount() == self.receiver.get_amount():
                    #additional check that to be settled amounts are equal

                    #transfer of securities
                    delivered_securities = self.deliverer.securitiesAccount.deductBalance(self.deliverer.get_amount(), self.deliverer.get_securityType())
                    received_securities = self.receiver.securitiesAccount.addBalance(self.receiver.get_amount(), self.deliverer.get_securityType())

                    #transfer of cash
                    delivered_cash = self.receiver.cashAccount.deductBalance(self.receiver.get_amount(), "Cash")
                    received_cash = self.deliverer.cashAccount.addBalance(self.deliverer.get_amount(), "Cash")

                    #extra check for safety
                    if not delivered_securities == received_securities == delivered_cash == received_cash == self.deliverer.get_amount() == self.receiver.get_amount():
                        self.deliverer.set_status("Cancelled due to error")
                        self.receiver.set_status("Cancelled due to error")
                        self.status = "Cancelled due to error"

                    #change states to "Settled"
                    self.deliverer.set_status("Settled")
                    self.receiver.set_status("Settled")
                    self.status = "Settled"

                    #logging
                    self.model.log_event(f"Transaction {self.transactionID} settled fully.", self.transactionID, is_transaction = True)
                    #remove the transaction and instructions from the model if fully settled
                    self.model.agents.remove(self.deliverer)
                    self.model.agents.remove(self.receiver)
                    self.model.agents.remove(self)


            elif self.deliverer.get_amount() == 0 or self.receiver.get_amount() == 0:
                #will do nothing if there is no cash or securities available
                #logging
                self.model.log_event(f"Error: Transaction {self.transactionID} failed due to no cash or securities available", self.transactionID, is_transaction = True)
            else:
                #handless partial settlement
                # Inside the partial settlement block in TransactionAgent.settle()
                if self.deliverer.get_institution().check_partial_allowed() and self.receiver.get_institution().check_partial_allowed():
                    delivery_children = self.deliverer.createDeliveryChildren()
                    receipt_children = self.receiver.createReceiptChildren()

                    # Check if partial settlement children were created.
                    if receipt_children == (None, None) or delivery_children == (None, None):
                        self.model.log_event(
                            f"Transaction {self.transactionID} partial settlement aborted due to insufficient funds.",
                            self.transactionID,
                            is_transaction=True
                        )
                        # Optionally, you can handle this scenario (e.g., cancel the transaction or retry later)
                    else:
                        delivery_child_1, delivery_child_2 = delivery_children
                        receipt_child_1, receipt_child_2 = receipt_children

                        child_transaction_1 = delivery_child_1.match()
                        child_transaction_2 = delivery_child_2.match()
                        child_transaction_1.settle()
                        child_transaction_2.deliverer.get_securitiesAccount().set_newSecurities(False)
                        child_transaction_2.receiver.get_cashAccount().set_newSecurities(False)
                        self.model.log_event(
                            f"Transaction {self.transactionID} partially settled. Children {receipt_child_1.get_uniqueID()}, "
                            f"{receipt_child_2.get_uniqueID()}, {delivery_child_1.get_uniqueID()} and {delivery_child_2.get_uniqueID()} created. "
                            f"Transactions {child_transaction_1.transactionID} and {child_transaction_2.transactionID} created.",
                            self.transactionID,
                            is_transaction=True
                        )
                        self.cancel_partial()
        else:
            self.model.log_event(f"One of the instructions or transaction not in the correct state", self.transactionID, is_transaction = True)
        self.deliverer.get_securitiesAccount().set_newSecurities(False)
        self.receiver.get_cashAccount().set_newSecurities(False)

    def step(self):
        if (self.deliverer.get_securitiesAccount().get_newSecurities() == False
            or self.receiver.get_cashAccount().get_newSecurities() == False):
            #if no new securities or cash where added to an account, no settlement gets tried
            return

        if self.deliverer.is_instruction_time_out():
            self.deliverer.cancel_timout()
        elif self.receiver.is_instruction_time_out():
            self.receiver.cancel_timout()
        else:
            if self.status not in ["Cancelled due to timeout", "Settled"]:
                self.settle()
        self.model.simulated_time = self.model.simulated_time + timedelta(seconds=1)

    def cancel_partial(self):
        self.status = "Cancelled due to partial settlement"
        self.deliverer.set_status("Cancelled due to partial settlement")
        self.receiver.set_status("Cancelled due to partial settlement")

        #logging
        self.model.log_event(f"Transaction {self.transactionID} cancelled due to partial settlement.", self.transactionID, is_transaction = True)
        #remove transition and instructions from the model when cancelled
        self.model.agents.remove(self.deliverer)
        self.model.agents.remove(self.receiver)
        self.model.agents.remove(self)


