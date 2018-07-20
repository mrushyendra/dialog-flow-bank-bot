import validate
import helpers

# --- Entry Point for intent ---     

def transferFunds(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    account = validate.try_ex(lambda: requestBody['queryResult']['parameters']['account'])
    amount = validate.try_ex(lambda: requestBody['queryResult']['parameters']['amount'])
    recipient = validate.try_ex(lambda: requestBody['queryResult']['parameters']['recipient'])

    parameters = {'account' : account, 'amount' : amount, 'recipient' : recipient}
    
    outputContexts = message = followUpEvent = None
    
    # Checks the validity of each slot sequentially, calling the appropriate event if any slot is invalid/incomplete, or if all slots have been filled
    if recipient is not None and recipient != "" and validate.isvalidRecipient(recipient):
        if account is not None and account != "" and validate.isvalidAccount(account):
            if amount is not None and amount != "" and validate.isvalidAmount(helpers.hardcodedAccountBalance, amount, account):
                parameters['event'] = 'FUNDS_TRANSFER_CONFIRM_TRANSFER'
                contextName = session+"/contexts/confirm_fundstransfercontext"
            else:
                parameters['event'] = 'FUNDS_TRANSFER_GET_AMOUNT'
                contextName = session+"/contexts/getamount_fundstransfercontext"
        else:
            parameters['event'] = 'FUNDS_TRANSFER_GET_ACCOUNT'
            contextName = session+"/contexts/getaccount_fundstransfercontext"
    else: #default next intent if no parameters are provided
        parameters['event'] = 'FUNDS_TRANSFER_GET_RECIPIENT'
        contextName = session+"/contexts/getrecipient_fundstransfercontext"

    # Store parameters like account, amount, etc. if supplied and send to the subsequent intent
    outputContexts = [
                {
                    "name": contextName,
                    "lifespanCount": 1,
                    "parameters": parameters
                }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    return helpers.createResponseBody(message, outputContexts, followUpEvent)

# --- Functions that deal with individual secondary intents (i.e. for elciting and validating slots, asking for confirmation) ---
# --- Nomenclature: secondaryIntentName_mainIntentName e.g. getAccount_fundsTransfer is the function that deals with the get Account intent
# for the funds transfer goal ---

def confirm_fundsTransfer(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])

    parameters = validate.try_ex(lambda: requestBody['queryResult']['parameters'])
    confirm = validate.try_ex(lambda: requestBody['queryResult']['parameters']['confirm'])
    message = event = account = amount = recipient = None
    
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/confirm_fundstransfercontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            account = validate.try_ex(lambda: context['parameters']['account'])
            amount = validate.try_ex(lambda: context['parameters']['amount'])
            recipient = validate.try_ex(lambda: context['parameters']['recipient'])
            if confirm is None:
                confirm = validate.try_ex(lambda: context['parameters']['confirm'])

    parameters['event'] = event   
    parameters['confirm'] = confirm
    parameters['account'] = account
    parameters['amount'] = amount
    parameters['recipient'] = recipient

    if confirm is not None and confirm != "":
        if confirm == 'yes':
            remainingBalance = helpers.deductAccountBalance(helpers.hardcodedAccountBalance, account, amount) #Requires backend API call in actual code
            message = eventsData[event]['languages'][languageCode][0].format(amount['amount'], recipient, account, remainingBalance)
            return helpers.createResponseBody(message, None, None)
        else:
            message = eventsData[event]['languages'][languageCode][1]
            return helpers.createResponseBody(message, None, None)
    else:
        parameters['event'] = 'FUNDS_TRANSFER_CONFIRM_TRANSFER'
        followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
        contextName = session+"/contexts/confirm_fundstransfercontext"
        outputContexts = [
                {
                    "name": contextName,
                    "lifespanCount": 1,
                    "parameters": parameters
                }]
        message = eventsData[event]['languages'][languageCode][2].format(amount['amount'], recipient, account)
        return helpers.createResponseBody(message, outputContexts, followUpEvent)

def getAmount_fundsTransfer(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = validate.try_ex(lambda: requestBody['queryResult']['parameters'])
    amount = validate.try_ex(lambda: parameters['amount'])
    event = error = account = recipient = message = followUpEvent = None
     
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getamount_fundstransfercontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            error = validate.try_ex(lambda: context['parameters']['error'])
            recipient = validate.try_ex(lambda: context['parameters']['recipient'])
            account = validate.try_ex(lambda: context['parameters']['account'])
    parameters['event'] = event
    parameters['recipient'] = recipient
    parameters['account'] = account
    
    if amount is not None and amount != "" and account is not None and account != "":
        if validate.isvalidAmount(helpers.hardcodedAccountBalance, amount, account):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session+"/contexts/" + eventsData[event]['nextContext']
        else:
            parameters['error'] = True
            contextName = session + "/contexts/getamount_fundstransfercontext"
    else: #Unfilled
        contextName = session + "/contexts/getamount_fundstransfercontext"
        if(error == True):
            message = eventsData[event]['languages'][languageCode][0].format(parameters['account'])
        else:
            message = eventsData[event]['languages'][languageCode][1]

    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    return helpers.createResponseBody(message, outputContexts, followUpEvent)


def getAccount_fundsTransfer(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = validate.try_ex(lambda: requestBody['queryResult']['parameters'])
    account = validate.try_ex(lambda: parameters['account'])
    error = event = recipient = message = followUpEvent = None

    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getaccount_fundstransfercontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            error = validate.try_ex(lambda: context['parameters']['error'])
            recipient = validate.try_ex(lambda: context['parameters']['recipient'])
    parameters['event'] = event
    parameters['recipient'] = recipient

    if account is not None and account != "":
        if validate.isvalidAccount(account):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session + "/contexts/" + eventsData[event]['nextContext']
        else:
            parameters['error'] = True
            contextName = session + "/contexts/getaccount_fundstransfercontext"
    else: #Unfilled
        contextName = session+"/contexts/getaccount_fundstransfercontext"
        if(error == True):
            message = eventsData[event]['languages'][languageCode][0]
        else:
            message = eventsData[event]['languages'][languageCode][1]

    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    return helpers.createResponseBody(message, outputContexts, followUpEvent)

def getRecipient_fundsTransfer(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    recipient = validate.try_ex(lambda: requestBody['queryResult']['parameters']['recipient'])
    error = event = message = followUpEvent = None

    # Read from the getrecipient_fundstransfercontext that has been passed in as part of the input http request
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getrecipient_fundstransfercontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            error = validate.try_ex(lambda: context['parameters']['error'])
    parameters = {'recipient' : recipient, 'event' : event}
    
    if recipient is not None and recipient != "":
        if validate.isvalidRecipient(recipient):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session+"/contexts/"+eventsData[event]['nextContext']
        else:
            parameters['error'] = True #Error message will be shown when getRecipient_fundsTransfer() is called immediately again
            contextName = session+"/contexts/getrecipient_fundstransfercontext"
    else: #Unfilled
        contextName = session+"/contexts/getrecipient_fundstransfercontext"
        if(error == True): # Flag indicates that user has previously supplied an invalid recipient. Show error message
            message = eventsData[event]['languages'][languageCode][0]
        else:
            message = eventsData[event]['languages'][languageCode][1]

    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    return helpers.createResponseBody(message, outputContexts, followUpEvent)

