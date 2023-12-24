
from pyx import App, createElement

class TTTBoard:
    def __init__(self):
        self.board = [[None, None, None], [None, None, None], [None, None, None]]
        self.user1 = None
        self.user2 = None
        self.turn = 0
        self.winner = None
    
    def onClick(self, user, row, col):
        if self.board[row][col] != None: return
        if user == self.user1:
            if self.turn != 0: return
            self.board[row][col] = 0
            self.board = self.board
            self.turn = 1
        elif user == self.user2:
            if self.turn != 1: return
            self.board[row][col] = 1
            self.board = self.board
            self.turn = 0
        else:
            return
        
        self.winner = self.checkWin()
        if self.winner != None:
            self.turn = -1
    
    def checkWin(self):
        for row in range(3):
            if self.board[row][0] != None and self.board[row][0] == self.board[row][1] and self.board[row][1] == self.board[row][2]:
                return self.board[row][0]
        for col in range(3):
            if self.board[0][col] != None and self.board[0][col] == self.board[1][col] and self.board[1][col] == self.board[2][col]:
                return self.board[0][col]
        if self.board[0][0] != None and self.board[0][0] == self.board[1][1] and self.board[1][1] == self.board[2][2]:
            return self.board[0][0]
        if self.board[0][2] != None and self.board[0][2] == self.board[1][1] and self.board[1][1] == self.board[2][0]:
            return self.board[0][2]
        return None

    def __render__(self, user):
        return createElement('div', {},
            createElement('div', {
                'style': {
                    'display': 'flex',
                    'flexDirection': 'column'
                }
            }, *([
                createElement('div', {
                    'style': {
                        'display': 'flex',
                        'flexDirection': 'row'
                    }
                }, *([
                    createElement('div', {
                        'style': {
                            'width': '100px',
                            'height': '100px',
                            'border': '1px solid black',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'alignItems': 'center'
                        },
                        'onClick': (lambda row, col: lambda e: self.onClick(user, row, col))(row, col)
                    }, "" if self.board[row][col] == None else ["O", "X"][self.board[row][col]]) for col in range(3)
                ])) for row in range(3)
            ])),
            createElement('div', {}, "The winner is: " + ["O", "X"][self.winner] if self.winner != None else "")
        )

class TTTApp(App):
    def __init__(self):
        super().__init__()
        self.board = TTTBoard()
        self.user1 = None
        self.user2 = None
        self.spectators = []
    
    def onConnect(self, user):
        if self.user1 == None:
            self.user1 = user
            self.board.user1 = user
        elif self.user2 == None:
            self.user2 = user
            self.board.user2 = user
        else:
            self.spectators = self.spectators + [user]
    
    def onDisconnect(self, user):
        if self.user1 == user:
            self.user1 = None
            self.board.user1 = None
        elif self.user2 == user:
            self.user2 = None
            self.board.user2 = None
        else:
            self.spectators = [spectator for spectator in self.spectators if spectator != user]

    def __render__(self, user):
        return createElement('div', {},
            "Tic Tac Toe",
            self.board,
            createElement('div', {}, f"User 1: {self.user1.sid}") if self.user1 != None else "Waiting for user 1...",
            createElement('div', {}, f"User 2: {self.user2.sid}") if self.user2 != None else "Waiting for user 2...",
            *([createElement('div', {}, f"Spectator: {spectator.sid}") for spectator in self.spectators])
        )

app = TTTApp()
app.run()

