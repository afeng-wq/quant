from django.http import HttpResponse
from utils.tushare_util import TushareUtil
import json
from .models import StockList, Question
from .tasks import sendmail


def index(request):
    util = TushareUtil.instance()
    data = util.get_stock_list()
    stock = StockList.objects.get(index=1)
    print(stock)
    data = util.get_stock_info(ts_code='000001.SZ',start_date='20201124',end_date='20201124')
    return HttpResponse(stock)


def detail(request):
    sendmail.delay('test@test.com')
    data = list(Question.objects.values('question_text'))
    return HttpResponse(json.dumps(data), content_type='application/json')


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)