from celery import task
import time

from celery.task import periodic_task
from qs import celery_app


@celery_app.task
def sendmail(email):
    print('start send email to %s' % email)
    time.sleep(5)  # 休息5秒
    print('success')
    return True


@periodic_task(run_every=10)
def some_task():
    print('periodic task test!!!!!')
    time.sleep(5)
    print('success')
    return True
