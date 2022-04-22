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
from share.models import BackgroundProcess
from share.models import Favourite
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

    try:
        var = request.session['user_id'];
        context = {"login": "login"}
        return render(request, 'share/dashboard.html', context)
        
    except:
        scalpingOrder = ScalpingOrder.objects.all()
        context = {
            "scalpingOrder": scalpingOrder}
        return render(request, 'share/login.html', context)
    


def dashboardView(request):
    try :
        var = request.session['user_id'];
        loggedInUser = request.session['user_id'];
        UserData = User.objects.get(id=loggedInUser)
        scalpingOrder = ScalpingOrder.objects.all()
        context = {
            "scalpingOrder": scalpingOrder,"loggedInUser":UserData.user_id}
        return render(request, 'share/dashboard.html', context)
    except:
        context = {}
        return render(request, 'share/login.html', context)


def addNewScalping(request):
    fav = Favourite.objects.all()
    context = {"addnew": "addnew","fav":fav}
    return render(request, 'share/addNewScalping.html', context)


def editScalping(request):
    requestData = request.POST
    request.session['orderIdForModification'] = requestData['orderid']
    return HttpResponse("Hello, world. You're at the polls index.")  

def openEditScalping(request):
    context = {"addnew": "addnew"}
    return render(request, 'share/editScalping.html', context)



def deleteScalping(request):
    requestData = request.POST
    scalipingOrder = ScalpingOrder.objects.filter(id=requestData['orderid'])  
    scalipingOrder.delete()
    orderHistroy = OrderHistory.objects.filter(scalpingOrderid=requestData['orderid'])  
    orderHistroy.delete()
    return HttpResponse("Hello, world. You're at the polls index.")    
    



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


def addToFav(request):
    requestData = request.POST
    instrumentToken = requestData['instrumentToken']
    fav = Favourite(instrumentToken=instrumentToken)
    fav.save()
    return HttpResponse("Hello, world. You're at the polls index.")
   


def runScalping(request):
    requestData = request.POST
    scalipingOrder = ScalpingOrder.objects.filter(id=requestData['orderid'])

    backgroundProcess = BackgroundProcess.objects.all()
    process = backgroundProcess[0]
    process.status = 'stop'
    process.save()

    if scalipingOrder.count() > 0:
        userData = User.objects.all()
        user = userData[0]
    
        userId = user.user_id
        consumerKey = user.consumer_key
        accessToken = user.access_token
        accessCode = user.accessCode
        app_id = user.app_id
        passwords = user.password

        client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                                   consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
        client.login(password=passwords)
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

                if(scalipingOrder[0].instrumenttype == 'Fno'):
                    orderhistoryvariable = outputQuery["Success"]['NSE']

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

                if(scalipingOrder[0].instrumenttype == 'Fno'):
                    orderhistoryvariable = outputQuery["Success"]['NSE']    

                equivalentOrderPrice = startPrice + exitDiff
        
                orderHistory = OrderHistory(scalpingOrderid=requestData['orderid'], instrument_token=instrument_token, equivalentOrderPrice=equivalentOrderPrice, order_type="N",
                                            quantity=lotQuantity, order_id=orderhistoryvariable['orderId'], order_status='pending', initialOrderType=initialOrderType, startPrice=startPrice, instrumenttype=scalipingOrder[0].instrumenttype)
                orderHistory.save()   
        
                startPrice = startPrice - entryDiff

    backgroundProcess = BackgroundProcess.objects.all()
    process = backgroundProcess[0]
    process.status = 'running'
    process.save()            
    
    newScalpOrder = ScalpingOrder.objects.get(id=requestData['orderid'])
    newScalpOrder.status = 'active'
    newScalpOrder.save()
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
    userId = requestData['userId']
    consumerKey = requestData['consumerKey']
    accessToken = requestData['accessToken']
    accessCode = requestData['accessCode']
    app_id = requestData['appId']
    passwords = requestData['password']

    client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                               consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
    client.login(password=passwords)
    client.session_2fa(access_code = accessCode)

    user = User(user_id=userId, consumer_key=consumerKey,access_token=accessToken,
                accessCode=accessCode,app_id = app_id ,password = passwords)
    user.save()

    backgroundProcess = BackgroundProcess.objects.all()
    process = backgroundProcess[0]
    process.status = 'running'
    process.save()

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
    instrumenttype = requestData.get('instrumenttype')
    intrumentTag = requestData.get('instrumentName')
    scaplingOrder = ScalpingOrder(userid=request.session['user_id'], currentdate=currentdate, instrumentToken=instrumentToken, orderType=orderType,
                                  lotQuantity=lotQuantity, steps=steps, entryDiff=entryDiff, exitDiff=exitDiff, startPrice=startPrice ,instrumenttype=instrumenttype,instrumentTag=intrumentTag)
    scaplingOrder.save()
    return HttpResponse("Hello, world. You're at the polls index.")
