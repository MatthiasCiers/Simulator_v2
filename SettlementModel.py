from mesa import Model
from datetime import datetime, timedelta
import pandas as pd
import InstitutionAgent
import Account
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
        self.simulation_duration_days = 2
        self.min_settlement_amount = 100
        self.bond_types = ["Bond-A", "Bond-B", "Bond-C", "Bond-D"]
        self.steps_per_day = 500 #random chosen


        self.simulation_start = datetime.now()
        self.simulation_end = self.simulation_start + timedelta(days=self.simulation_duration_days)
        self.simulated_time = self.simulation_start

        self.trading_start = timedelta(hours=1, minutes=30)
        self.trading_end = timedelta(hours=19, minutes=30)
        self.batch_start = timedelta(hours=22, minutes=0)
        self.day_end = timedelta(hours=23, minutes=59, seconds=59)

        self.batch_processed = False
        self.institutions = []
        self.accounts = []
        self.instructions = []
        self.transactions = []
        self.event_log = []
        self.activity_log = []
        self.generate_data()

    def random_timestamp(self):
        delta = self.simulation_end - self.simulated_time
        random_seconds = random.uniform(0, delta.total_seconds())
        random_time = self.simulation_start + timedelta(seconds=random_seconds)
        return random_time  # Now returns a datetime object

    def log_event(self, message, agent_id, is_transaction=True):
        timestamp = self.simulated_time.strftime('%Y-%m-%d %H:%M:%S')
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
        print("Generate Accounts & Institutions:")
        print("-----------------------------------------")
        for i in range(1, self.num_institutions+ 1):
            print("-------------------------------------")
            inst_id = f"INST-{i}"
            inst_accounts = []
            total_accounts = random.randint(self.min_total_accounts, self.max_total_accounts)
            #generate cash account => there has to be at least 1 cash account
            new_cash_accountID = generate_iban()
            new_cash_accountType = "Cash"
            new_cash_balance =  round(random.uniform(100000, 200000), 2)
            new_cash_creditLimit = round(random.uniform(100000, 500000), 2)
            new_cash_Account = Account.Account(accountID=new_cash_accountID, accountType= new_cash_accountType, balance= new_cash_balance, creditLimit=new_cash_creditLimit)
            inst_accounts.append(new_cash_Account)
            self.accounts.append(new_cash_Account)
            print(new_cash_Account.__repr__())
            for _ in range(total_accounts - 1):
                new_security_accountID = generate_iban()
                new_security_accountType = random.choice(self.bond_types)
                new_security_balance = round(random.uniform(100000, 200000), 2)
                new_security_creditLimit = 0
                new_security_Account = Account.Account(accountID=new_security_accountID, accountType= new_security_accountType, balance= new_security_balance, creditLimit= new_security_creditLimit)
                inst_accounts.append(new_security_Account)
                self.accounts.append(new_security_Account)
                print(new_security_Account.__repr__())
            new_institution = InstitutionAgent.InstitutionAgent(institutionID= inst_id, accounts= inst_accounts, model=self, allowPartial=True)
            self.institutions.append(new_institution)
            print(new_institution.__repr__())
        print("-------------------------------------------------------")
        print("Accounts & Institutions generated")




    def step(self):
            time_of_day = self.simulated_time.time()

            if self.trading_start <= timedelta(hours=time_of_day.hour, minutes=time_of_day.minute) <= self.trading_end:
                #real-time processing
                self.batch_processed = False
                print(f"Running simulation step {self.steps}...")
                #shuffles all agents and then executes their step module once for all of them
                self.agents.shuffle_do("step")
                print(f"{len(self.agents)} Agents executed their step module")
            elif timedelta(hours=time_of_day.hour, minutes=time_of_day.minute) >= self.batch_start:
                if not self.batch_processed: #batch processing at 22:00 only one loop of batch_processing
                    self.batch_processing()
                    self.batch_processed = True

            self.simulated_time += timedelta(seconds=1)

            if self.simulated_time >= datetime.combine(self.simulated_time.date(), datetime.min.time()) + self.day_end:
                self.simulated_time = datetime.combine(self.simulated_time.date() + timedelta(days=1), datetime.min.time()) + self.trading_start

    def register_transaction(self,t):
        self.transactions.append(t)

    def remove_transaction(self,t):
        self.transactions.remove(t)

    def batch_processing(self):
        for transaction in self.transactions:
            if transaction.get_status() == "Matched":
                transaction.settle()






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
    try:
        while model.simulated_time < model.simulation_end:
            model.step()
    except RecursionError:
        print("RecursionError encountered: maximum recursion depth exceeded. Terminating simulation gracefully.")

    print("Final Event Log:")
    for event in model.event_log:
        print(event)
    print("Saving final event log...")
    model.save_log(log_path)
