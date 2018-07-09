import json
import datetime
import time
import helpers
import fundsTransfer
import billPayment
import validate



# --- Functions that deal with individual secondary intents (i.e. for elciting and validating slots, asking for confirmation) ---
# --- Nomenclature: secondaryIntentName_mainIntentName e.g. getAccount_fundsTransfer is the function that deals with the get Account intent
# for the funds transfer goal ---
def confirm_billPayment(requestBody, eventsData):
    session = try_ex(lambda: requestBody['session'])
    languageCode = try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = try_ex(lambda: requestBody['queryResult']['parameters'])
    confirm = try_ex(lambda: requestBody['queryResult']['parameters']['confirm'])
    message = event = account = amount = biller = None
    
    outputContexts = try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/confirm_billpaymentcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = try_ex(lambda: context['parameters']['event'])
            account = try_ex(lambda: context['parameters']['account'])
            amount = try_ex(lambda: context['parameters']['amount'])
            biller = try_ex(lambda: context['parameters']['biller'])
            if confirm is None:
                confirm = try_ex(lambda: context['parameters']['confirm'])

    parameters['event'] = event
    parameters['confirm'] = confirm
    parameters['account'] = account
    parameters['amount'] = amount
    parameters['biller'] = biller

    if confirm is not None and confirm != "":
        if confirm == 'yes':
            remainingBalance = deductAccountBalance(hardcodedAccountBalance, account, amount) #Would require backend API call in actual code
            message = eventsData[event]['languages'][languageCode][0].format(amount['amount'], biller, account, remainingBalance)
            return createResponseBody(message, None, None)
        else:#Either user has said no, or possibly some error in their response. TODO: Split up messages for both cases
            message = eventsData[event]['languages'][languageCode][1]
            return createResponseBody(message, None, None)
    else:#Ask for confirmation again
        parameters['event'] = 'BILL_PAYMENT_CONFIRM_TRANSFER'
        followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
        contextName = session+"/contexts/confirm_billpaymentcontext"
        outputContexts = [
                {
                    "name": contextName,
                    "lifespanCount": 1,
                    "parameters": parameters
                }]
        message = eventsData[event]['languages'][languageCode][2].format(amount['amount'], biller, account)
        return createResponseBody(message, outputContexts, followUpEvent)

def getAmount_billPayment(requestBody, eventsData):
    session = try_ex(lambda: requestBody['session'])
    languageCode = try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = try_ex(lambda: requestBody['queryResult']['parameters'])
    amount = try_ex(lambda: parameters['amount'])
    event = error = account = biller = message = followUpEvent = None
     
    outputContexts = try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getamount_billpaymentcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = try_ex(lambda: context['parameters']['event'])
            error = try_ex(lambda: context['parameters']['error'])
            biller = try_ex(lambda: context['parameters']['biller'])
            account = try_ex(lambda: context['parameters']['account'])
    parameters['event'] = event
    parameters['biller'] = biller
    parameters['account'] = account
    
    if amount is not None and amount != "" and account is not None and account != "":
        if isvalidAmount(hardcodedAccountBalance, amount, account):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session+"/contexts/" + eventsData[event]['nextContext']
        else:
            parameters['error'] = True
            contextName = session + "/contexts/getamount_billpaymentcontext"
    else: #Unfilled
        contextName = session + "/contexts/getamount_billpaymentcontext"
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
    return createResponseBody(message, outputContexts, followUpEvent)


def getAccount_billPayment(requestBody, eventsData):
    session = try_ex(lambda: requestBody['session'])
    languageCode = try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = try_ex(lambda: requestBody['queryResult']['parameters'])
    account = try_ex(lambda: parameters['account'])
    error = event = biller = message = followUpEvent = None
    
    outputContexts = try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getaccount_billpaymentcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = try_ex(lambda: context['parameters']['event'])
            error = try_ex(lambda: context['parameters']['error'])
            biller = try_ex(lambda: context['parameters']['biller'])
    parameters['event'] = event
    parameters['biller'] = biller

    if account is not None and account != "":
        if isvalidAccount(account):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session + "/contexts/" + eventsData[event]['nextContext']
        else:
            parameters['error'] = True
            contextName = session + "/contexts/getaccount_billpaymentcontext"
    else: #Unfilled
        contextName = session+"/contexts/getaccount_billpaymentcontext"
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
    return createResponseBody(message, outputContexts, followUpEvent)


def getBiller_billPayment(requestBody, eventsData):
    session = try_ex(lambda: requestBody['session'])
    languageCode = try_ex(lambda: requestBody['queryResult']['languageCode'])
    biller = try_ex(lambda: requestBody['queryResult']['parameters']['biller'])
    error = event = message = followUpEvent = None
    
    outputContexts = try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getbiller_billpaymentcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = try_ex(lambda: context['parameters']['event'])
            error = try_ex(lambda: context['parameters']['error'])
    parameters = {'biller' : biller, 'event' : event}
    
    if biller is not None and biller != "":
        if isvalidBiller(biller):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session+"/contexts/"+eventsData[event]['nextContext']
        else:
            parameters['error'] = True
            contextName = session+"/contexts/getbiller_billpaymentcontext"
    else: #Unfilled
        contextName = session+"/contexts/getbiller_billpaymentcontext"
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
    return createResponseBody(message, outputContexts, followUpEvent)
    
# --- Entry Points for the 3 possible goals of the user - get balance, pay bills or transfer funds ---        

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
        
def payBill(requestBody, eventsData):
    session = try_ex(lambda: requestBody['session'])
    languageCode = try_ex(lambda: requestBody['queryResult']['languageCode'])
    account = try_ex(lambda: requestBody['queryResult']['parameters']['account'])
    amount = try_ex(lambda: requestBody['queryResult']['parameters']['amount'])
    biller = try_ex(lambda: requestBody['queryResult']['parameters']['biller'])

    parameters = {'account' : account, 'amount' : amount, 'biller' : biller}
    
    outputContexts = message = followUpEvent = None
    
    # Checks the validity of each slot sequentially, calling the appropriate event if any slot is invalid/incomplete, or if all slots have been filled
    if biller is not None and biller != "" and isvalidBiller(biller):
        if account is not None and account != "" and isvalidAccount(account):
            if amount is not None and amount != "" and isvalidAmount(hardcodedAccountBalance, amount, account):
                parameters['event'] = 'BILL_PAYMENT_CONFIRM_TRANSFER'
                contextName = session+"/contexts/confirm_billpaymentcontext"
            else:
                parameters['event'] = 'BILL_PAYMENT_GET_AMOUNT'
                contextName = session+"/contexts/getamount_billpaymentcontext"
        else:
            parameters['event'] = 'BILL_PAYMENT_GET_ACCOUNT'
            contextName = session+"/contexts/getaccount_billpaymentcontext"
    else: #default next intent if no parameters are provided
        parameters['event'] = 'BILL_PAYMENT_GET_BILLER'
        contextName = session+"/contexts/getbiller_billpaymentcontext"

    outputContexts = [
        {
            "name": contextName,
            "lifespanCount": 1,
            "parameters": parameters
        }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    return createResponseBody(message, outputContexts, followUpEvent)
    
# --- Calls respective intent ---

def dispatch(requestBody, eventsData):
    helpers.init()
    funcDict = {'billPayment' : payBill,
                'getBiller_billPayment' : getBiller_billPayment,
                'getAccount_billPayment' : getAccount_billPayment,
                'getAccount_fundsTransfer' : fundsTransfer.getAccount_fundsTransfer,
                'getAmount_billPayment' : getAmount_billPayment,
                'getAmount_fundsTransfer' : fundsTransfer.getAmount_fundsTransfer,
                'confirm_fundsTransfer' : fundsTransfer.confirm_fundsTransfer,
                'confirm_billPayment' : confirm_billPayment,
                'fundsTransfer' : fundsTransfer.transferFunds,
                'getRecipient_fundsTransfer' : fundsTransfer.getRecipient_fundsTransfer,
                'getBalance' : getBalance}
    if requestBody is None:
        return None
    requestBody = json.loads(requestBody)
    intent = try_ex(lambda: requestBody['queryResult']['intent']['displayName'])
    result = (try_ex(lambda: funcDict[intent](requestBody, eventsData)))
    if result is None:
        raise Exception('Intent with name ' + intent + ' not supported')
    return result
