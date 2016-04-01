__author__ = 'Alastair Kerr'

import json

from ofc import OFC
from pineapple import Pineapple
import gameHandlerHelpers


class GameHandler(object):
    def __init__(self, variant='ofc', playerCount=2, gameState={}):
        """
        Initialises game handler object
        Game handler communicates between server and back end logic
        :return: None
        """
        assert isinstance(variant, basestring)
        assert variant.lower() in ['ofc', 'pineapple']
        assert isinstance(playerCount, int)
        assert 1 < playerCount <= 4
        assert isinstance(gameState, dict)

        self.playerCount = playerCount
        self.gameState = gameState
        firstToAct, nextToAct, actingOrderPointer, roundNumber, roundActionNumber, deck, deckPointer = 1, 1, 0, 1, 1, None, 0
        if (gameState != {}):
            # Game state info overrides existing variables e.g. playerCount
            self.interpretPlayerCount(gameState)
            firstToAct, nextToAct, actingOrderPointer, roundNumber, roundActionNumber, deck, deckPointer = \
                self.interpretGameVars(gameState['gameState'])

        self.game = None
        # Create a game object for the desired variant using any read in variables
        if (variant.lower() == 'ofc'):
            self.game = OFC(playerCount=self.playerCount, firstToAct=firstToAct, nextToAct=nextToAct, \
                            actingOrderPointer=actingOrderPointer, roundNumber=roundNumber, variant='ofc', \
                            roundActionNumber=roundActionNumber, deck=deck, deckPointer=deckPointer)
        elif (variant.lower() == 'pineapple'):
            self.game = Pineapple(playerCount=self.playerCount, firstToAct=firstToAct, nextToAct=nextToAct, \
                            actingOrderPointer=actingOrderPointer, roundNumber=roundNumber, variant='pineapple', \
                            roundActionNumber=roundActionNumber, deck=deck, deckPointer=deckPointer)

        if (gameState != {}):
            # Update game state objects with read in information
            self.interpretGameStatePlacements(gameState)
            self.interpretPlayerCards(gameState)

    def interpretPlayerCount(self, gameState={}):
        """
        Reads game state playerNumber to work out how many player objects to initialise the game object with
        :param gameState: dict game state
        :return: None
        """
        assert isinstance(gameState, dict)
        assert 'playerCount' in gameState.keys()
        self.playerCount = gameState['playerCount']
        assert isinstance(self.playerCount, int)
        assert 1 < self.playerCount <= 4

    def interpretPlayerCards(self, gameState={}):
        """
        Interprets player cards from game state and updates game objects
        :param gameState: Game State dict
        :return: None
        """
        assert isinstance(gameState, dict)
        for i in range(1, self.playerCount+1):
            self.game.players[i-1].cards = gameHandlerHelpers.convertStringToCards(gameState['players'][str(i)]['cards'])

    def interpretGameVars(self, gameState={}):
        """
        Interprets game and round variables and returns these to initialise game objects with
        :param gameState: 'gameState' key:dict
        :return: firstToAct, nextToAct, actingOrderPointer, roundNumber, roundActionNumber, deck, deckPointer
        """
        firstToAct = gameState['firstToAct']
        nextToAct = gameState['nextToAct']
        actingOrderPointer = gameState['actingOrderPointer']
        roundNumber = gameState['roundNumber']
        roundActionNumber = gameState['roundActionNumber']
        deck = gameState['deck']
        deckPointer = gameState['deckPointer']
        return firstToAct, nextToAct, actingOrderPointer, roundNumber, roundActionNumber, deck, deckPointer

    def interpretGameStatePlacements(self, gameState={}):
        """
        Interprets the gameState placements and updates the game objects with this information
        :return: None
        """
        nestedPlacementsDict = gameState['gameState']['placements']
        for playerKey in nestedPlacementsDict.keys():
            self.interpretPlayerPlacements(nestedPlacementsDict, playerKey)

    def interpretPlayerPlacements(self, placementsDic, key):
        """
        Reads dictionary and interprets the placements and updates the game's board object with this information
        :param placementsDic: Gamestate dictionary at nested level ['gameState']['placements']
        :param key: The desired player whose placements are to be interpreted i.e. '1', '2', '3', '4'
        :return: None
        """
        assert isinstance(placementsDic, dict)
        assert isinstance(key, basestring)
        assert key in ['1', '2', '3', '4']
        self.game.board.setPlacements(playerNumber=int(key), \
                                   bottomRowCards=gameHandlerHelpers.convertStringToCards(placementsDic[key]['bottomRow']), \
                                   middleRowCards=gameHandlerHelpers.convertStringToCards(placementsDic[key]['middleRow']), \
                                   topRowCards=gameHandlerHelpers.convertStringToCards(placementsDic[key]['topRow']))

    def getCompiledGameState(self):
        """
        Returns the compile JSON game state for the game object associated with this handler instance
        :return: Game state JSON
        """
        return gameHandlerHelpers.compileGameState(self.game)

    def getNextActionDetails(self):
        """
        Calls game object to determine next action
        :return: [Player number, round action number, cards to place]
        """
        return self.game.handleNextAction()


if __name__ == "__main__":
    # Testing functionality
    jsonFile = json.load(open("json_test"))
    g = GameHandler(variant='ofc', gameState=jsonFile)
    pNum = 1
    # Board object setPlacements method sets placements in an array, index[0] -> player 1, index[1] -> player 2 ...
    for p in g.game.board.placements:
        print "Player %s: Bottom %s (%s), middle %s (%s), top %s (%s)" % \
              (pNum, p.bottomRow.humanReadable(), p.bottomRow.classifyRow(), \
               p.middleRow.humanReadable(), p.middleRow.classifyRow(), \
               p.topRow.humanReadable(), p.topRow.classifyRow() )
        pNum += 1
    print "\nNow interpreting scores for this game state...\n"
    print g.game.interpretScores()
    print g.getCompiledGameState()