from time import sleep

from celery.result import AsyncResult
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from nluis.celery import app


@app.task(bind=True)
def loop(self, l):
    for i in range(int(l)):
        print(i)
        sleep(2)
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': l})
    print('Task completed')
    return {'current': l, 'total': l}


class TestCeleryView(APIView):

    def get(self, request):
        # task = zakaria.delay(5)
        task = loop.delay(50)
        return Response({
            'task_id': task.id,
            'task_state': task.state,
            'task_ready': task.ready()
        })

    def post(self, request):
        task_id = request.data['task_id']
        task = AsyncResult(task_id)
        if task.state == 'FAILURE' or task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task.state,
                'progression': "None",
                'info': str(task.info)
            }
        else:
            current = task.info.get('current', 0)
            total = task.info.get('total', 1)
            progression = (int(current) / int(total)) * 100  # to display a percentage of progress of the task
            response = {
                'task_id': task_id,
                'state': task.state,
                'progression': progression,
                'info': "None"
            }
        return Response(response, status=200)
