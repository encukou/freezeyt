from pathlib import Path
from wsgi_static_middleware import StaticMiddleware

from demo_project.wsgi import application as django_wsgi_app

BASE_PATH = Path(__file__).parent
STATIC_DIRS = [BASE_PATH / 'static']


app = StaticMiddleware(
    django_wsgi_app, static_root='/static', static_dirs=STATIC_DIRS
)

freeze_config = {'extra_pages': ['/extra/']}