Passward Generator
==================

Password generator that uses Jinja and mincss to create a compiled/compressed static html page.

Start the web server with

    python application.py

Then access the web page in the web browser

    http://localhost:9000/

The compressed version of the page can be accessed at

    http://localhost:9000/compress

Requires
-------

* Jinja2
* mincss
* lxml
* slimit
* rcssmin
