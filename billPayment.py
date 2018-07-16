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
    

