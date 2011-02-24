from bzrlib.transport.http import wsgi

def application(environ, start_response):
    app = wsgi.make_app(
        root="/var/opt/kanon/bzr",
        prefix="/bzr",
        readonly=False,
        load_plugins=True,
        enable_logging=False)
    return app(environ, start_response)