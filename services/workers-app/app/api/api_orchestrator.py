from app.worker_pool.wo_selenium import SeleniumTaskHandler, SeleniumWorkerSession
from app.core.core_orchestrator import RequestWorkers, WorkerAvailability
from flask import Flask, jsonify, abort, request, make_response, url_for

from app.config import config
from app import network_health
import requests as r
import logging

from flask_restplus import Namespace, Resource, fields, reqparse
from flask import current_app as app

'''
Orchestrator of the worker pool

expected input: message with info for allocating resources
Hey, what can i use? and if free: request the stuffs
output: free? yes/no, response from worker
'''

api = Namespace('orchestrator', description='i orchestrate stuff')

#parser.add_argument('name', type=int, location='form')

config = api.model('Config', {
    'id': fields.Integer,
    'country': fields.String,
    'company_name': fields.String,
    'event': fields.String,
    'link': fields.String,
    'config': fields.Nested,
})


@api.route('/')
class OrchestratorAPI(Resource):
    @api.expect(model=config)
    #@api.doc(model=config)
    def post(self):
        message = request.get_json(force=True)
        if message != None:
            response = RequestWorkers().request_workers(message)
        return jsonify({'response': response['response_orchestrator']})


#### Standaline availability check
@api.route('/availability/<string:worker>')
class WorkerAvailabilityAPI(Resource):
    def get(self, *args, **kwargs):
        return WorkerAvailability().availability()


#### Standalone call?
@api.route('/network/selenium')
class SeleniumWorker(Resource):

    def get(self):
        return network_health.check_hub()

    def post(self):
        response = SeleniumTaskHandler(message)
        return response
