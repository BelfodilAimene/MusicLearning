#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import comparator
import struct

import cgi
import logging

from google.appengine.api import files
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext import db

COMPARE_WITH='REF0.wav'



MAIN_PAGE_HTML2 = """\
<html>
  <head>
  <title> Music Learning </title>
  <script type="text/javascript" src="/js/swfobject.js"></script>
  <script type="text/javascript" src="/js/recorder.js"></script>
  <script type="text/javascript" src="/js/gui.js"></script>
  <script type="text/javascript" src="/bootstrap/js/bootstrap.js"></script>
  <link type="text/css" rel="stylesheet" href="/bootstrap/css/bootstrap.css" />
  <link type="text/css" rel="stylesheet" href="/bootstrap/css/bootstrap.min.css" />
  <link type="text/css" rel="stylesheet" href="/bootstrap/css/starter-template.css" />
  <script>
	function setupRecorder() {
		Wami.setup({
			id : "wami"
		});
	}
  </script>
  </head>
  <body onload="setupRecorder()">

    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">Music Learning</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="#">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </nav>

    <div class="container">

      <div class="starter-template">

        <div >
        <h2>Son de reference</h2>
          <audio id="audio1" src='"""+COMPARE_WITH+"""' controls preload="auto" autobuffer> </audio>
        </div>
        <div> <h3> Enregistrement </h3></div>
        <div>
          <button onclick="Wami.startRecording('son')">Lancer Enregistrement</button>
          <button onclick="Wami.stopRecording()">Arreter Enregistrement</button>
        </div>

        <div> <h3> Validation </h3></div>
        <div>
          <form action="/valider" method="post">
            <div><input type="submit" class="btn btn-large" value="valider"></div>
          </form>
        </div>
        
      </div>

    </div><!-- /.container -->
  </body>
</html>
"""


MAIN_PAGE_HTML = """\
<html>
  <head>
  <script type="text/javascript" src="/js/swfobject.js"></script>
  <script type="text/javascript" src="/js/recorder.js"></script>
  <script type="text/javascript" src="/js/gui.js"></script>
  <script type="text/javascript" src="/bootstrap/js/bootstrap.js"></script>
  <link type="text/css" rel="stylesheet" href="/bootstrap/css/bootstrap.css" />
  <script>
	function setupRecorder() {
		Wami.setup({
			id : "wami"
		});
	}
  </script>
  </head>
  <body onload="setupRecorder()">
  <div id="wami" style="margin-left: 100px;"></div>
  <div>
  <noscript>WAMI requires Javascript</noscript>
  </div>
  <!-- <div>
    <h> Son de reference</h>
    <div>
    <audio id="audio1" src='"""+COMPARE_WITH+"""' controls preload="auto" autobuffer> </audio>
    </div>
  </div> -->
    <button onclick="Wami.startRecording('son')">Start Recording</button>
  </div>
  <div>
    <button onclick="Wami.stopRecording()">Stop Recording</button>
  </div>
  <div>
    <form action="/valider" method="post">
      <div><input type="submit" value="valider"></div>
    </form>
  </div>
  </body>
</html>
"""

class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write(MAIN_PAGE_HTML)

class Calculator(webapp2.RequestHandler):
  def post(self):
    model = DataModel.get_by_key_name(self.get_name())
    blob_info = blobstore.BlobInfo.get(model.blob.key())
    blob_reader = blobstore.BlobReader(model.blob.key())
    data = blob_reader.read()

    
    L1=comparator.getSignalfromWav(COMPARE_WITH)
    L2=comparator.getSignalfromData(data)
    
    self.response.out.write("<div>")
    self.response.out.write(comparator.covariance(L1,L2))
    self.response.out.write("</div>")
    
    
  def get_name(self):
    name = "output.wav"
    params = cgi.parse_qs(self.request.query_string)
    if params and params['name']:
      name = params['name'][0];
    return name
    
    

# A simple database model to store a URL and an associated blob.
class DataModel(db.Model):
  url = db.StringProperty(required=True)
  blob = blobstore.BlobReferenceProperty(required=True)

# WamiHandler receives audio via a POST and serves it back to the
# client using a GET.  The audio data is stored in a blobstore, but
# additional meta information is (connecting a URL to a blob) is
# stored in the datastore.  You will need to enable the datastore
# admin section for your Google App Engine.
class WamiHandler(webapp.RequestHandler):
  def get(self): 
    model = DataModel.get_by_key_name(self.get_name())
    blob_info = blobstore.BlobInfo.get(model.blob.key())
    blob_reader = blobstore.BlobReader(model.blob.key())
    data = blob_reader.read()
    #self.response.headers['Content-Type'] = blob_info.content_type
    #self.response.out.write(data)
    logging.info("server-to-client: " + str(len(data)) +
                 " bytes at key " + str(model.blob.key()))
  def post(self):
    type = self.request.headers['Content-Type']
    blob_file_name = files.blobstore.create(mime_type=type)
    with files.open(blob_file_name, 'a') as f:
      f.write(self.request.body)
    f.close()
    files.finalize(blob_file_name)

    blob_key = files.blobstore.get_blob_key(blob_file_name)
    model = DataModel(key_name=self.get_name(),
                      url=self.request.url, blob=blob_key)
    db.put(model)
    logging.info("client-to-server: type(" + type +
                 ") key("  + str(blob_key) + ")")

  def get_name(self):
    name = "output.wav"
    params = cgi.parse_qs(self.request.query_string)
    if params and params['name']:
      name = params['name'][0];
    return name
    
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/valider', Calculator),
  ('/son', WamiHandler)
], debug=True)
