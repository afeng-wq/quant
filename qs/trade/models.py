from datetime import timezone, datetime

from django.db import models

class StockList(models.Model):
    index = models.IntegerField(primary_key=True)
    ts_code = models.CharField(max_length=9)
    symbol = models.CharField(max_length=6)
    name = models.CharField(max_length=45)
    area = models.CharField(max_length=45)
    industry = models.CharField(max_length=45)
    list_date = models.CharField(max_length=45)

    def __str__(self):
        print('__str__(self)')
        return '-'.join([self.ts_code, self.name])

    def __repr__(self):
        print('__repr__(self)')
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