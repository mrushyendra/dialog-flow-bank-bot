import json
import helpers
import fundsTransfer
import billPayment
import getBalance
import validate

# --- Calls respective intent ---

def dispatch(requestBody, eventsData):
    helpers.init()
    funcDict = {'billPayment' : billPayment.payBill,
                'getBiller_billPayment' : billPayment.getBiller_billPayment,
                'getAccount_billPayment' : billPayment.getAccount_billPayment,
                'getAccount_fundsTransfer' : fundsTransfer.getAccount_fundsTransfer,
                'getAmount_billPayment' : billPayment.getAmount_billPayment,
                'getAmount_fundsTransfer' : fundsTransfer.getAmount_fundsTransfer,
                'confirm_fundsTransfer' : fundsTransfer.confirm_fundsTransfer,
                'confirm_billPayment' : billPayment.confirm_billPayment,
                'fundsTransfer' : fundsTransfer.transferFunds,
                'getRecipient_fundsTransfer' : fundsTransfer.getRecipient_fundsTransfer,
                'getBalance' : getBalance.getBalance}
    if requestBody is None:
        return None
    requestBody = json.loads(requestBody)
    intent = validate.try_ex(lambda: requestBody['queryResult']['intent']['displayName'])
    result = (validate.try_ex(lambda: funcDict[intent](requestBody, eventsData)))
    if result is None:
        raise Exception('Intent with name ' + intent + ' not supported')
    return result
