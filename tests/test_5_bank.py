
from pyx import App, createElement

class Account:
    def __init__(self, user):
        self.user = user

    def deposit(self, amount):
        self.user['balance'] += amount
        print(f"Deposited {amount} to {self.user['name']}")

    def withdraw(self, amount):
        self.user['balance'] -= amount
        print(f"Withdrew {amount} from {self.user['name']}")

    def __render__(self, user):
        return createElement(
            "div",
            {},
            f"Balance: {self.user['balance']}",
            *([createElement(
                "button",
                {
                    "onClick": lambda e: self.deposit(10)
                },
                "Deposit"
            ),
            createElement(
                "button",
                {
                    "onClick": lambda e: self.withdraw(10)
                },
                "Withdraw"
            )] if user == self.user else [])
        )

class Bank(App):
    def __init__(self):
        super().__init__()
    
    def onConnect(self, user):
        user['account'] = Account(user)
        user['balance'] = 0
    
    def __render__(self, user):
        return createElement(
            "div",
            {},
            f"Balance: {user['balance']}",
            *[
                u['account']
                for u in self.users.values()
            ]
        )

app = Bank()
app.run()

