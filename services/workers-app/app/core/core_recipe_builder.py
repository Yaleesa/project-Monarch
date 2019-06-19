import time, json, csv, random
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import current_app as app

class RecipeBuilder:
    def __init__(self, event):
        self.id = random.randint(0,100)
        self.event = event
        self.template = {'id': self.id, 'event': self.event, 'recipes': []}

    def add_recipe_group(self, group_id):
        return {'group_id': group_id, 'ingredients': []}

    def add_ingredient(self, *args, **kwargs):
        return kwargs

    ########## temp cuz ugly hardcoded
    def config_to_recipe_links(self, config):
        self.event.update({'name': config['name']})
        self.template['recipes'].append(self.add_recipe_group('vacancy_pages'))

        for recipe in self.template['recipes']:
            if recipe['group_id'] == 'vacancy_pages':
                recipe['ingredients'].append(self.add_ingredient(method='url', type='start', fieldname='start_url', input=config['config']['start_url']))
                recipe['ingredients'].append(self.add_ingredient(method='xpath', type='urls', fieldname='vacancy_xc_path', input=config['config']['vacancy_xc_path']))
                if 'next_page_xc_path' in config['config']:
                    recipe['ingredients'].append(self.add_ingredient(method='xpath', type='click', fieldname='next_page_xc_path', input=config['config']['next_page_xc_path']))
                else:
                    recipe['ingredients'].append(self.add_ingredient(method='xpath', type='click', fieldname='next_page_xc_path', input=None))


        return self.template

    def config_to_recipe_content(self, root,combined):
        self.event.update({'name': combined['name']})
        self.event['recipes'].append(self.add_ingredient('url', 'start', 'root', root))
        # for key, value in combined.items():
        #     if key == 'start_url':
        #         continue
        #     elif key == 'vacancy_xc_path':
        #         continue
        #     elif key == 'next_page_xc_path':
        #         continue
        #     else:
        self.event['recipes'].append(self.add_ingredient('xpath', 'text', 'title', combined['config']['title']))
        self.event['recipes'].append(self.add_ingredient('source', 'source', 'source', 'source'))
        return self.template

    def config_to_recipe(self, config):
        app.logger.info(config['config'])
        for action in config['config']:
            app.logger.info(action)

            self.template['recipes'].append(self.add_ingredient(method=action['method'], type=action['type'], fieldname=action['fieldname'], input=action['input']))
        return self.template
