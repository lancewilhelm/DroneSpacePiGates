#import ActiveEngine.ActiveEngine
import json
import ActiveObject
import ActiveVariable
import ActiveMethod

TEMPLATES_KEY = "Templates"
TEMPLATE_METHOD_KEY = "methods"
TEMPLATE_VARIABLE_KEY = "variables"

def getGameObjects(gameData):
    print("gathering templates")
    templates = gameData[TEMPLATES_KEY]
    activeObjects = []
    for activeObjectKey in templates:
        activeObject = templates[activeObjectKey]
        print(activeObjectKey)
        methods = []
        variables = []
        for activeMethodKey in activeObject[TEMPLATE_METHOD_KEY]:
            activeMethodJSON = activeObject[TEMPLATE_METHOD_KEY]
            print(" - "+activeMethodKey+"()")
            activeMethod = activeMethodJSON[activeMethodKey]
            method = ActiveMethod.ActiveMethod(activeMethod)
            methods.append(method)

        for activeVariableKey in activeObject[TEMPLATE_VARIABLE_KEY]:
            activeVariableJSON = activeObject[TEMPLATE_VARIABLE_KEY]
            print(" - "+activeVariableKey)
            activeVariable = activeVariableJSON[activeVariableKey]
            variable = ActiveVariable.ActiveVariable(activeVariableKey,activeVariable)
            variables.append(variable)

        newObject = ActiveObject.ActiveObject(variables,methods)
        activeObjects.append(newObject)
    print("got "+str(len(activeObjects))+" template objects")
    return activeObjects

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
