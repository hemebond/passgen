# HTTP server and templating
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template

# mincss
from os.path import abspath, dirname, join, normpath
from mincss.processor import Processor, ParserError
import lxml.html
from lxml import etree
from lxml.cssselect import CSSSelector

# Minification and compression
from rcssmin import cssmin
from slimit import minify
import base64
import re

PROJECT_ROOT = dirname(abspath(__file__))

stylesheets = [
	"static/css/bootstrap.css"
]

scripts = [
	"static/js/jquery.js",
	"static/js/bootstrap.js",
	"static/js/sha1.js",
	"static/js/app.js"
]

images = {
	"icon": "static/img/padlock.png"
}


def process_html(html):
	mini_html = html
	mini_html = re.sub(r'(\r\n|\n|\r|\t)', '', mini_html, flags=re.M)
	mini_html = re.sub(r'\s+', ' ', mini_html, flags=re.M)

	return mini_html


def process_css(html, stylesheets):
	p = Processor()
	parser = etree.HTMLParser()
	tree = etree.fromstring(html, parser).getroottree()
	page = tree.getroot()

	if page is None:
		print repr(html)
		raise ParserError("Could not parse the HTML")

	body, = CSSSelector('body')(page)

	processed_css = ''

	for sheet in stylesheets:
		sheet_path = normpath(join(PROJECT_ROOT, sheet))

		with open(sheet_path, 'r') as sheet_file:
			content = unicode(sheet_file.read(), 'utf-8')
			processed_css += p._process_content(content, [body, ])

	return cssmin(processed_css)


def process_js(scripts):
	aggregated_scripts = ''

	for script in scripts:
		script_path = normpath(join(PROJECT_ROOT, script))
		with open(script_path, 'r') as script_file:
			aggregated_scripts += unicode(script_file.read(), 'utf-8')

	return minify(aggregated_scripts, mangle=True, mangle_toplevel=True)


def process_images(images):
	processed_images = {}

	for key, image in images.items():
		with open(images[key], "rb") as image_file:
			encoded_string = base64.b64encode(image_file.read())
			processed_images[key] = "data:image/png;base64," + encoded_string

	return processed_images


class MyRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		template_path = normpath(join(PROJECT_ROOT, 'templates/password.html'))

		if self.path in ["/", "/compress"]:
			with open(template_path) as tpl:
				template = Template(tpl.read())

			if self.path == "/":
				html = template.render(
					stylesheets=stylesheets,
					scripts=scripts,
					images=images
				)

			if self.path.startswith("/compress"):
				raw_html = template.render(images={})

				html = template.render(
					inline_style=process_css(raw_html, stylesheets),
					inline_script=process_js(scripts),
					images=process_images(images),
				)

				html = process_html(html)

			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(html)

			return

		if self.path.startswith("/static"):
			local_path = normpath(join(PROJECT_ROOT, self.path[1:]))

			with open(local_path) as static_file:
				html = static_file.read()

			self.wfile.write(html)
			return

		self.send_error(404, "File Not Found %s" % self.path)


if __name__ == "__main__":
	try:
		server = HTTPServer(("0.0.0.0", 9000), MyRequestHandler)
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()
