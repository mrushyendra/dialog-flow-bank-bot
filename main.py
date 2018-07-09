import webapp2
import json
import generateDialogFlowResponse
import eventsData

class generateResponse(webapp2.RequestHandler):
    def post(self):
        responseBody = generateDialogFlowResponse.dispatch(self.request.body, eventsData.data)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(responseBody)) 
    def get(self):
        self.response.write('test string')

app = webapp2.WSGIApplication([
    (r'/', generateResponse),
    ], debug=True)
