import time, json, csv, random
from flask_restplus import Namespace, Resource, fields
from app.core.core_recipe_builder import RecipeBuilder
from flask import Flask, jsonify, abort, request, make_response, url_for


api = Namespace('recipebuilder', description='To build a recipe the workers understand')


'''
recipe_template = {
    'source': __file__,
    'id': random.randint(0,10),
    'event': {'method': 'requesting_workers', 'workers':['selenium'], 'module': 'vacancy' ### can be different
        'recipes': [{group_id: 'group', 'order': 1, ingredients:[
            {'name': 'identifier', 'method': 'name_of_method', type: 'text', 'input': 'data needed for method'},
        ]}]

}
'''

tests = {'id': 1, 'event': 'unit', 'recipes':[{'groud_id': 3, 'order': 1, 'ingredients': [{'method': 'unit', 'type': 'unit', 'input': 'unit'}] }]}

ingredients = api.model('Ingredients', {
    'name': fields.String,
    'method': fields.String,
    'type': fields.String,
    'input': fields.String,
})

recipes = api.model('Recipes', {
    'group_id': fields.String,
    'order': fields.Integer,
    'ingredients': fields.List(fields.Nested(ingredients)),
})

message = api.model('Message', {
    'id': fields.Integer,
    'event': fields.String, #what kind of task do you want
    'recipes': fields.List(fields.Nested(recipes)),
})






@api.route('/')
class recipeTemplate(Resource):
    @api.marshal_with(message)
    def post(self):
        message = request.get_json(force=True)
        recipe = RecipeBuilder(event=message['event'], module=message['module']).config_to_recipe_links(message)
        print(recipe)
        response = json.dumps(recipe)
        print(response)
        return response





#################
