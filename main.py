from flask import Flask, render_template, request, redirect, url_for
import pyodbc as db
import socket
import datetime as dt

database = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=northwind;Trusted_Connection=yes;'
logfile = 'c:\\temp\\process_log.txt'
logfile2 = 'c:\\temp\\process_log2.txt'

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
id_field = host_name + ' / ' + host_ip

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/db')
def DatabaseTable():
    (result, columns, id_field) = GetDatabaseTable()
    return render_template('database.html', data = result, columns = columns, idfield = id_field)

@app.route('/postback/<id>/<processid>') 
def Postback(id, processid):
    RunProcess(id, processid)
    return render_template('processrunning.html', companyname = id, processid = processid, idfield = id_field)

@app.route('/postback2/')
def Postback2():
    printstring = id_field + ', ' + str(dt.datetime.now())
    PrintToFile(logfile2, printstring)
    return redirect(url_for('home'))

def RunProcess(id, processid):
    print ('Initiating Process for ' + id, processid)
    printstring = id + ',' + socket.gethostname() + \
        ',' + str(dt.datetime.now()) + ',' + str(processid)
    PrintToFile(logfile, printstring)
    print ('Process Complete for ' + id, processid)

def GetDatabaseTable():
    try:
        conn = db.connect(database)
        cursor = conn.cursor()
    except db.Error as err:
        sqlState = err.args[1]
        print (sqlState)

    sql = 'SELECT ShipperID, CompanyName, Phone, ltrim(str(ABS(CHECKSUM(NewId())) % 10000000)) as ProcessID FROM [dbo].[Shippers]'
    cursor.execute(sql)
    result = cursor.fetchall()
    columns =  [column[0] for column in cursor.description]

    return result, columns, id_field

def PrintToFile(filepath, printstring):
    with open(filepath, 'a+') as f:
        print (printstring, file = f)
 

if __name__ == '__main__':
     app.run(debug=True)