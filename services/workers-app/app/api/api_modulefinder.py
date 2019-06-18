##
from flask_restplus import Namespace, Resource, fields

import sys
import pkgutil

api = Namespace('modules', description='All the modules in the project')

### DIT WORD ANDERS, ONDERSTAANDE HEEFT NUL ZIN
@api.route('/')
class Modules(Resource):
    def get(self):
        search_path = None # set to None to see all modules importable from sys.path
        all_modules = [x[1] for x in pkgutil.iter_modules(path=search_path)]
        return all_modules
