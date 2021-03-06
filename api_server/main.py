import sys
from common import init

if not hasattr(sys, '_called_from_test'):  # Make sure we never run this when unit testing.

    # When run with uWSGI (production).
    if __name__ == 'uwsgi_file_main':
        application, migrate = init(testing=False)

    # When run with `python main.py`, when people want to run it locally.
    if __name__ == '__main__':
        application, migrate = init(testing=True)
        # set the WSGI application callable to allow using uWSGI:
        # uwsgi --http :8080 -w app
        application.run(port=8080)