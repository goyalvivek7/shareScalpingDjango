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
from share.models import RememberMeUser
from django.contrib import messages
from datetime import datetime
import time
import django_rq
from django_rq import job
from redis import Redis
from rq_scheduler import Scheduler
from django_rq.queues import get_queue
import threading
import json
import threading


def index(request):

    try:
        var = request.session['user_id'];
        context = {"login": "login"}
        return render(request, 'share/dashboard.html', context)
        
    except:
        scalpingOrder = ScalpingOrder.objects.all()
        rememberMeUser = RememberMeUser.objects.all()
        
        try:
            userData = rememberMeUser[0]
        except:
            userData = {}    

        context = {
            "scalpingOrder": scalpingOrder,"user":userData}
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
        rememberMeUser = RememberMeUser.objects.all()
        
        try:
            userData = rememberMeUser[0]
        except:
            userData = {}    

        context = {"user":userData}
        return render(request, 'share/login.html', context)


def addNewScalping(request):
    var = request.session['user_id'];
    loggedInUser = request.session['user_id'];
    UserData = User.objects.get(id=loggedInUser)
    fav = Favourite.objects.all()
    context = {"addnew": "addnew","fav":fav,"loggedInUser":UserData.user_id}
    return render(request, 'share/addNewScalping.html', context)

def openMyFavourite(request):
    var = request.session['user_id'];
    loggedInUser = request.session['user_id'];
    UserData = User.objects.get(id=loggedInUser)
    fav = Favourite.objects.all()
    context = {"addnew": "addnew","fav":fav,"loggedInUser":UserData.user_id}
    return render(request, 'share/myFavourite.html', context)


def deleteFavourite(request):
    requestData = request.POST
    Favourite.objects.filter(id=requestData['favId']).delete()
    return HttpResponse("Hello, world. You're at the polls index.")


def editScalping(request):
    requestData = request.POST
    request.session['orderIdForModification'] = requestData['orderid']
    return HttpResponse("Hello, world. You're at the polls index.")  

def openEditScalping(request):
    scalpingOrder = ScalpingOrder.objects.filter(id=request.session['orderIdForModification'])
    
    ordertType = scalpingOrder[0].orderType
    sellOrder = False
    buyOrder = False
    if(ordertType == 'Buy'):
        buyOrder = True
        sellOrder = False
    else:
        sellOrder = True
        buyOrder = False



    equity = False
    fno = False
    currency = False

    if(scalpingOrder[0].instrumenttype == 'Normal'):
        equity = True
        fno = False
        currency = False
    elif(scalpingOrder[0].instrumenttype == 'Fno'):
        equity = False
        fno = True
        currency = False  
    elif(scalpingOrder[0].instrumenttype == 'Cash'):
        equity = False
        fno = False
        currency = True       


    var = request.session['user_id'];
    loggedInUser = request.session['user_id'];
    UserData = User.objects.get(id=loggedInUser)

    fav = Favourite.objects.all()

    context = {"fav":fav,"loggedInUser":UserData.user_id,"scalpingOrder": scalpingOrder[0],"sellOrder":sellOrder,"buyOrder":buyOrder,"equity":equity,"fno":fno,"currency":currency}
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
    intrumentTag = requestData['instrumentTag']
    fav = Favourite(instrumentToken=instrumentToken,instrumentTag=intrumentTag)
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

    RememberMeUser.objects.all().delete()
    rememberMeUser = RememberMeUser(user_id=userId, consumer_key=consumerKey,access_token=accessToken,
                accessCode=accessCode,app_id = app_id ,password = passwords)
    rememberMeUser.save()

    client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                               consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
    client.login(password=passwords)
    client.session_2fa(access_code = accessCode)

    user = User(user_id=userId, consumer_key=consumerKey,access_token=accessToken,
                accessCode=accessCode,app_id = app_id ,password = passwords)
    user.save()


    rememberMeUser = RememberMeUser(user_id=userId, consumer_key=consumerKey,access_token=accessToken,
                accessCode=accessCode,app_id = app_id ,password = passwords)
    rememberMeUser.save()

    

    request.session['user_id'] = user.id

    process = BackgroundProcess(status = 'stop')
    process.save()

    t = threading.Thread(target=backgroundTask.backgroundTest,args=[100])
    t.setDaemon(True)
    t.start()

    

    return HttpResponse("Hello, world. You're at the polls index.")


def logoutUser(request):
    User.objects.all().delete()
    del request.session['user_id']
    return HttpResponse("Hello, world. You're at the polls index.")


def updateScalpingOrder(request):
    requestData = request.POST
    scalipingOrder = ScalpingOrder.objects.get(id=request.session['orderIdForModification'])
    scalipingOrder.instrumentToken = requestData.get('instrumentToken')
    scalipingOrder.orderType = requestData.get('orderType')
    scalipingOrder.lotQuantity = requestData.get('lotQuantity')
    scalipingOrder.steps = requestData.get('steps')
    scalipingOrder.entryDiff = requestData.get('entryDiff')
    scalipingOrder.exitDiff = requestData.get('exitDiff')
    scalipingOrder.startPrice = requestData.get('startPrice')
    scalipingOrder.instrumenttype = requestData.get('instrumenttype')
    scalipingOrder.instrumentTag = requestData.get('instrumentName')
    scalipingOrder.save()
    orderHistroy = OrderHistory.objects.filter(scalpingOrderid=request.session['orderIdForModification'])  
    orderHistroy.delete()
    return HttpResponse("Hello, world. You're at the polls index.")

def addScalping(request):
    requestData = request.POST

    data = requestData['data']
    jsonEncoded = json.loads(data)

    if(jsonEncoded[0]):
        if(jsonEncoded[0]['type'] == 'buy'):
             currentdate = datetime.today().strftime('%d-%m-%Y')
             instrumentToken = jsonEncoded[0]['instrumentToken']
             orderType = 'Buy'
             lotQuantity = jsonEncoded[0]['lotQuantity']
             steps = jsonEncoded[0]['steps']
             entryDiff = jsonEncoded[0]['entryDiff']
             exitDiff = jsonEncoded[0]['exitDiff']
             startPrice = jsonEncoded[0]['startPrice']
             instrumenttype = jsonEncoded[0]['intrumentType']
             intrumentTag = jsonEncoded[0]['instrumentTag']
             scaplingOrder = ScalpingOrder(userid=request.session['user_id'], currentdate=currentdate, instrumentToken=instrumentToken, orderType=orderType,
                                       lotQuantity=lotQuantity, steps=steps, entryDiff=entryDiff, exitDiff=exitDiff, startPrice=startPrice ,instrumenttype=instrumenttype,instrumentTag=intrumentTag)
             scaplingOrder.save()
        else:
             currentdate = datetime.today().strftime('%d-%m-%Y')
             instrumentToken = jsonEncoded[0]['instrumentToken']
             orderType = 'Sell'
             lotQuantity = jsonEncoded[0]['lotQuantity']
             steps = jsonEncoded[0]['steps']
             entryDiff = jsonEncoded[0]['entryDiff']
             exitDiff = jsonEncoded[0]['exitDiff']
             startPrice = jsonEncoded[0]['startPrice']
             instrumenttype = jsonEncoded[0]['intrumentType']
             intrumentTag = jsonEncoded[0]['instrumentTag']
             scaplingOrder = ScalpingOrder(userid=request.session['user_id'], currentdate=currentdate, instrumentToken=instrumentToken, orderType=orderType,
                                       lotQuantity=lotQuantity, steps=steps, entryDiff=entryDiff, exitDiff=exitDiff, startPrice=startPrice ,instrumenttype=instrumenttype,instrumentTag=intrumentTag)
             scaplingOrder.save()

    try:         
         if(jsonEncoded[1]):
             if(jsonEncoded[1]['type'] == 'buy'):
                  currentdate = datetime.today().strftime('%d-%m-%Y')
                  instrumentToken = jsonEncoded[1]['instrumentToken']
                  orderType = 'Buy'
                  lotQuantity = jsonEncoded[1]['lotQuantity']
                  steps = jsonEncoded[1]['steps']
                  entryDiff = jsonEncoded[1]['entryDiff']
                  exitDiff = jsonEncoded[1]['exitDiff']
                  startPrice = jsonEncoded[1]['startPrice']
                  instrumenttype = jsonEncoded[1]['intrumentType']
                  intrumentTag = jsonEncoded[1]['instrumentTag']
                  scaplingOrder = ScalpingOrder(userid=request.session['user_id'], currentdate=currentdate, instrumentToken=instrumentToken, orderType=orderType,
                                            lotQuantity=lotQuantity, steps=steps, entryDiff=entryDiff, exitDiff=exitDiff, startPrice=startPrice ,instrumenttype=instrumenttype,instrumentTag=intrumentTag)
                  scaplingOrder.save()
             else:
                  currentdate = datetime.today().strftime('%d-%m-%Y')
                  instrumentToken = jsonEncoded[1]['instrumentToken']
                  orderType = 'Sell'
                  lotQuantity = jsonEncoded[1]['lotQuantity']
                  steps = jsonEncoded[1]['steps']
                  entryDiff = jsonEncoded[1]['entryDiff']
                  exitDiff = jsonEncoded[1]['exitDiff']
                  startPrice = jsonEncoded[1]['startPrice']
                  instrumenttype = jsonEncoded[1]['intrumentType']
                  intrumentTag = jsonEncoded[1]['instrumentTag']
                  scaplingOrder = ScalpingOrder(userid=request.session['user_id'], currentdate=currentdate, instrumentToken=instrumentToken, orderType=orderType,
                                            lotQuantity=lotQuantity, steps=steps, entryDiff=entryDiff, exitDiff=exitDiff, startPrice=startPrice ,instrumenttype=instrumenttype,instrumentTag=intrumentTag)
                  scaplingOrder.save()        
    except:
         print('error')


    



    return HttpResponse("Hello, world. You're at the polls index.")


class backgroundTask():

    def backgroundTest(id):
        
        from django.apps import AppConfig
        from share.models import OrderHistory
        from share.models import User
        from ks_api_client import ks_api
        from share.models import BackgroundProcess
        from share.models import ScalpingOrder

        
        userData = User.objects.all()
        if userData.count() > 0:
            backgroundProcess = BackgroundProcess.objects.all()
            process = backgroundProcess[0]
            process.status = 'running'
            process.save() 
        else:
            backgroundProcess = BackgroundProcess.objects.all()
            if(backgroundProcess.count() > 0):
                process = backgroundProcess[0]
                process.status = 'stop'
                process.save()
            else:   
                process = BackgroundProcess(status = 'stop')
                process.save()

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
        
    
        while True:
            backgroundProcess = BackgroundProcess.objects.all()
            process = backgroundProcess[0]
            if(process.status == 'running'):
                try:
                     print('looping')
                     orderHistory = OrderHistory.objects.all()
                     outputOrder = client.order_report()
                     time.sleep(1)
                     for item in orderHistory:
                         scalipingOrder = ScalpingOrder.objects.filter(id=item.scalpingOrderid)
                         if scalipingOrder[0].orderType == 'Sell':
                              if item.order_status == 'pending':
                                  for historyOrder in outputOrder['success']:
                                      if int(item.order_id) == historyOrder['orderId'] and historyOrder['status'] == 'TRAD':
                                          print('submit order'+str(item.order_id))
                                          if item.initialOrderType == 'BUY':
                                              outputQuery = client.place_order(order_type=item.order_type, instrument_token=int(item.instrument_token), transaction_type="SELL", quantity=int(item.quantity),
                                                                               price=float(item.startPrice), disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="original")
                                              time.sleep(2)
                                              
                                              if(item.instrumenttype == 'Normal'):
                                                  orderhistoryvariable = outputQuery["Success"]['NSE']
                  
                                              if(item.instrumenttype == 'Cash'):
                                                  orderhistoryvariable = outputQuery["Success"]['NSE-FX']
         
                                              if(item.instrumenttype == 'Fno'):
                                                  orderhistoryvariable = outputQuery["Success"]['NSE']    
                  
                                              item.order_id = orderhistoryvariable['orderId']
                                              item.initialOrderType = "SELL"
                                              item.save()
                                          else:
                                              outputQuery = client.place_order(order_type=item.order_type, instrument_token=int(item.instrument_token), transaction_type="BUY", quantity=int(item.quantity),
                                                                               price=float(item.equivalentOrderPrice), disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="equivalent")
                                              time.sleep(2)
                                              
                                              if(item.instrumenttype == 'Normal'):
                                                  orderhistoryvariable = outputQuery["Success"]['NSE']
                  
                                              if(item.instrumenttype == 'Cash'):
                                                  orderhistoryvariable = outputQuery["Success"]['NSE-FX']
         
                                              if(item.instrumenttype == 'Fno'):
                                                  orderhistoryvariable = outputQuery["Success"]['NSE']     
                  
                                              item.order_id = orderhistoryvariable['orderId']
                                              item.initialOrderType = "BUY"
                                              item.save()
                         if scalipingOrder[0].orderType == 'Buy':  
                              if item.order_status == 'pending':
                                         for historyOrder in outputOrder['success']:
                                             if int(item.order_id) == historyOrder['orderId'] and historyOrder['status'] == 'TRAD':
                                                 print('submit order'+str(item.order_id))
                                                 if item.initialOrderType == 'SELL':
                                                     outputQuery = client.place_order(order_type=item.order_type, instrument_token=int(item.instrument_token), transaction_type="BUY", quantity=int(item.quantity),
                                                                                      price=float(item.startPrice), disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="original")
                                                     time.sleep(2)
                                                     
                                                     if(item.instrumenttype == 'Normal'):
                                                         orderhistoryvariable = outputQuery["Success"]['NSE']
                         
                                                     if(item.instrumenttype == 'Cash'):
                                                         orderhistoryvariable = outputQuery["Success"]['NSE-FX']
                
                                                     if(item.instrumenttype == 'Fno'):
                                                         orderhistoryvariable = outputQuery["Success"]['NSE']    
                         
                                                     item.order_id = orderhistoryvariable['orderId']
                                                     item.initialOrderType = "BUY"
                                                     item.save()
                                                 else:
                                                     outputQuery = client.place_order(order_type=item.order_type, instrument_token=int(item.instrument_token), transaction_type="SELL", quantity=int(item.quantity),
                                                                                      price=float(item.equivalentOrderPrice), disclosed_quantity=0, trigger_price=0, validity="GFD", variety="REGULAR", tag="equivalent")
                                                     time.sleep(2)
                                                     
                                                     if(item.instrumenttype == 'Normal'):
                                                         orderhistoryvariable = outputQuery["Success"]['NSE']
                         
                                                     if(item.instrumenttype == 'Cash'):
                                                         orderhistoryvariable = outputQuery["Success"]['NSE-FX']
                
                                                     if(item.instrumenttype == 'Fno'):
                                                         orderhistoryvariable = outputQuery["Success"]['NSE']     
                         
                                                     item.order_id = orderhistoryvariable['orderId']
                                                     item.initialOrderType = "SELL"
                                                     item.save()            
                except:
                    print('error')
                    time.sleep(1)
                    client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                                       consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
                    client.login(password=passwords)
                    client.session_2fa(access_code=accessCode)
                # print(outputOrder)
        print('loop ends')
