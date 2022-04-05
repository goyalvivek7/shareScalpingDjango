from django.db import models

class User(models.Model):
    user_id = models.CharField(max_length=200)
    consumer_key = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    accessCode = models.TextField()

class ScalpingOrder(models.Model):
    userid = models.CharField(max_length=200 , default='00000000000')
    currentdate = models.CharField(max_length=200 , default='0000000')
    instrumentToken = models.CharField(max_length=200)
    orderType = models.CharField(max_length=200)
    lotQuantity = models.CharField(max_length=200)
    steps = models.CharField(max_length=200)
    entryDiff = models.CharField(max_length=200)
    exitDiff = models.CharField(max_length=200)
    startPrice = models.CharField(max_length=200)
    status = models.CharField(max_length=200 , default='active')

class OrderHistory(models.Model):
    scalpingOrderid = models.CharField(max_length=200)
    instrument_token = models.CharField(max_length=200)
    equivalentOrderPrice =  models.CharField(max_length=200)
    order_type = models.CharField(max_length=200)
    quantity  = models.CharField(max_length=200)
    order_id = models.CharField(max_length=200)
    order_status = models.CharField(max_length=200)
    initialOrderType = models.CharField(max_length=200)
    startPrice = models.CharField(max_length=200)


