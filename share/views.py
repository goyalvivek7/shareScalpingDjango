from black import out
from django.http import HttpResponse
from django.shortcuts import render
import ks_api_client
from ks_api_client import ks_api
from time import sleep
from django.core import serializers
from django.shortcuts import redirect
from share.models import User
from share.models import OrderHistory
from share.models import ScalpingOrder
from django.contrib import messages
from datetime import datetime
import time
import django_rq
from django_rq import job
from redis import Redis
from rq_scheduler import Scheduler
from django_rq.queues import get_queue
import threading


def index(request):

    context = {"login": "login"}
    return render(request, 'share/login.html', context)
def dashboardView(request):
    print(request.session['user_id'])
    scalpingOrder = ScalpingOrder.objects.all()
    context = {
        "scalpingOrder": scalpingOrder}
    return render(request, 'share/dashboard.html', context)
def addNewScalping(request):
    context = {"dashboard": "dashboard"}
    return render(request, 'share/addNewScalping.html', context)


global client
class orderHistoryModel:
    def __init__(self, instrument_token, equivalentOrderPrice, order_type, quantity, order_id, order_status, initialOrderType, startPrice):
        self.instrument_token = instrument_token
        self.equivalentOrderPrice = equivalentOrderPrice
        self.order_type = order_type
        self.quantity = quantity
        self.order_id = order_id
        self.order_status = order_status
        self.initialOrderType = initialOrderType
        self.startPrice = startPrice


def runScalping(request):
    requestData = request.POST
    scalipingOrder = ScalpingOrder.objects.filter(id=requestData['orderid'])

    if scalipingOrder.count() > 0:
        userId = 'PAR97_56'
        consumerKey = 'Z2wfl8frw78RnUvnO5sNT3C2eEca'
        accessToken = '17f745f8-577e-368f-b76e-c0343fbb43e2'
        accessCode = "7881"
        app_id = "efe683d5-2f91-4649-9bc9-0ae0547d849a"
        client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                                   consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
        client.login(password="march@2022")
        client.session_2fa(access_code=accessCode)
    
        if scalipingOrder[0].orderType == 'Sell':
            # for sell type order
            initialOrderType = "SELL"
            steps = int(scalipingOrder[0].steps)
            entryDiff = float(scalipingOrder[0].entryDiff)
            exitDiff = float(scalipingOrder[0].exitDiff)
            startPrice = float(scalipingOrder[0].startPrice)
            instrument_token = int(scalipingOrder[0].instrumentToken)
            lotQuantity = int(scalipingOrder[0].lotQuantity)
            # Place an order
            
            for x in range(steps):
                print(x)
                outputQuery = client.place_order(order_type="N", instrument_token=instrument_token, transaction_type=initialOrderType, quantity=lotQuantity,
                                                 price=startPrice, disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="order"+str(x))
                if(scalipingOrder[0].instrumenttype == 'Normal'):
                    orderhistoryvariable = outputQuery["Success"]['NSE']

                if(scalipingOrder[0].instrumenttype == 'Cash'):
                    orderhistoryvariable = outputQuery["Success"]['NSE-FX']

                equivalentOrderPrice = startPrice - exitDiff
                
                orderHistory = OrderHistory(scalpingOrderid=requestData['orderid'], instrument_token=instrument_token, equivalentOrderPrice=equivalentOrderPrice, order_type="N",
                                            quantity=lotQuantity, order_id=orderhistoryvariable['orderId'], order_status='pending', initialOrderType=initialOrderType, startPrice=startPrice,instrumenttype=scalipingOrder[0].instrumenttype)
                orderHistory.save()
        
                startPrice = startPrice + entryDiff



    
        if scalipingOrder[0].orderType == 'Buy':
            # for buy type order
            initialOrderType = "BUY"
            steps = int(scalipingOrder[0].steps)
            entryDiff = float(scalipingOrder[0].entryDiff)
            exitDiff = float(scalipingOrder[0].exitDiff)
            startPrice = float(scalipingOrder[0].startPrice)
            instrument_token = int(scalipingOrder[0].instrumentToken)
            lotQuantity = int(scalipingOrder[0].lotQuantity)
            # Place an order
            orderHistory = []
            for x in range(steps):
                print(x)
                outputQuery = client.place_order(order_type="N", instrument_token=instrument_token, transaction_type=initialOrderType, quantity=lotQuantity,
                                             price=startPrice, disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="order"+str(x))
                
                if(scalipingOrder[0].instrumenttype == 'Normal'):
                    orderhistoryvariable = outputQuery["Success"]['NSE']

                if(scalipingOrder[0].instrumenttype == 'Cash'):
                    orderhistoryvariable = outputQuery["Success"]['NSE-FX']

                equivalentOrderPrice = startPrice + exitDiff
        
                orderHistory = OrderHistory(scalpingOrderid=requestData['orderid'], instrument_token=instrument_token, equivalentOrderPrice=equivalentOrderPrice, order_type="N",
                                            quantity=lotQuantity, order_id=orderhistoryvariable['orderId'], order_status='pending', initialOrderType=initialOrderType, startPrice=startPrice, instrumenttype=scalipingOrder[0].instrumenttype)
                orderHistory.save()   
        
                startPrice = startPrice - entryDiff

    return HttpResponse("Hello, world. You're at the polls index.")

def cancelOrder(request):
    requestData = request.POST
    OrderHistory.objects.filter(scalpingOrderid=requestData['orderid']).delete()
    scalipingOrders = ScalpingOrder.objects.get(id=requestData['orderid'])
    scalipingOrders.status = 'stop'
    scalipingOrders.save()
   
    return HttpResponse("Hello, world. You're at the polls index.")
    
        
    


def loginUser(request):

    requestData = request.POST
    userId = 'PAR97_56'
    consumerKey = 'Z2wfl8frw78RnUvnO5sNT3C2eEca'
    accessToken = '17f745f8-577e-368f-b76e-c0343fbb43e2'
    accessCode = "7881"
    app_id = "efe683d5-2f91-4649-9bc9-0ae0547d849a"

    client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                               consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
    client.login(password="march@2022")
    client.session_2fa(access_code = accessCode)

    user = User(user_id=userId, consumer_key=consumerKey,access_token=accessToken,
                accessCode=accessCode)
    user.save()
    request.session['user_id'] = user.id
    return HttpResponse("Hello, world. You're at the polls index.")


def addScalping(request):
    requestData = request.POST
    currentdate = datetime.today().strftime('%d-%m-%Y')
    instrumentToken = requestData.get('instrumentToken')
    orderType = requestData.get('orderType')
    lotQuantity = requestData.get('lotQuantity')
    steps = requestData.get('steps')
    entryDiff = requestData.get('entryDiff')
    exitDiff = requestData.get('exitDiff')
    startPrice = requestData.get('startPrice')
    instrumenttype = requestData.get('instrumenttype');
    scaplingOrder = ScalpingOrder(userid=request.session['user_id'], currentdate=currentdate, instrumentToken=instrumentToken, orderType=orderType,
                                  lotQuantity=lotQuantity, steps=steps, entryDiff=entryDiff, exitDiff=exitDiff, startPrice=startPrice ,instrumenttype=instrumenttype)
    scaplingOrder.save()
    return HttpResponse("Hello, world. You're at the polls index.")
