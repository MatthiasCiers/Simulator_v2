from mesa import Model
from datetime import datetime
import pandas as pd
import TransactionAgent
import InstitutionAgent
import Account
import DeliveryInstructionAgent
import ReceiptInstructionAgent
import random

def generate_iban():
    """Generate a simple IBAN-like string.
    Example: 'DE45' + 16 digits.
    """
    country_code = random.choice(["DE", "FR", "NL", "GB"])
    check_digits = str(random.randint(10, 99))
    bban = ''.join(random.choices("0123456789", k=5))
    return f"{country_code}{check_digits}{bban}"


class SettlementModel(Model):
    def __init__(self):
        super().__init__()

        #parameters of the model
        self.num_institutions = 5
        self.min_total_accounts = 2
        self.max_total_accounts = 6
        self.simulation_duration_days = 10
        self.bond_types = ["Bond-A", "Bond-B", "Bond-C", "Bond-D"]
        self.steps_per_day = 500 #random chosen



        self.participants = []
        self.accounts = []
        self.instructions = []
        self.transactions = []
        self.event_log = []
        self.activity_log = []
        self.generate_data()


    def log_event(self, message, agent_id, is_transaction=True):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {'Timestamp': timestamp, 'Agent ID': agent_id, 'Event': message}

        if is_transaction:
            if log_entry not in self.event_log:
                print(f"{timestamp} | Agent ID: {log_entry['Agent ID']} | {message}")
                self.event_log.append(log_entry)  # Ensures no duplicates
        else:
            if log_entry not in self.activity_log:
                print(f"{timestamp} | Agent ID: {log_entry['Agent ID']} | {message}")
                  # Ensures no duplicates

        self.activity_log.append(log_entry)

    def save_log(self, filename=None, activity_filename=None):
        if filename is None:
            filename = "event_log.csv"  # Default filename
        df = pd.DataFrame(self.event_log)
        df.to_csv(filename, index=False)
        if activity_filename is None:
            activity_filename = "activity_log.csv"
        df_activity = pd.DataFrame(self.activity_log)
        df_activity.to_csv(activity_filename, index=False)
        print(f"Activity log saved to {activity_filename}")
        print(f"Event Log saved to {filename}")

    def generate_data(self):
        for i in range(1, self.num_institutions+ 1):
            inst_id = f"INST-{i}"
            inst_accounts = []
            total_accounts = random.randint(self.min_total_accounts, self.max_total_accounts)
            #generate cash account => there has to be at least 1 cash account
            new_cash_accountID = generate_iban()
            new_cash_accountType = "Cash"
            new_cash_balance =  round(random.uniform(5000, 200000), 2)
            new_cash_creditLimit = round(random.uniform(100000, 500000), 2)
            new_cash_Account = Account.Account(accountID=new_cash_accountID, accountType= new_cash_accountType, balance= new_cash_balance, creditLimit=new_cash_creditLimit)
            inst_accounts.append(new_cash_Account)
            self.accounts.append(new_cash_Account)
            for _ in range(total_accounts - 1):
                new_security_accountID = generate_iban()
                new_security_accountType = random.choice(self.bond_types)
                new_security_balance = round(random.uniform(5000, 200000), 2)
                new_security_creditLimit = 0
                new_security_Account = Account.Account(accountID=new_security_accountID, accountType= new_security_accountType, balance= new_security_balance, creditLimit= new_security_creditLimit)
                inst_accounts.append(new_security_Account)
                self.accounts.append(new_security_Account)
            new_institution = InstitutionAgent.InstitutionAgent(institutionID= inst_id, accounts= inst_accounts, model=self, allowPartial=True)
            self.participants.append(new_institution)




    def step(self):
        print(f"Running simulation step {self.steps}...")
        #shuffles all agents and then executes their step module once for all of them
        self.agents.shuffle_do("step")
        print(len(self.agents) + "Agents executed their step module")


        #this has to be implemented later
       # if self.steps % self.steps_per_day == 0:
        #    print(f"\n=== End of Business Day (Step {self.steps}) Batch Processing ===")
         #   self.agents.shuffle_do("batch_run")
          #  print("=== End of Batch Processing ===\n")


















if __name__ == "__main__":
    print("Starting simulation...")
    log_path = input("Enter the path to save the log (press Enter for default): ")
    if not log_path.strip():
        log_path = "event_log.csv"
    model = SettlementModel()
    for _ in range(100):
        model.step()
    print("Final Event Log:")
    for event in model.event_log:
        print(event)
    print("Saving final event log...")
    model.save_log(log_path)
