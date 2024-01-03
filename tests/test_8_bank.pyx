
from pyx import App, createElement

class Account:
    def __render__(self, user):
        return (
            <div>Balance: {self.user['balance']}
                {[
                    <button onClick={lambda e: self.deposit(10)}>Deposit</button>,
                    <button onClick={lambda e: self.withdraw(10)}>Withdraw</button>
                ] if user == self.user else [
                    <button onClick={lambda e: self.sendTo(user, 10)}>Send</button>
                ]}
            </div>
        )

class Bank(App):
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

