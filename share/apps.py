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
        from ks_api_client import ks_api

        orderHistory = OrderHistory.objects.all()
    
        userId = 'PAR97_56'
        consumerKey = 'Z2wfl8frw78RnUvnO5sNT3C2eEca'
        accessToken = '17f745f8-577e-368f-b76e-c0343fbb43e2'
        accessCode = "4315"
        app_id = "efe683d5-2f91-4649-9bc9-0ae0547d849a"
    
        client = ks_api.KSTradeApi(access_token=accessToken, userid=userId,
                                   consumer_key=consumerKey, ip="127.0.0.1", app_id=app_id)
        client.login(password="march@2022")
        client.session_2fa(access_code=accessCode)
    
        for x in range(90000000000000000000):
            print('looping')
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
    
                                item.order_id = orderhistoryvariable['orderId']
                                item.initialOrderType = "BUY"
                                item.save()
    
            # print(outputOrder)
        print('loop ends')