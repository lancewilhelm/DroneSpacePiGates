#import ActiveEngine.ActiveEngine
import json

TEMPLATES_KEY = "Templates"

def gateGameObjects(gameData):
    templates = gameData[TEMPLATES_KEY]

def readJSON(filename):
    with open(filename, 'r') as myfile:
        data=myfile.read().replace('\n', '')
    return json.loads(data)

def main():
    gameObjects = []
    gameVeriables = []

    gameData = readJSON('twoMinuteRace.json')
    gameObjects = getGameObjects(gameData)
main()
