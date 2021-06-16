from pathlib import Path

from flask import Flask

APP_DIR = Path(__file__).parent

app = Flask(__name__)
freeze_config = {'extra_files':
                    {'bin_range.dat':
                        {'wrong-map-key': 'AAECAwQFBgcICQ=='}
                    }
                }
