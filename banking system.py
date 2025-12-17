import json
from abc import ABC, abstractmethod
from uuid import uuid4

### Account Class (Abstract)
class Account(ABC):
    def __init__(self, account_number, account_holder_id, initial_balance=0.0):
        self._account_number = account_number
        self._account_holder_id = account_holder_id
        self._balance = initial_balance

    @property
    def account_number(self):
        return self._account_number

    @property
    def balance(self):
        return self._balance

    @property
    def account_holder_id(self):
        return self._account_holder_id

    @abstractmethod
    def deposit(self, amount) -> bool:
        pass

    @abstractmethod
    def withdraw(self, amount) -> bool:
        pass

    def display_details(self):
        return f"Acc No: {self.account_number}, Balance: ${self.balance:.2f}"

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "account_holder_id": self.account_holder_id,
            "balance": self.balance,
        }

### SavingsAccount Class
class SavingsAccount(Account):
    def __init__(self, account_number, account_holder_id, initial_balance=0.0, interest_rate=0.01):
        super().__init__(account_number, account_holder_id, initial_balance)
        self._interest_rate = interest_rate

    @property
    def interest_rate(self):
        return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, value):
        if value < 0:
            raise ValueError("Interest rate cannot be negative")
        self._interest_rate = value

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self._balance -= amount
            return True
        return False

    def apply_interest(self):
        self._balance += self.balance * self.interest_rate

    def display_details(self):
        return f"{super().display_details()}, Interest Rate: {self.interest_rate*100}%"

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "savings"
        data["interest_rate"] = self.interest_rate
        return data

### CheckingAccount Class
class CheckingAccount(Account):
    def __init__(self, account_number, account_holder_id, initial_balance=0.0, overdraft_limit=0.0):
        super().__init__(account_number, account_holder_id, initial_balance)
        self._overdraft_limit = overdraft_limit

    @property
    def overdraft_limit(self):
        return self._overdraft_limit

    @overdraft_limit.setter
    def overdraft_limit(self, value):
        if value < 0:
            raise ValueError("Overdraft limit cannot be negative")
        self._overdraft_limit = value

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance + self.overdraft_limit:
            self._balance -= amount
            return True
        return False

    def display_details(self):
        return f"{super().display_details()}, Overdraft Limit: ${self.overdraft_limit:.2f}"

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "checking"
        data["overdraft_limit"] = self.overdraft_limit
        return data

### Customer Class
class Customer:
    def __init__(self, customer_id, name, address):
        self._customer_id = customer_id
        self._name = name
        self._address = address
        self._account_numbers = []

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def name(self):
        return self._name

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def account_numbers(self):
        return self._account_numbers.copy()

    def add_account_number(self, account_number):
        if account_number not in self.account_numbers:
            self._account_numbers.append(account_number)

    def remove_account_number(self, account_number):
        if account_number in self._account_numbers:
            self._account_numbers.remove(account_number)

    def display_details(self):
        return f"Customer ID: {self.customer_id}, Name: {self.name}, Address: {self.address}, Accounts: {len(self.account_numbers)}"

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "address": self.address,
            "account_numbers": self.account_numbers,
        }

### Bank Class
class Bank:
    def __init__(self, customer_file='customers.json', account_file='accounts.json'):
        self._customers = {}
        self._accounts = {}
        self._customer_file = customer_file
        self._account_file = account_file
        self._load_data()

    def _load_data(self):
        try:
            with open(self._customer_file, 'r') as f:
                customers_data = json.load(f)
                for customer_id, customer_info in customers_data.items():
                    customer = Customer(customer_id, customer_info['name'], customer_info['address'])
                    customer._account_numbers = customer_info['account_numbers']
                    self._customers[customer_id] = customer
        except FileNotFoundError:
            pass
        try:
            with open(self._account_file, 'r') as f:
                accounts_data = json.load(f)
                for account_number, account_info in accounts_data.items():
                    if account_info['type'] == 'savings':
                        account = SavingsAccount(account_number, account_info['account_holder_id'], account_info['balance'], account_info['interest_rate'])
                    elif account_info['type'] == 'checking':
                        account = CheckingAccount(account_number, account_info['account_holder_id'], account_info['balance'], account_info['overdraft_limit'])
                    else:
                        continue
                    self._accounts[account_number] = account
        except FileNotFoundError:
            pass

    def _save_data(self):
        customers_data = {customer_id: customer.to_dict() for customer_id, customer in self._customers.items()}
        with open(self._customer_file, 'w') as f:
            json.dump(customers_data, f, indent=4)
        accounts_data = {account_number: account.to_dict() for account_number, account in self._accounts.items()}
        with open(self._account_file, 'w') as f:
            json.dump(accounts_data, f, indent=4)

    def add_customer(self, customer):
        if customer.customer_id not in self._customers:
            self._customers[customer.customer_id] = customer
            self._save_data()
            return True
        return False

    def remove_customer(self, customer_id):
        if customer_id in self._customers and not self._customers[customer_id].account_numbers:
            del self._customers[customer_id]
            self._save_data()
            return True
        return False

    def create_account(self, customer_id, account_type, initial_balance=0.0, **kwargs):
        if customer_id in self._customers:
            account_number = str(uuid4())
            if account_type == 'savings':
                account = SavingsAccount(account_number, customer_id, initial_balance, **kwargs)
            elif account_type == 'checking':
                account = CheckingAccount(account_number, customer_id, initial_balance, **kwargs)
            else:
                return None
            self._accounts[account_number] = account
            self._customers[customer_id].add_account_number(account_number)
            self._save_data()
            return account
        return None

    def deposit(self, account_number, amount):
        if account_number in self._accounts:
            result = self._accounts[account_number].deposit(amount)
            self._save_data()
            return result
        return False

    def withdraw(self, account_number, amount):
        if account_number in self._accounts:
            result = self._accounts[account_number].withdraw(amount)
            self._save_data()
            return result
        return False

    def transfer_funds(self, from_acc_num, to_acc_num, amount):
        if from_acc_num in self._accounts and to_acc_num in self._accounts:
            if self.withdraw(from_acc_num, amount):
                return self.deposit(to_acc_num, amount)
        return False

### Console Interface
    def run(self):
        while True:
            print("\n1. Add Customer\n2. Create Account\n3. Deposit\n4. Withdraw\n5. Transfer\n6. View Customer Accounts\n7. Apply Interest\n8. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                customer_id = input("Enter customer ID: ")
                name = input("Enter customer name: ")
                address = input("Enter customer address: ")
                customer = Customer(customer_id, name, address)
                if self.add_customer(customer):
                    print("Customer added successfully.")
                else:
                    print("Customer ID already exists.")
            elif choice == '2':
                customer_id = input("Enter customer ID: ")
                if customer_id not in self._customers:
                    print("Customer ID does not exist.")
                    continue  # Go back to menu

                account_type = input("Enter account type (savings/checking): ").lower()
                if account_type not in ['savings', 'checking']:
                    print("Invalid account type.")
                    continue

                try:
                    initial_balance = float(input("Enter initial balance: "))
                except ValueError:
                    print("Invalid balance amount.")
                    continue

                if account_type == 'savings':
                    try:
                        interest_rate = float(input("Enter interest rate: "))
                    except ValueError:
                        print("Invalid interest rate.")
                        continue
                    account = self.create_account(customer_id, account_type, initial_balance, interest_rate=interest_rate)
                else:
                    try:
                        overdraft_limit = float(input("Enter overdraft limit: "))
                    except ValueError:
                        print("Invalid overdraft limit.")
                        continue
                    account = self.create_account(customer_id, account_type, initial_balance, overdraft_limit=overdraft_limit)

                if account:
                    print(f"{account_type.capitalize()} account created successfully. Account Number: {account.account_number}")
                else:
                    print("Failed to create account.")
            elif choice == '3':
                account_number = input("Enter account number: ")
                amount = float(input("Enter amount to deposit: "))
                if self.deposit(account_number, amount):
                    print("Deposit successful.")
                else:
                    print("Deposit failed.")
            elif choice == '4':
                account_number = input("Enter account number: ")
                amount = float(input("Enter amount to withdraw: "))
                if self.withdraw(account_number, amount):
                    print("Withdrawal successful.")
                else:
                    print("Withdrawal failed.")
            elif choice == '5':
                from_acc_num = input("Enter source account number: ")
                to_acc_num = input("Enter destination account number: ")
                amount = float(input("Enter amount to transfer: "))
                if self.transfer_funds(from_acc_num, to_acc_num, amount):
                    print("Transfer successful.")
                else:
                    print("Transfer failed.")
            elif choice == '6':
                customer_id = input("Enter customer ID: ")
                if customer_id in self._customers:
                    for account_number in self._customers[customer_id].account_numbers:
                        print(self._accounts[account_number].display_details())
                else:
                    print("Customer not found.")
            elif choice == '7':
                for account_number, account in self._accounts.items():
                    if isinstance(account, SavingsAccount):
                        account.apply_interest()
                self._save_data()
                print("Interest applied to savings accounts.")
            elif choice == '8':
                print("Exiting App...")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    bank = Bank()
    bank.run()
