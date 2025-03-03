from mesa import Agent
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
        # TODO: Return the current status
        pass

    def settle(self):
        # TODO: Implement settlement logic
        pass

    def cancel_timeout(self):
        # TODO: Implement timeout cancellation logic
        pass

    def cancel_partial(self):
        # TODO: Implement partial settlement cancellation logic
        pass

