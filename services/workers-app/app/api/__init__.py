from flask_restplus import Api

api = Api(
    title='The Colony API',
    version='1.0',
    description='Various types of workers are ready for you to use',
    # All API metadatas
)


from .api_modulefinder import api as modulefinder
from .api_orchestrator import api as orchestrator
from .api_recipe_builder import api as recipeBuilder
from app.worker_pool.wo_selenium import worker as selenium
from app.worker_pool.wo_scrapy.spider import worker as spider

prefix = '/api/v1'
api.add_namespace(modulefinder, path=prefix+'/modules')
api.add_namespace(recipeBuilder, path=prefix+'/recipebuilder')


api.add_namespace(orchestrator, path=prefix+'/orchestrator')
api.add_namespace(selenium, path=prefix+'/selenium')
api.add_namespace(spider, path=prefix+'/scrapy')
