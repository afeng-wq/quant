from datetime import timezone, datetime

from django.db import models


class StockList(models.Model):
    index = models.IntegerField()
    ts_code = models.CharField(max_length=9)
    symbol = models.CharField(primary_key=True,max_length=6)
    name = models.CharField(max_length=45)
    area = models.CharField(max_length=45)
    industry = models.CharField(max_length=45)
    list_date = models.CharField(max_length=45)

    def __str__(self):
        return '-'.join([self.ts_code, self.name])

    def __repr__(self):
        return '-'.join([self.ts_code, self.name])

    class Meta:
        db_table = 'stock_list'


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

'''
| index|trade_date|ts_code   |open   |high   |low    |close  |pre_close|change              |pct_chg  | vol       | amount      | turnover_rate | volume_ratio |ma5     | ma_v_5     | ma10    | ma_v_10    |ma20     | ma_v_20    | ma72    | ma_v_72    | ma120   | ma_v_120| 
|     0| 20201126 |000002.SZ | 30.78 | 31.07 | 30.12 | 30.94 | 30.8    |0.14000000000000057 |  0.4545 | 584039.77 | 1788275.571 |        0.6012 |         NULL | 19.574 | 60601.912 | 19.529    | 53780.287 | 19.4825 | 50590.3995 | 21.2065 | 75992.6447 | 22.1088 | 110739.7629 |
'''
class Stock(models.Model):
    index = models.IntegerField()
    trade_date = models.CharField(primary_key=True)
    ts_code = models.CharField(max_length=9)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    pre_close = models.FloatField()
    change = models.FloatField()
    pct_chg = models.FloatField()
    vol = models.FloatField()
    amount = models.FloatField()
    turnover_rate = models.FloatField()
    volume_ratio = models.FloatField()

    class Meta:
        ordering = ['trade_date']