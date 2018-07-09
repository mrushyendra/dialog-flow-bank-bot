# --- Hardcoded bank balance for user ---

def __init__:
    hardcodedAccountBalance = {'current' : 100, 'savings' : 10000}

# --- Helper function for making HTTP requests ---

def createResponseBody(message, outputContexts=None, followUpEvent=None):
    return {'fulfillmentText' : message,
            'outputContexts' : outputContexts,
            'followupEventInput' : followUpEvent}

# --- Backend logic helper functions ---

def deductAccountBalance(userAccountBalance, accountType, amount):
    """
    Updates actual account balance. Note: In final version this would require a backend call to deduct and transfer money. 
    """
    amountNum = try_ex(lambda: amount['amount'])
    if amountNum is not None:
        if userAccountBalance[accountType] >= amountNum:
            userAccountBalance[accountType]-=amountNum
            return userAccountBalance[accountType]
    else:
        raise Exception('Balance not sufficient for transfer')
