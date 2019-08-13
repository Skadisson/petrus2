from werkzeug.wrappers import Request, Response
from bin.service import Environment
from bin.module import Estimate
from bin.module import Search
from bin.module import Trend
from bin.module import Update
from bin.module import Backup
import os
import json


@Request.application
def petrus(request):
    function = request.args.get('function', None)
    items = []
    success = False
    if function == 'Estimate':
        jira_key = request.args.get('jira_key', None)
        if jira_key is not None:
            estimator = Estimate.Estimate(jira_key)
            items, success = estimator.run()
    elif function == 'Search':
        keywords = request.args.get('keywords', None)
        if keywords is not None:
            search = Search.Search(keywords)
            items, success = search.run()
    elif function == 'Trend':
        months = request.args.get('months', None)
        if months is not None:
            trend = Trend.Trend(months)
            items, success = trend.run()
    elif function == 'Update':
        update = Update.Update()
        items, success = update.run()
    elif function == 'Backup':
        backup = Backup.Backup()
        items, success = backup.run()
    response = {'success': success, 'items': items}
    json_response = json.dumps(response)
    return Response(json_response, mimetype='application/json')


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    env = Environment.Environment()
    port = env.get_service_port()
    host = env.get_service_host()
    run_simple(hostname=host, port=port, application=petrus)
