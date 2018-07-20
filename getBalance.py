import validate
import helpers

def getBalance(requestBody, eventsData):
    session = try_ex(lambda: requestBody['session'])
    account = try_ex(lambda: requestBody['queryResult']['parameters']['account'])
    languageCode = try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = {'account' : account}
    outputContexts = message = followUpEvent = event = error = None

    # Check if getBalance has previously been called, with user supplying an invalid account
    outputContexts = try_ex(lambda: requestBody['queryResult']['outputContexts'])
    if outputContexts is not None:
        currContext = session+"/contexts/getbalancecontext"
        for context in outputContexts:
            if context['name'] == currContext:
                error = try_ex(lambda: context['parameters']['error'])

    if account is not None and account !="":
        if isvalidAccount(account):
            remainingBalance = try_ex(lambda: hardcodedAccountBalance[account])
            message = eventsData['GET_BALANCE']['languages'][languageCode][0].format(account, remainingBalance)
            return createResponseBody(message, outputContexts, followUpEvent)
        else: #Store error flag in parameters so that when getBalance is called again the error message is shown
            parameters['error'] = True
            parameters['event'] = 'GET_BALANCE'
            contextName = session + '/contexts/getbalancecontext'
    else:
        contextName = session + '/contexts/getbalancecontext'
        parameters['event'] = 'GET_BALANCE'
        if error == True: #Show the error message if error has previously been set
            message = eventsData['GET_BALANCE']['languages'][languageCode][1]
        else: # Else simply ask user for account type with no error msg
            message = eventsData['GET_BALANCE']['languages'][languageCode][2]

    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    return createResponseBody(message, outputContexts, followUpEvent) 
