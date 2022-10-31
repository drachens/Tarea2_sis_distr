from kafka import KafkaProducer
from kafka.errors import KafkaError
import time
import json

class Producer():
    def __init__(self, data, topic,particion):
        self.topic = topic
        self.data = data
        self.particion = particion
        #self.particion = particion
        self.producer = KafkaProducer(bootstrap_servers=['172.21.0.5:9093'],
                                     value_serializer=lambda m: json.dumps(m).encode('utf-8'))
    def write_data(self):
        data = self.data
        particion = self.particion
       # particion = self.particion
        try:
            self.producer.send(self.topic,value=data,partition=particion)
            return(f"Agregado correctamente a topico: {self.topic} y particion: {particion}")
        except:
            return('Error')