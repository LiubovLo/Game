import random


# Исключения для игры
class BoardException(Exception):
    pass


class OutOfBoardException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски!"


class UsedCellException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class ShipPlacementException(BoardException):
    pass


# Класс точки на поле
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


# Класс корабля
class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    @property
    def points(self):
        ship_points = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.direction == 0:
                cur_x += i

            elif self.direction == 1:
                cur_y += i

            ship_points.append(Point(cur_x, cur_y))
        return ship_points


# Класс игрового поля
class Board:
    def __init__(self, hidden=False, size = 6):
        self.size = size
        self.hidden = hidden
        self.count = 0
        self.field = [ ["O"]*size for _ in range(size) ]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for p in ship.points:
            if self.out_of_board(p) or p in self.busy:
                raise ShipPlacementException()
        for p in ship.points:
            self.field[p.x][p.y] = "■"
            self.busy.append(p)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, visible=False):
        for p in ship.points:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    cur = Point(p.x + dx, p.y + dy)
                    if not self.out_of_board(cur) and cur not in self.busy:
                        if visible:
                            self.field[cur.x][cur.y] = "T"
                        self.busy.append(cur)



    def __str__(self):
        result = ""
        result += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            result += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hidden:
            result = result.replace("■", "O")
        return result

    def out_of_board(self, point):
        return not (0 <= point.x < self.size and 0 <= point.y < self.size)

    def shot(self, p):
        if self.out_of_board(p):
            raise OutOfBoardException()
        if p in self.busy:
            raise UsedCellException()
        self.busy.append(p)

        for ship in self.ships:
            if p in ship.points:
                ship.lives -= 1
                self.field[p.x][p.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, visible=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[p.x][p.y] = "T"
        print("Мимо!")
        return False
    def begin(self):
        self.busy = []
    def defeat(self):
        return all(ship.lives == 0 for ship in self.ships)


# Класс игрока
class Player:
    def __init__(self, board, opponent_board):
        self.board = board
        self.opponent_board = opponent_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.opponent_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        p = Point(random.randint(0, 5), random.randint(0, 5))
        print(f"Ход компьютера: {p.x + 1} {p.y + 1}")
        return p


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Point(x - 1, y - 1)


# Класс игры
class Game:
    def __init__(self):
        player_board = self.random_board()
        ai_board = self.random_board(hidden=True)
        self.ai = AI(ai_board, player_board)
        self.user = User(player_board, ai_board)

    def random_board(self, hidden=False):
        board = None
        while board is None:
            board = self.try_create_board(hidden)
        return board

    def try_create_board(self, hidden):
        board = Board(hidden)
        attempts = 0
        for length in [3, 2, 2, 1, 1, 1, 1]:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Point(random.randint(0, 5), random.randint(0, 5)), length, random.randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except ShipPlacementException:
                    pass
        board.begin()
        return board

    def loop(self):
        turn = 0
        while True:
            print("\nВаша доска:")
            print(self.user.board)
            print("\nДоска противника:")
            print(self.ai.board)
            if turn % 2 == 0:
                print("\nВаш ход!")
                repeat = self.user.move()
            else:
                print("\nХодит компьютер!")
                repeat = self.ai.move()
            if repeat:
                turn -= 1
            if self.ai.board.defeat():
                print("\nВы победили!")
                break
            if self.user.board.defeat():
                print("\nВы проиграли!")
                break
            turn += 1

    def start(self):
        print("Начинаем игру!")
        self.loop()


# Запуск игры
g = Game()
g.start()
