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
        self.simulation_duration_days = 5
        self.min_settlement_amount = 100
        self.bond_types = ["Bond-A", "Bond-B", "Bond-C", "Bond-D"]



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
            new_cash_balance = round(random.uniform(150000, 300000), 2)  # Increased balance range
            new_cash_creditLimit = round(random.uniform(200000, 600000), 2)
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

    def get_recursive_settled_amount(self, parent_instruction):
        """
        Recursively sum the settled amounts of all descendant (child) instructions
        for a given parent instruction.

        Parameters:
            parent_instruction: The instruction whose children (and their descendants)
                                are to be summed.
        Returns:
            The total settled amount from all descendant instructions.
        """
        total = 0.0
        for inst in self.instructions:
            # Check if this instruction is a child of the parent_instruction.
            if inst.isChild and inst.motherID == parent_instruction.get_uniqueID():
                # If the child instruction is settled, add its amount.
                if inst.get_status() in ["Settled on time", "Settled late"]:
                    total += inst.get_amount()
                # Recursively include settled amounts from further descendant instructions.
                total += self.get_recursive_settled_amount(inst)
        return total

    def calculate_settlement_efficiency(self):
        """
        Calculates settlement efficiency based on instruction pairs, including recursive
        child instructions.

        Two metrics are computed:
         - Instruction Efficiency: the percentage of original instruction pairs (mother instructions)
           that ended up fully settled (either directly or via child instructions covering the full amount).
         - Value Efficiency: the ratio (in percent) of the total settled (effective) value to the total
           intended settlement value.

        Original instructions are those with motherID == "mother", and they are grouped by their linkcode.
        In case of partial settlement (both instructions cancelled due to partial settlement), this method
        recursively aggregates settled amounts from child instructions.

        Returns:
            A tuple (instruction_efficiency_percentage, value_efficiency_percentage)
        """
        total_original_pairs = 0
        fully_settled_pairs = 0
        total_intended_value = 0.0
        total_settled_value = 0.0

        # Group original (mother) instructions by linkcode.
        original_pairs = {}
        for inst in self.instructions:
            if inst.motherID == "mother":
                original_pairs.setdefault(inst.linkcode, []).append(inst)

        for linkcode, pair in original_pairs.items():
            if len(pair) < 2:
                # We expect a pair (delivery and receipt); if not, skip this group.
                continue

            # We assume both instructions have the same intended settlement amount.
            intended_amount = pair[0].get_amount()
            total_original_pairs += 1
            total_intended_value += intended_amount

            # Case 1: Fully settled directly (both instructions settled on time or late).
            if (pair[0].get_status() in ["Settled on time", "Settled late"] and
                    pair[1].get_status() in ["Settled on time", "Settled late"]):
                fully_settled_pairs += 1
                total_settled_value += intended_amount

            # Case 2: Partial settlement – both instructions were cancelled due to partial settlement.
            elif (pair[0].get_status() == "Cancelled due to partial settlement" and
                  pair[1].get_status() == "Cancelled due to partial settlement"):
                # Recursively sum settled amounts from child instructions (and their descendants).
                settled_child_value = (self.get_recursive_settled_amount(pair[0]) +
                                       self.get_recursive_settled_amount(pair[1]))
                # The effective settled amount is capped at the intended amount.
                effective_settled = min(settled_child_value, intended_amount)
                total_settled_value += effective_settled
                # Count the pair as fully settled if the effective settled value equals the intended value.
                if effective_settled == intended_amount:
                    fully_settled_pairs += 1
            # Other statuses are considered as not settled.

        instruction_efficiency = (fully_settled_pairs / total_original_pairs * 100) if total_original_pairs > 0 else 0
        value_efficiency = (total_settled_value / total_intended_value * 100) if total_intended_value > 0 else 0

        return instruction_efficiency, value_efficiency

    def print_settlement_efficiency(self):
        """
        Quickly prints the settlement efficiency metrics.
        """
        instruction_eff, value_eff = self.calculate_settlement_efficiency()
        print("Settlement Efficiency:")
        print("  Instruction Efficiency: {:.2f}%".format(instruction_eff))
        print("  Value Efficiency: {:.2f}%".format(value_eff))

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
    print("---------------------------------------------------------------")
    model.print_settlement_efficiency()

