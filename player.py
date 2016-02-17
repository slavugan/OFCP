__author__ = 'Alastair Kerr'


class Player():
    def __init__(self, playerNumber=1, score=0):
        """
        Initialise player object
        Each player has a player number, a score and a Placement object with a top, middle and bottom row
        :return: None
        """
        assert isinstance(playerNumber, int)
        assert 1 <= playerNumber <= 4
        assert isinstance(score, int)

        self.playerNumber = playerNumber
        self.score = score
        self.scoresList = None # This is used to store information about a player's row scores on the current round
                               # List [Bool fouled, tuple bottom row score, tuple middle row score, tuple top row score]
