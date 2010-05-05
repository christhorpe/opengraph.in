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

import re
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

import BeautifulSoup




def render_template(self, end_point, template_values):
	path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
	response = template.render(path, template_values)
	self.response.out.write(response)


OPENGRAPH = """
<meta property="fb:app_id" content="112907218746859"/>
<meta property="og:title" content="OpenGraph.In : Finding OpenGraph content within links" />
<meta property="og:site_name" content="OpenGraph.In" />
<meta property="og:type" content="website" />
<meta property="og:url" content="http://www.opengraph.in/" />
<meta property="og:description" content="Unlocking the potential of the OpenGraph Protocol to be a universal API. Made by Jaggeree" />
"""



class MainHandler(webapp.RequestHandler):
	def get(self):
		format = self.request.get("format")
		url = False
		requested_url = False
		resource_url = False
		graphitems = False
		errors = False
		if self.request.get("url"):
			try:
				url = True
				requested_url = self.request.get("url")
				if requested_url == "http://www.opengraph.in/":
					resource_url = requested_url
					content = OPENGRAPH
				else:
					if not "http://" in requested_url[0:7]:
						requested_url = "http://" + requested_url
					html = urlfetch.fetch(requested_url)
					content = html.content
					if not html.final_url:
						resource_url = requested_url
					else:
						resource_url = html.final_url
				page = BeautifulSoup.BeautifulSoup(content)
				graphitems = []
				keys = []
				values = []
				for meta in page.findAll('meta', {'property' : re.compile(r'og:[a-z_]+$')}):
					for attr, val in meta.attrs:
						graphitems.append({attr:val})
			except:
				errors = "Something went wrong"
		template_values = {
				"url":url,
				"requested_url": requested_url,
				"resource_url": resource_url,
				"graphitems":graphitems,
				"thisopengraph": OPENGRAPH
		}
		if format == "json":
			render_template(self, "formats/json.tmpl", template_values)
		else:
			render_template(self, "formats/html.tmpl", template_values)




def main():
	application = webapp.WSGIApplication([
	('/', MainHandler)
	], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
