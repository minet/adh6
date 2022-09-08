from adh6.server import init

# When run with uWSGI (production).
if __name__ == 'uwsgi_file_main':
    application = init()

# When run with `python main.py`, when people want to run it locally.
if __name__ == '__main__':
    application = init()
    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application.run(port=8080)
