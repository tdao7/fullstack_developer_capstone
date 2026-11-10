"""Lightweight educational sentiment microservice at :5050; no Flask download needed."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import unquote,urlsplit
import json
from djangoapp.data import analyze_text
class SentimentHandler(BaseHTTPRequestHandler):
 def do_GET(self):
  path=urlsplit(self.path).path
  if not path.startswith('/analyze/'):
   self.send_response(404);self.end_headers();return
  result=json.dumps({'sentiment':analyze_text(unquote(path.split('/analyze/',1)[1]))}).encode()
  self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(result)));self.end_headers();self.wfile.write(result)
if __name__=='__main__':
 print('Sentiment demo running on http://127.0.0.1:5050',flush=True)
 HTTPServer(('127.0.0.1',5050),SentimentHandler).serve_forever()
