from kafka import KafkaConsumer
from kafka.errors import KafkaError
from threading import current_thread
import time
import json
from kafka.structs import TopicPartition

class Consumer_topic_partition():
    def __init__(self, topic, particion,group_id):
        self.topic = topic
        self.particion = particion
        #self.client_id = client_id
        self.group_id = group_id
        self.consumer = KafkaConsumer(
            bootstrap_servers=['172.21.0.5:9093'],
            #client_id = self.client_id,
            auto_offset_reset='latest',
            #max_poll_records = 1000,
            #auto_commit_interval_ms=1000,
            #enable_auto_commit=True,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.consumer.assign([TopicPartition(self.topic,self.particion)])
        #self.consumer.commit()
    def consume(self):
        try:
            return(self.consumer)
        except:
            return(-1)