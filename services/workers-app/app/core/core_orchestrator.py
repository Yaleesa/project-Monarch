from app.config import config
from app import network_health
from app.core.core_recipe_builder import RecipeBuilder
from app.worker_pool.wo_selenium import SeleniumTaskHandler, SeleniumWorkerSession
from app.worker_pool.wo_scrapy.spider import ScrapyRunner
from app.worker_pool.wo_API_requests import APIRequester

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import current_app as app

import requests as r

class WorkerAvailability:
    def __init__(self, *args, **kwargs):
        self.available_workers = ['selenium', 'scrapy', 'requests']
        self.availability_list = self.availability()
    # Global availability checker
    def availability(self):
        availability_list = dict()

        def message(worker):
            if worker == 'selenium':
                return network_health.check_hub()
            if worker == 'scrapy':
                return {'message': 'Is it me you looking for?', 'ready': True}
            if worker == 'requests':
                return {'message': 'Zei u nou aaaapi?', 'ready': True}
            else:
                return {'message': 'This is not a valid worker', 'ready': False}

        availability_list['workers'] = {worker: message(worker) for worker in self.available_workers}
        return availability_list

class RequestWorkers:
    def __init__(self):
        self.availability_list = WorkerAvailability().availability()
    ''' incomming messages: first call recipebuilder
        Checks availabilty & Assign requests to workers'''
    def request_workers(self, message):
        try:
            for worker in message['event']['workers']:
                app.logger.info('Requested: ' + worker)
                if self.availability_list['workers'][worker]['ready']:
                    app.logger.info(f'{worker} is ready!')
                    response = self.assign_requests(worker, message)
                    app.logger.info("assigned to gatekeeper")
                    response = response['response_gatekeeper']
                else:
                    response = {'status': False, 'message': self.availability_list['workers'][worker]}
                    app.logger.info(response)
        except Exception as err:
            response = str(err)
            app.logger.error(err, exc_info=True)
        return {'response_orchestrator': response}


    def assign_requests(self, worker, message):
        if worker == 'selenium':
            gatekeeper = SeleniumGateKeeper()
            response = gatekeeper.run(message)
            return {"response_gatekeeper": response}

        if worker == 'scrapy':
            gatekeeper = ScrapyGateKeeper()
            response = gatekeeper.run(message)
            return {"response_gatekeeper": response}

        if worker == 'requests':
            gatekeeper = RequestsGateKeeper()
            response = gatekeeper.run(message)
            return {"response_gatekeeper": response}

### Oke ja beetje overdreven dit lol
class SeleniumGateKeeper:
    def run(self, message):
        try:
            if message['event']['name'] == 'config_tester':
                recipe = RecipeBuilder(event=message['event']).config_to_recipe_links(message)
            else:
                recipe = RecipeBuilder(event=message['event']).config_to_recipe(message)
        except Exception as err:
            app.logger.error(err, exc_info=True)
            #recipe = message
        response = SeleniumTaskHandler(recipe)
        return response['response_selenium']

class ScrapyGateKeeper:
    def run(self, message):
        response = ScrapyRunner().go(message)
        return response['response_scrapy']

class RequestsGateKeeper:
    def run(self, message):
        response = APIRequester().request(message)
        return response['response_requests']
