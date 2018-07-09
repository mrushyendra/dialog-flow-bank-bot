# --- Generic python helper functions ---

def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function will have a negative impact on performance.
    """
    try:
        return func()
    except KeyError:
        return None


def tryExIndexError(func):
    """
    Call passed in function in try block. If IndexError is encountered return None.
    This function is intended to be used to safely access list.

    Note that this function will have a negative impact on performance.
    """
    try:
        return func()
    except IndexError:
        return None

def isvalidBiller(biller):
    return True


def isvalidAccount(account):
    return True


def isvalidRecipient(recipient):
    return True 
    

def isvalidAmount(userAccountBalance, amount, accountType):
    if type(amount) is dict:
        amountNum = try_ex(lambda: amount['amount'])
        if userAccountBalance[accountType] >= amountNum:
            return True
    return False


def isvalidDate(date):
    return True
    
    
def isvalidTime(time):
    return True;

