from ctypes import sizeof
import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_cors import CORS
from producer import Producer
from consumer import Consumer_topic_partition
import json
import sys
from time import sleep
from kafka import KafkaConsumer
from kafka.structs import TopicPartition

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(host='172.21.0.2',
                            database='kafka',
                            user='docker',
                            password='docker')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addMember/', methods=['GET','POST'])
def addMember():
    if request.method == 'POST':
        nombre = request.form['name']
        apellido = request.form['lastname']
        rut = request.form['rut']
        correo = request.form['email']
        patente = request.form['patente']
        premium = request.form['premium']
        sas = {"nombre":nombre, "apellido":apellido, "rut":rut, "correo":correo, "patente":patente, "premium":premium}
        if premium == "1":
            particion = 1
            conn = get_db_connection()
            cur = conn.cursor()
            SQLs = '''INSERT INTO miembros(nombre,apellido,rut,patente,premium) VALUES(%s,%s,%s,%s,%s);'''
            insert = (str(nombre), str(apellido), str(rut), str(patente), str(premium))
            try:
                cur.execute(SQLs,insert)
                conn.commit()
            except:
                print("ERROR INSERT URLS")
        else:
            particion = 0
        producer = Producer(sas,'crear-miembros',particion)
        print(producer.write_data())
        #print(sas,file=sys.stdout)
        #topic: crear-miembros, particion 0 -> no-premium
        #topic: crear-miembros, particion 1 -> premium
        return redirect('/')
    
    return render_template('addMember.html')

@app.route('/recordSale/', methods=['GET','POST'])
def recordSale():
    if request.method == 'POST':
        cliente = request.form['client']
        cantidad = request.form['cantidad']
        hora = request.form['time']
        stock = request.form['stock']
        coordenada = [request.form['longitud'],request.form['latitud']]
        venta = {"cliente":cliente, "cantidad":cantidad, "hora":hora, "stock":stock, "coordenada":coordenada}
        stock_1 = {"coordenada":coordenada,"stock":stock}
        ubicacion = {"coordenada":coordenada,"hora":hora}
        #topic: ventas-stock, particion 0 -> ventas
        #topic: ventas-stock, particion 1 -> stock
        #topic: ubicaciones, particion 0 -> carrito_vigente
        producer1 = Producer(venta,'ventas-stock',0)
        producer2 = Producer(stock_1,'ventas-stock',1)
        producer3 = Producer(ubicacion,'ubicaciones',0)
        print(producer1.write_data())
        print(producer2.write_data())
        print(producer3.write_data())
        return redirect("/")
        
    return render_template('recordSale.html')

@app.route('/addFugitive/', methods=['GET','POST'])
def addFugitive():
    if request.method == 'POST':
        coordenada = {"coordenada":[request.form['longitud'],request.form['latitud']]}
        #topic: ubicaciones, particion 1 -> carrito_profugo
        producer = Producer(coordenada,'ubicaciones',1)
        print(producer.write_data())
        return redirect("/")
    return render_template('addFugitive.html')

@app.route('/consumersView/',methods=['GET'])
def consumersView():
    if request.method == 'GET':
        consumer = Consumer_topic_partition('update-carrito',1,'earliest','carro','fugas_0')
        #print(consumer.subscribe(['update-miembros','update-carrito']))
        print(consumer)
        coordenadas = []
        bucle = True
        while bucle == True:
            print("polling...")
            records = consumer.consume().poll(timeout_ms=1000)
            if records:
                for _,consumer_records in records.items():
                    for consumer_record in consumer_records:
                        coordenadas.append(consumer_record.value)
                        #print(consumer_record.value['coordenada'])
                        if(consumer_record.value):
                            continue
                        else:
                            break
            else:
                bucle = False
        print(coordenadas)
        return render_template('consumersView.html',coordenadas=coordenadas,len=len(coordenadas))

@app.route('/ventasDiarias/',methods=['GET'])
def ventasDiarias():
    #topic: ventas-stock, particion 0 -> ventas
    if request.method == 'GET':
        consumer = Consumer_topic_partition('ventas-stock',0,'ventas')
        ventas = []
        bucle = True
        while bucle:
            records = consumer.consume().poll(timeout_ms=1000)
            if records:
                for _,consumer_records in records.items():
                    for consumer_record in consumer_records:
                        ventas.append(consumer_record.value)
                        #print(consumer_record.value['coordenada'])
                        if(consumer_record.value):
                            continue
                        else:
                            break
            else:
                bucle = False
        #DISTINTOS CARRITOS
        carritos = []
        for i in ventas:
            if i['coordenada'] in carritos:
                pass
            else:
                carritos.append(i['coordenada'])
        print("carritos")
        print(carritos)
        #CANTIDAD SOPAIPILLAS VENDIDAS Y CLIENTES POR CARRITO
        vendidas=[]
        for carrito in carritos: # CARRITOS:ARRAY DE COORDENADAS DE CADA CARRITO
            sum = 0
            clientes = 0
            for venta in ventas:
                if carrito == venta['coordenada']:
                    sum = sum + int(venta['cantidad'])
                    clientes = clientes + 1
                else:
                    pass
            vendidas.append({"ubicacion_carrito":carrito,"promedio_ventas":sum/clientes, "clientes_totales":clientes})
        
        print("VENDIDAS")
        print(vendidas)
    return render_template('ventasDiarias.html',vendidas=vendidas,len=len(vendidas))

@app.route('/resposicionStock/',methods=['GET'])
def reposicionStock():
    #topic: ventas-stock, particion 1 -> stock
    if request.method == 'GET':
        consumer = Consumer_topic_partition('ventas-stock',1,'stock')
        bucle = True
        count=0
        count_2=0
        reposiciones = []
        stock_s = []
        while bucle:
            records = consumer.consume().poll(timeout_ms=1000)
            for _,consumer_records in records.items():
                for consumer_record in consumer_records:
                    if(int(consumer_record.value['stock'])<=20):
                        print('REPONER STOCK')
                        sas = {"ubicacion":consumer_record.value['coordenada'],"stock":int(consumer_record.value['stock'])}
                        if count <= 4:
                            stock_s.append(sas)
                            count = count + 1
                        else:
                            reposiciones.append({count_2:stock_s})
                            stock_s = []
                            stock_s.append(sas)
                            count = 1
                            count_2 = count_2 + 1
                        print(stock_s)
                        print(reposiciones)
                    else:
                        print(reposiciones)

                
    return render_template('resposicionStock.html')