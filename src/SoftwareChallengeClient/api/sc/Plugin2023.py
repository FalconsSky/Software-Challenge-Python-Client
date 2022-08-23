import src.SoftwareChallengeClient.api.networking.xflux.XFluxDecorator as XStrDec
from src.SoftwareChallengeClient.api.networking.xflux.XFluxInterface import ImplicitArray, Attribute, Traverse, \
    ChildAttribute


class Vector:
    """
    Represents a vector in the hexagonal grid. It can calculate various vector operations.
    """

    def __init__(self, dx: int = 0, dy: int = 0):
        """
        Constructor for the Vector class.
        :param dx: The x-coordinate of the vector.
        :param dy: The y-coordinate of the vector.
        """
        self.dx = dx
        self.dy = dy

    def length(self):
        """
        Calculates the length of the vector.
        :return: The length of the vector.
        """
        return (self.dx ** 2 + self.dy ** 2) ** 0.5

    def times(self, scalar: int):
        """
        Extends the vector by a scalar.
        :param scalar: The scalar to extend the vector by.
        :return: The extended vector.
        """
        return Vector(self.dx * scalar, self.dy * scalar)

    def plus(self, other: 'Vector'):
        """
        Adds two vectors.
        :param other: The other vector to add.
        :return: The sum of the two vectors as a new vector object.
        """
        return Vector(self.dx + other.dx, self.dy + other.dy)

    def minus(self, other: 'Vector'):
        """
        Subtracts two vectors.
        :param other: The other vector to subtract.
        :return: The difference of the two vectors as a new vector object.
        """
        return Vector(self.dx - other.dx, self.dy - other.dy)

    def compareTo(self, other: 'Vector'):
        """
        Compares two vectors.
        :param other: The other vector to compare to.
        :return: True if the vectors are equal, false otherwise.
        """
        return self.dx == other.dx and self.dy == other.dy

    @property
    def DIRECTIONS(self) -> list['Vector']:
        """
        Gets the six neighbors of the vector.
        :return: A list of the six neighbors of the vector.
        """
        return [
            Vector(1, -1),  # UP RIGHT
            Vector(-2, 0),  # LEFT
            Vector(1, 1),  # DOWN RIGHT
            Vector(-1, 1),  # DOWN LEFT
            Vector(2, 0),  # Right
            Vector(-1, -1)  # UP LEFT
        ]

    def isOneHexMove(self):
        """
        Checks if the vector is a one hex move.
        :return: True if the vector is a one hex move, false otherwise.
        """
        return abs(self.dx) == abs(self.dy) or (self.dx % 2 == 0 and self.dy == 0)

    def toCoordinates(self) -> 'Coordinates':
        """
        Converts the vector to coordinate object.
        :return:    The coordinate object.
        """
        return Coordinates(self.dx, self.dy, isDouble=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the vector.
        :return: The string representation of the vector.
        """
        return "Vector({}, {})".format(self.dx, self.dy)


@XStrDec.alias(name='coordinates')
@XStrDec.alias(name='to')
@XStrDec.alias(name='from')
class Coordinates:
    """
    Representation of a coordination system in the hexagonal grid.
    """

    def __init__(self, x: int, y: int, isDouble: bool = True):
        """
        Constructor for the Coordinates class.
        :param x: The x-coordinate of the coordination system.
        :param y: The y-coordinate of the coordination system.
        :param isDouble: Determines if the coordinate is in double hex format. Default is True.
        """
        self.x = x
        self.y = y
        self.isDouble = isDouble

    def addVector(self, vector: Vector) -> 'Coordinates':
        """
        Adds a vector to the coordinate.
        :param vector: The vector to add.
        :return: The new coordinate.
        """

        return self.getVector().plus(vector).toCoordinates() if self.isDouble else \
            self.getDoubleHex().getVector().plus(vector).toCoordinates().getArray()

    def minusVector(self, vector: Vector) -> 'Coordinates':
        """
        Subtracts a vector from the coordinate.
        :param vector: The vector to subtract.
        :return: The new coordinate.
        """
        return self.getVector().minus(vector).toCoordinates()

    def getDistance(self, other: 'Coordinates') -> 'Coordinates':
        """
        Calculates the distance between two coordinates.
        :param other: The other coordinate to calculate the distance to.
        :return: The distance between the two coordinates as Vector object.
        """
        return self.getVector().minus(other.getVector()).toCoordinates()

    def getVector(self) -> Vector:
        """
        Gets the vector from the coordinate to the origin.
        :return: The vector from the coordinate to the origin.
        """
        return Vector(self.x, self.y)

    def getHexNeighbors(self) -> list[Vector]:
        """
        Gets the six neighbors of the coordinate.
        :return: A list of the six neighbors of the coordinate.
        """
        ...

    def arrayToDoubleHex(self) -> 'Coordinates':
        """
        Converts the coordinate to double hex coordinates.
        :return: The double hex coordinates.
        """
        return Coordinates(self.x * 2 + (1 if self.y % 2 == 1 else 0), self.y, True)

    def doubleHexToArray(self) -> 'Coordinates':
        """
        Converts the double hex coordinates to coordinate.
        :return: The coordinate.
        """
        return Coordinates(int(self.x / 2 - (1 if self.y % 2 == 1 else 0)), self.y, False)

    def getArray(self) -> 'Coordinates':
        """
        Checks if the coordinate is an array or double hex coordinate.
        :return: Self if the coordinate is an array, doubleHexToArray if the coordinate is a double hex coordinate.
        """
        return self if not self.isDouble else self.doubleHexToArray()

    def getDoubleHex(self) -> 'Coordinates':
        """
        Checks if the coordinate is a double hex coordinate.
        :return: Self if the coordinate is a double hex coordinate, doubleHexToArray if the coordinate is an array.
        """
        return self if self.isDouble else self.arrayToDoubleHex()

    def __str__(self) -> str:
        return "Coordinates[{}, {}], Double: {}".format(self.x, self.y, self.isDouble)


@XStrDec.alias(name='move')
@XStrDec.alias(name='lastMove')
@XStrDec.attrDict(attr="toCoo", name="to")
@XStrDec.attrDict(attr="fromCoo", name="from")
class Move:
    """
    Represents a move in the game. 
    """

    def __init__(self, toCoo: Coordinates, fromCoo: Coordinates = None):
        """
        :param toCoo: The destination of the move.
        :param fromCoo: The origin of the move.
        """
        coordinates = {
            None if fromCoo is None else "from": None if fromCoo is None else {
                "x": fromCoo.x,
                "y": fromCoo.y
            },
            "to": {
                "x": toCoo.x,
                "y": toCoo.y
            }
        }
        self.__from__to = ChildAttribute(self, children=coordinates, fieldValues=[fromCoo, toCoo])

    @property
    def fromCoo(self):
        return self.__from__to.fieldValues[0]

    @property
    def toCoo(self):
        return self.__from__to.fieldValues[1]

    @toCoo.setter
    def toCoo(self, value: Coordinates):
        self.__from__to.fieldValues[1] = value

    def getDelta(self):
        """
        Gets the distance between the origin and the destination.
        :return: The delta of the move as a Vector object.
        """
        return self.toCoo.getDistance(self.fromCoo)

    def reversed(self):
        """
        Reverses the move.
        :return: The reversed move.
        """
        return Move(self.fromCoo, self.toCoo)

    def compareTo(self, other: 'Move'):
        """
        Compares two moves.
        :param other: The other move to compare to.
        :return: True if the moves are equal, false otherwise.
        """
        return self.fromCoo.compareTo(other.fromCoo) and self.toCoo.compareTo(other.toCoo)

    def __str__(self) -> str:
        return "Move from {} to {}".format(self.fromCoo, self.toCoo)

    @staticmethod
    def move(origin: Coordinates, delta: Vector) -> 'Move':
        """
        Executes the move to the destination.
        :param origin: The origin of the move.
        :param delta: The delta of the move.
        :return: The new move.
        """
        return Move(origin.addVector(delta), origin)


@XStrDec.alias(name='team')
@XStrDec.alias(name='startTeam')
class Team:

    def __init__(self, color: str):
        self.ONE = {
            'opponent': 'TWO',
            'name': 'ONE',
            'letter': 'R',
            'color': 'Rot'
        }
        self.TWO = {
            'opponent': 'ONE',
            'name': 'TWO',
            'letter': 'B',
            'color': 'Blau'
        }
        self.teamEnum = None
        if color == "ONE":
            self.teamEnum = self.ONE
        elif color == "TWO":
            self.teamEnum = self.TWO
        else:
            raise Exception("Invalid : {}".format(color))

    def team(self) -> 'Team':
        return self

    def color(self) -> str:
        return self.teamEnum['color']

    def opponent(self) -> 'Team':
        return Team(self.teamEnum['opponent'])

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Team) and self.teamEnum['name'] == __o.teamEnum['name']

    def __str__(self) -> str:
        return "Team {}.".format(self.teamEnum['name'])


@XStrDec.alias(name='field')
class Field:
    def __init__(self, field: int | str | Team = None):
        self.field: int | str | Team
        if not field or isinstance(field, Team):
            self.field = field
        elif field.isnumeric():
            self.field = int(field)
        elif field.isalpha():
            self.field = Team(field)
        else:
            raise TypeError("The field's input is wrong: {}".format(field))

    def isEmpty(self) -> bool:
        return self.field == 0

    def isOccupied(self) -> bool:
        return isinstance(self.field, Team)

    def getFish(self) -> None | int:
        return None if self.isOccupied() else self.field

    def getPenguin(self) -> Team | None:
        return self.field if isinstance(self.field, Team) else None

    def __copy__(self):
        return Field(self.field)

    def __str__(self):
        return ("This Field is occupied by {}".format(self.field)) + (
            " fish(es)" if isinstance(self.field, int) else "")


@XStrDec.alias(name='list')
class HexBoard:
    def __init__(self, gameField: list[list[Field]] = None):
        self.__gameField = ImplicitArray(caller=self, fieldName="gameField", fieldValue=gameField)

    @property
    def gameField(self):
        return self.__gameField.fieldValue

    def areFieldsEmpty(self) -> bool:
        for row in self.gameField:
            for field in row:
                if not field.isEmpty():
                    return False
        return True

    def isOccupied(self, coordinates: Coordinates) -> bool:
        arrayCoordinates = coordinates.getArray()
        return self.getField(arrayCoordinates).isOccupied()

    def isValid(self, coordinates: Coordinates) -> bool:
        arrayCoordinates = coordinates.getArray()
        return 0 <= arrayCoordinates.x < len(self.gameField) and 0 <= arrayCoordinates.y < len(self.gameField[0])

    def width(self) -> int:
        return len(self.gameField)

    def height(self) -> int:
        return len(self.gameField[0])

    def __getField(self, x: int, y: int) -> Field:
        """
        Gets the field at the given coordinates.
        *Used only internally*

        :param x: The x-coordinate of the field.
        :param y: The y-coordinate of the field.
        :return: The field at the given coordinates.
        """
        return self.gameField[x][y]

    def getField(self, position: Coordinates) -> Field:
        """
        Gets the field at the given position.
        :param position: The position of the field.
        :return: The field at the given position.
        :raise IndexError: If the position is not valid.
        """
        arrayCoordinates = position.getArray()
        if self.isValid(arrayCoordinates):
            return self.__getField(arrayCoordinates.x, arrayCoordinates.y)
        else:
            raise IndexError("Index out of range: [x={}, y={}]".format(arrayCoordinates.x, arrayCoordinates.y))

    def getFieldOrNone(self, position: Coordinates) -> Field | None:
        """
        Gets the field at the given position no matter if it is valid or not.
        :param position: The position of the field.
        :return: The field at the given position,or None if the position is not valid.
        """
        position = position.getArray()
        if self.isValid(position):
            return self.__getField(position.x, position.y)
        else:
            return None

    def getFieldByIndex(self, index: int) -> Field:
        """
        Gets the field at the given index. The index is the position of the field in the board. 
        The field of the board is calculated as follows:

        - `x = index / width`
        - `y = index % width`
        - The index is 0-based. The index is calculated from the top left corner of the board. 

        :param index: The index of the field.
        :return: The field at the given index.
        """
        x = index // self.width()
        y = index % self.width()
        return self.getField(Coordinates(x, y, False))

    def getAllFields(self) -> list[Field]:
        """
        Gets all hexFields of the board.
        :return: All hexFields of the board.
        """
        return [self.getFieldByIndex(i) for i in range(self.width() * self.height())]

    def compareTo(self, other: 'HexBoard') -> list[Field]:
        """
        Compares two boards and returns a list of the hexFields that are different.
        :param other: The other board to compare to.
        :return: A list of hexFields that are different or a empty list if the boards are equal.
        """
        fields = []
        for x in range(len(self.gameField)):
            for y in range(len(self.gameField[0])):
                if self.gameField[x][y] != other.gameField[x][y]:
                    fields.append(self.gameField[x][y])
        return fields

    def contains(self, field: Field) -> bool:
        for row in self.gameField:
            if field in row:
                return True
        return False

    def containsAll(self, fields: list[Field]) -> bool:
        for field in fields:
            if not self.contains(field):
                return False
        return True

    def __str__(self) -> str:
        return str(self.gameField)

    def __copy__(self):
        return HexBoard(self.gameField)

    def __eq__(self, other):
        return self.compareTo(other)

    def __hash__(self) -> int:
        return hash(self.gameField)


@XStrDec.alias(name='board')
class Board:
    """
    Class which represents a game board. Consisting of a two-dimensional array of hexFields.
    """

    def __init__(self, hexBoard: HexBoard):
        self.__fields = Traverse(self, hexBoard)

    @property
    def hexFields(self) -> HexBoard:
        return self.__fields.fieldValue

    def getMovesInDirection(self, origin: Coordinates, direction: Vector) -> list[Move]:
        # Get all hexFields in all directions to infinity or until a field is not valid and add them to a list of moves.
        moves = []
        for i in range(1, self.hexFields.width()):
            try:
                moves.append(Move(fromCoo=origin, toCoo=origin.getDoubleHex().addVector(direction.times(i))))
            except IndexError:
                break
        return moves

    def __isDirectionValid(self, field: Coordinates) -> bool:
        arrayCoordinate = field.getArray()
        return self.hexFields.isValid(arrayCoordinate) and not self.hexFields.isOccupied(arrayCoordinate) and not \
            self.hexFields.getField(arrayCoordinate).isEmpty()

    def possibleMovesFrom(self, position: Coordinates) -> list[Move]:
        """
        Returns a list of all possible moves from the given position. That are all moves in all hexagonal directions.
        :param position: The position to start from.
        :return: A list of all possible moves from the given position.
        :raise: IndexError if the position is not valid.
        """
        if not self.hexFields.isValid(position):
            raise IndexError("Index out of range: [x={}, y={}]".format(position.x, position.y))
        moves = []
        for direction in Vector().DIRECTIONS:
            moves.extend(self.getMovesInDirection(position, direction))
        return moves

    def getPenguins(self) -> list[Field]:
        """
        Searches the board for all penguins.
        :return: A list of all hexFields that are occupied by a penguin.
        """
        return [field for field in self.hexFields.getAllFields() if field.isOccupied()]

    def getTeamsPenguins(self, team: Team) -> list[Coordinates]:
        # Loop over the hexFields 2d array:
        teamsPenguins = []
        for x in range(self.hexFields.width()):
            for y in range(self.hexFields.height()):
                currentField = self.hexFields.getField(Coordinates(x, y, False))
                if currentField.isOccupied() and currentField.getPenguin().team() == team:
                    coordinates = Coordinates(x, y, False).getDoubleHex()
                    print("Piece: ", currentField)
                    teamsPenguins.append(coordinates)
        return teamsPenguins

    def __eq__(self, other):
        return self.hexFields == other.hexFields


@XStrDec.alias(name='fishes')
class Fishes:
    def __init__(self, fishesOne: int, fishesTwo: int):
        self.__fishesOne = fishesOne
        self.__fishesTwo = fishesTwo

    @property
    def fishesOne(self):
        return self.__fishesOne

    @property
    def fishesTwo(self):
        return self.__fishesTwo


@XStrDec.alias(name='state')
@XStrDec.childAttribute(name="startTeam", mappedClass=Team)
class GameState:
    """
       A `GameState` contains all information, that describes the game state at a given time, that is, between two game
       moves.

       This includes:
         - a consecutive turn number (round & turn) and who's turn it is
         - the board
         - the last move made

       The `GameState` is thus the central object through which all essential information of the current game can be
       accessed.

       Therefore, for easier handling, it offers further aids, such as:
         - a method to calculate available moves and to execute moves

       The game server sends a new copy of the `GameState` to both participating players after each completed move,
       describing the then current state. Information about the course of the game can only be obtained from the
       `GameState` to a limited extent and must therefore be recorded by a game client itself if necessary.

       In addition to the actual information certain partial information can be queried.
       """

    def __init__(self, board: Board, turn: int, startTeam: Team, fishes: Fishes, lastMove: Move = None):
        """
        Creates a new `GameState` with the given parameters.
        :param board: The board of the game.
        :param turn: The turn number of the game.
        :param startTeam: The team that has the first turn.
        :param fishes: The number of fishes each team has.
        :param lastMove: The last move made.
        """
        self.startTeam = startTeam
        self.__board = Traverse(self, board)
        self.__turn = Attribute(caller=self, fieldName="turn", fieldValue=turn)
        self.round = int((self.turn + 1) / 2)
        self.currentTeam = self.currentTeamFromTurn()
        self.otherTeam = self.currentTeamFromTurn().opponent()
        self.lastMove = lastMove
        self.fishes = fishes
        self.currentPieces = self.board.getTeamsPenguins(self.currentTeam)

    @property
    def board(self) -> Board:
        return self.__board.fieldValue

    @property
    def turn(self):
        return int(self.__turn.fieldValue)

    def getPossibleMoves(self) -> list[Move]:
        """
        Gets all possible moves for the current team.
        That includes all possible moves from all hexFields that are not occupied by a penguin from that team.
        :return: A list of all possible moves from the current player's turn.
        """
        moves = []
        if len(self.currentPieces) < 4:
            hexBoard = self.board.hexFields
            for x in range(hexBoard.width() - 1):
                for y in range(hexBoard.height() - 1):
                    field = hexBoard.getField(Coordinates(x, y, False))
                    if not field.isOccupied() and field.getFish() == 1:
                        moves.append(Move(fromCoo=None, toCoo=Coordinates(x, y, False).getDoubleHex()))
        else:
            for piece in self.currentPieces:
                print(piece)
                moves.extend(self.board.possibleMovesFrom(piece))
        return moves

    def currentTeamFromTurn(self) -> Team:
        """
        Calculates the current team from the turn number.
        :return: The team that has the current turn.
        """
        return self.startTeam if self.turn % 2 == 0 else self.startTeam.opponent()
