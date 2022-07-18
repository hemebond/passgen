# HTTP server and templating
import http.server
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

SERVER_PORT = 9000

STYLESHEETS = [
	"static/css/bootstrap.min.css",
	"static/css/app.css",
]

SCRIPTS = [
	"static/js/sha1.js",
	"static/js/app.js",
]

IMAGES = {
	"icon": "static/img/padlock.png",
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
		print(repr(html))
		raise ParserError("Could not parse the HTML")

	body, = CSSSelector('body')(page)

	processed_css = ''

	for sheet in stylesheets:
		sheet_path = normpath(join(PROJECT_ROOT, sheet))

		with open(sheet_path, 'r') as sheet_file:
			content = sheet_file.read()

		processed_css += p._process_content(content, [body, ])

	return cssmin(processed_css)


def process_js(scripts):
	aggregated_scripts = ''

	for script in scripts:
		script_path = normpath(join(PROJECT_ROOT, script))
		with open(script_path, 'r') as script_file:
			aggregated_scripts += script_file.read()

	return minify(aggregated_scripts, mangle=True, mangle_toplevel=True)


def process_images(images):
	processed_images = {}

	for key, image in images.items():
		with open(images[key], "rb") as image_file:
			image_data = image_file.read()

		encoded_string = base64.standard_b64encode(image_data)
		processed_images[key] = "data:image/png;base64," + encoded_string.decode('utf-8')

	return processed_images


class Handler(http.server.SimpleHTTPRequestHandler):
	extensions_map = {
		'.css': 'text/css',
		'.html': 'text/html',
		'.js': 'text/javascript',
		'.png': 'image/png',
	}


	def get_template(self):
		template_path = normpath(join(PROJECT_ROOT, 'templates/password.html'))

		with open(template_path) as tpl:
			template = Template(tpl.read())

		return template


	def get_html(self):
		template = self.get_template()

		return template.render(
			stylesheets=STYLESHEETS,
			scripts=SCRIPTS,
			images=IMAGES
		)


	def get_compressed(self):
		template = self.get_template()
		raw_html = template.render(images={})

		html = template.render(
			inline_style=process_css(raw_html, STYLESHEETS),
			inline_script=process_js(SCRIPTS),
			images=process_images(IMAGES),
		)

		return process_html(html)


	def do_GET(self):
		if self.path.startswith("/static"):
			return super().do_GET()

		html = None

		if self.path == "/":
			html = self.get_html()

		if self.path.startswith("/compress"):
			html = self.get_compressed()

		if html is not None:
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(bytes(html, 'utf-8'))
			return

		self.send_error(404, "File Not Found %s" % self.path)


if __name__ == "__main__":
	try:
		server = http.server.HTTPServer(("", SERVER_PORT), Handler)  # listen on all interfaces
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()
