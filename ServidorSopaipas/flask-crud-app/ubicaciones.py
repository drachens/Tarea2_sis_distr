from consumer import Consumer_topic_partition
import os
import psycopg2
#topic: ubicaciones, particion 1 -> carrito_profugo
#topic: ubicaciones, particion 0 -> carrito_vigente

consumer1 = Consumer_topic_partition('ubicaciones',0,'carrito_vigente')
consumer2 = Consumer_topic_partition('ubicaciones',1,'carrito_profugo')
bucle = True
while bucle:
    #VIGENTES
    records1 = consumer1.consume().poll(timeout_ms=1000)
    records2 = consumer2.consume().poll(timeout_ms=1000)

    if records1:
        print("CARRITOS VIGENTES")
        for _,consumer_records in records1.items():
            for consumer_record in consumer_records:
                print('coordenada:', consumer_record.value['coordenada'],'hora:',consumer_record.value['hora'],'\n')
                if(consumer_record.value):
                    continue
                else:
                    break
    if records2:
        print("CARRITOS PROFUGOS")
        for _,consumer2_records in records2.items():
            for consumer2_record in consumer2_records:
                print(consumer2_record.value['coordenada'],'\n')
                if(consumer2_record.value):
                    continue
                else:
                    break
