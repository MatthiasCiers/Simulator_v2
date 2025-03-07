from mesa import Agent
import InstructionAgent
import ReceiptInstructionAgent
import DeliveryInstructionAgent

class TransactionAgent(Agent):
    def __init__(self, model, transactionID: str, deliverer: DeliveryInstructionAgent, receiver: ReceiptInstructionAgent, status: str):
        super().__init__(model)
        self.transactionID = transactionID
        self.deliverer = deliverer
        self.receiver = receiver
        self.status = status

    def get_status(self):
        return self.status

    def settle(self):
        if self.deliverer.get_status() == "Matched" and self.receiver.get_status() == "Matched":
            if (
                #checks if full ammount can be settled
                self.deliverer.securitiesAccount.checkBalance(self.deliverer.get_amount, self.deliverer.get_securityType)
                and self.receiver.cashAccount.checkBalance(self.receiver.get_amount, self.receiver.get_securityType)
            ):
                if self.deliverer.get_amount() == self.receiver.get_amount():
                    #additional check that to be settled amounts are equal

                    #transfer of securities
                    delivered_securities = self.deliverer.securitiesAccount.deductBalance(self.deliverer.get_amount, self.deliverer.get_securityType)
                    received_securites = self.receiver.securitiesAccount.addBalance(self.receiver.get_amount, self.deliverer.get_securityType)

                    #transfer of cash
                    delivered_cash = self.receiver.cashAccount.deductBalance(self.receiver.get_amount, "Cash")
                    received_cash = self.deliverer.cashAccount.addBalance(self.deliverer.get_amount, "Cash")

                    #extra check for safety
                    if not delivered_securities == received_securites == delivered_cash == received_cash == self.deliverer.get_amount == self.receiver.get_amount:
                        self.deliverer.set_status("Cancelled due to error")
                        self.receiver.set_status("Cancelled due to error")
                        self.status = "Cancelled due to error"

                    #change states to "Settled"
                    self.deliverer.set_status("Settled")
                    self.receiver.set_status("Settled")
                    self.status = "Settled"

            elif self.deliverer.get_amount() == 0 or self.receiver.get_amount() == 0:
                #will do nothing if there is no cash or securities available
                pass
            else:
                #handless partial settlement

                if self.deliverer.get_institution().check_partial_allowed() and self.receiver.get_institution().check_partial_allowed():
                    #check if institutions allow partial settlement
                    delivery_child_1, delivery_child_2 = self.deliverer.createDeliveryChildren()
                    receipt_child_1, receipt_child_2 = self.receiver.createReceiptChildren()
                    child_transaction_1 = delivery_child_1.match()
                    child_transaction_2 = delivery_child_2.match()
                    child_transaction_1.settle()







    def cancel_timeout(self):
        # TODO: Implement timeout cancellation logic
        pass

    def cancel_partial(self):
        # TODO: Implement partial settlement cancellation logic
        pass

