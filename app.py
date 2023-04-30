from flask import Flask,redirect,render_template,request
import pyodbc
import time
import redis
import pickle
import hashlib

app = Flask(__name__)

server = 'kshitija.database.windows.net'
database = 'ksh'
username = '*************'
password = '*******'
driver= '{ODBC Driver 17 for SQL Server}'
myHostname = "kshiti.redis.cache.windows.net"
myPassword = "GkOhC1t41JqxUAooMBp3V5CL1ZDONtMLGAzCaNZMUrY="

connect = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

cursor = connect.cursor()

redi = redis.Redis(host='kshiti.redis.cache.windows.net',
        port=6380, db=0, password='GkOhC1t41JqxUAooMBp3V5CL1ZDONtMLGAzCaNZMUrY=', ssl=True)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/search_with_redis')
def search_with_redis():
    return render_template('search_with_redis.html')

@app.route('/search_without_redis')
def search_without_redis():
    return render_template('search_without_redis.html')

@app.route('/with_out_redis', methods=['POST','GET'])
def with_out_redis():
    no=int(request.form['no'])
    mag1=request.form['mag1']
    mag2=request.form['mag2']
    data1="select  *  from all_month WHERE mag  between '"+mag1+"' and '"+mag2+"'"
    start = time.time()
    for i in range(1,no):
            cursor.execute(data1)
            rows = cursor.fetchall()
    end = time.time()
    executiontime=end - start
    data2 = cursor.execute("select count(*) from all_months WHERE mag  between '"+mag1+"' and '"+mag2+"'")
    count=data2.fetchone()
    return render_template('mag.html',rows=rows,timee=executiontime,count=count)

@app.route('/with_redis', methods=['POST','GET'])
def with_redis():  
    no=int(request.form['no'])
    mag1=request.form['mag1']
    mag2=request.form['mag2']
    data1 = "select  *  from all_months WHERE mag  between '"+mag1+"' and '"+mag2+"'"
    hash = hashlib.sha224(data1.encode('utf-8')).hexdigest()
    key = "redis_cache:" + hash
    start = time.time()
    for i in range(1,no):
        if(redi.get(key)):
            pass
        else:
            cursor.execute(data1)
            rows = cursor.fetchall()
            redi.set(key, pickle.dumps(rows))
            
            redi.expire(key,36)
    end = time.time()
    executiontime=end-start
    data2 = cursor.execute("select count(*) from all_months WHERE mag  between '"+mag1+"' and '"+mag2+"'")
    count = data2.fetchone()
    return render_template('mag.html',rows=rows,timee=executiontime,count=count)


if __name__ == '__main__':
  app.debug = True  
  app.run()