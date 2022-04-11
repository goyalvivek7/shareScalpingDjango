from django.apps import AppConfig
import time
import threading
import os 

class ShareConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'share'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            time.sleep(10)
            t = threading.Thread(target=backgroundTask.backgroundTest,args=[100])
            t.setDaemon(True)
            t.start()

      
class backgroundTask():
    def backgroundTest(id):
        
        from django.apps import AppConfig
        from share.models import OrderHistory
        from share.models import User
        from ks_api_client import ks_api

        
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
        
    
        while True:
            try:
                 print('looping')
                 orderHistory = OrderHistory.objects.all()
                 outputOrder = client.order_report()
                 time.sleep(1)
                 for item in orderHistory:
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
            except:
                print('error')
                time.sleep(1)
                client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                                   consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
                client.login(password=passwords)
                client.session_2fa(access_code=accessCode)
            # print(outputOrder)
        print('loop ends')