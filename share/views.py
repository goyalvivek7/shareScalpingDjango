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


def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
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

    print(requestData['orderid'])

    scalipingOrder = ScalpingOrder.objects.filter(id=requestData['orderid'])
    print(scalipingOrder[0].orderType)

    if scalipingOrder.count() > 0:

        userId = 'RAJEE19970'
        consumerKey = 'pdRLQ0EOtduAn91p7wdLiqFkxnca'
        accessToken = '3825657f-4b11-34da-91ef-f3350affb90e'
        accessCode = "9372"
        app_id = "99628ce6-d9d0-4161-b12b-10fdf36ac5bf"
    
        client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                                   consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
        client.login(password="march@2022")
        client.session_2fa(access_code=accessCode)
    
        
    
        if scalipingOrder[0].orderType == 'Sell':
            # for sell type order
            initialOrderType = "SELL"
            steps = 5
            entryDiff = 0.005
            exitDiff = 0.005
            startPrice = 99.2875
            instrument_token = 34167
            lotQuantity = 1000
            # Place an order
            orderHistory = []
            for x in range(steps):
                print(x)
                outputQuery = client.place_order(order_type="N", instrument_token=instrument_token, transaction_type=initialOrderType, quantity=lotQuantity,
                                                 price=startPrice, disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="order"+str(x))
                orderhistoryvariable = outputQuery["Success"]['NSE-FX']
                equivalentOrderPrice = startPrice - exitDiff
                orderHistory.append(orderHistoryModel(instrument_token, equivalentOrderPrice, "N",
                                                      lotQuantity, orderhistoryvariable['orderId'], 'pending', initialOrderType, startPrice))
        
                orderHistory = OrderHistory(scalpingOrderid=requestData['orderid'], instrument_token=instrument_token, equivalentOrderPrice=equivalentOrderPrice, order_type="N",
                                            quantity=lotQuantity, order_id=orderhistoryvariable['orderId'], order_status='pending', initialOrderType=initialOrderType, startPrice=startPrice)
                orderHistory.save()
        
                startPrice = startPrice + entryDiff



    
        if scalipingOrder[0].orderType == 'Buy':
            # for buy type order
            initialOrderType = "BUY"
            steps = 12
            entryDiff = 0.05
            exitDiff = 0.05
            startPrice = 3.75
            instrument_token = 48863
            lotQuantity = 850
            # Place an order
            orderHistory = []
            for x in range(steps):
                print(x)
                outputQuery = client.place_order(order_type="N", instrument_token=instrument_token, transaction_type=initialOrderType, quantity=lotQuantity,
                                             price=startPrice, disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="order"+str(x))
                orderhistoryvariable = outputQuery["Success"]['NSE']
                equivalentOrderPrice = startPrice + exitDiff
                orderHistory.append(orderHistoryModel(instrument_token, equivalentOrderPrice, "N",
                                lotQuantity, orderhistoryvariable['orderId'], 'pending', initialOrderType, startPrice))
        
                orderHistory = OrderHistory(scalpingOrderid=requestData['orderid'], instrument_token=instrument_token, equivalentOrderPrice=equivalentOrderPrice, order_type="N",
                                            quantity=lotQuantity, order_id=orderhistoryvariable['orderId'], order_status='pending', initialOrderType=initialOrderType, startPrice=startPrice)
                orderHistory.save()   
        
                startPrice = startPrice - entryDiff

        sum()
    return HttpResponse("Hello, world. You're at the polls index.")


def sum():


    orderHistory = OrderHistory.objects.all

    userId = 'RAJEE19970'
    consumerKey = 'pdRLQ0EOtduAn91p7wdLiqFkxnca'
    accessToken = '3825657f-4b11-34da-91ef-f3350affb90e'
    accessCode = "9372"
    app_id = "99628ce6-d9d0-4161-b12b-10fdf36ac5bf"

    client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                               consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
    client.login(password="march@2022")
    client.session_2fa(access_code=accessCode)

    for x in range(90000000000000000000):
        outputOrder = client.order_report()
        time.sleep(1)
        for item in orderHistory:
            if item.order_status == 'pending':
                for historyOrder in outputOrder['success']:
                    if item.order_id == historyOrder['orderId'] and historyOrder['status'] == 'TRAD':
                        print('submit order'+str(item.order_id))
                        if item.initialOrderType == 'BUY':
                            outputQuery = client.place_order(order_type=item.order_type, instrument_token=item.instrument_token, transaction_type="SELL", quantity=item.quantity,
                                                             price=item.startPrice, disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="original")
                            time.sleep(2)
                            orderhistoryvariable = outputQuery["Success"]['NSE-FX']
                            item.order_id = orderhistoryvariable['orderId']
                            item.initialOrderType = "SELL"
                        else:
                            outputQuery = client.place_order(order_type=item.order_type, instrument_token=item.instrument_token, transaction_type="BUY", quantity=item.quantity,
                                                             price=item.equivalentOrderPrice, disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="equivalent")
                            time.sleep(2)
                            orderhistoryvariable = outputQuery["Success"]['NSE-FX']
                            item.order_id = orderhistoryvariable['orderId']
                            item.initialOrderType = "BUY"

        # print(outputOrder)
    print('loop ends')


def printHello():
    for x in range(90000000000000000000):
        print('hello')

    print('loop ends')


def loginUser(request):

    queue = get_queue('default')
    job = queue.enqueue_at(datetime(2020, 10, 10), printHello)

    # scheduler = django_rq.get_scheduler('default')
    # scheduler.schedule(
    #     scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
    #     func=printHello,                     # Function to be queued
    #     args=[],             # Arguments passed into function when executed
    #     kwargs={},         # Keyword arguments passed into function when executed
    #     interval=1,                   # Time before the function is called again, in seconds
    #     repeat=10,                     # Repeat this number of times (None means repeat forever)
    #     meta={'foo': 'bar'}
    # )
    # scheduler.run()

    # requestData = request.POST
    # print(requestData)
    # userId = 'PAR97_56'
    # consumerKey = 'Z2wfl8frw78RnUvnO5sNT3C2eEca'
    # accessToken = '17f745f8-577e-368f-b76e-c0343fbb43e2'
    # accessCode = "3367"

    # client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
    #                            consumer_key=consumerKey, ip="127.0.0.1", app_id="efe683d5-2f91-4649-9bc9-0ae0547d849a")
    # client.login(password="march@2022")
    # client.session_2fa(access_code = accessCode)

    # user = User(user_id=userId, consumer_key=consumerKey,access_token=accessToken,
    #             accessCode=accessCode)
    # user.save()
    # print(user.id)
    # request.session['user_id'] = user.id
    return HttpResponse("Hello, world. You're at the polls index.")


def addScalping(request):
    requestData = request.POST
    print(requestData)
    currentdate = datetime.today().strftime('%d-%m-%Y')
    instrumentToken = requestData.get('instrumentToken')
    orderType = requestData.get('orderType')
    lotQuantity = requestData.get('lotQuantity')
    steps = requestData.get('steps')
    entryDiff = requestData.get('entryDiff')
    exitDiff = requestData.get('exitDiff')
    startPrice = requestData.get('startPrice')
    scaplingOrder = ScalpingOrder(userid=request.session['user_id'], currentdate=currentdate, instrumentToken=instrumentToken, orderType=orderType,
                                  lotQuantity=lotQuantity, steps=steps, entryDiff=entryDiff, exitDiff=exitDiff, startPrice=startPrice)
    scaplingOrder.save()
    return HttpResponse("Hello, world. You're at the polls index.")
