import os

import pyodbc

from flask import (Flask, redirect, render_template, request,send_from_directory, url_for,jsonify,session)
from urllib.parse import quote
app = Flask(__name__)

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import requests
import json
import os
import base64
from base64 import b64encode
import time
import msal
from flask_session import Session
from config import Config
server = 'tcp:sqlsrv-eastus2-dev-001.database.windows.net,1433'
database = 'CustomMetadata'
username = 'Login'
password = 'Thechanger@123'
driver = '{ODBC Driver 18 for SQL Server}'

connection_string = f'Driver={driver};Server={server};Database={database};Uid={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


def fetch_dropdownvalues():
   conn = pyodbc.connect(connection_string)
   cursor = conn.cursor()
   cursor.execute('SELECT DISTINCT Version FROM Metadata')  # Adjust your query
   dropdown_items = cursor.fetchall()
   return [row[0] for row in dropdown_items]

def CustomerNamesInfo(version):
   conn = pyodbc.connect(connection_string)
   cursor = conn.cursor()
   print(version)
   Query="SELECT DISTINCT ServerInstance FROM Metadata where version = ?"
   cursor.execute(Query,(version,))  # Adjust your query
   CustomerNames = cursor.fetchall()
   print(CustomerNames)
   return [row[0] for row in CustomerNames]



def format_license_info(license_info):
    formatted_info = []
    
    # Split the input into lines
    lines = license_info.split('\r\n')
    
    for line in lines:
        if line.strip() == "":
            formatted_info.append("")
            continue
        elif line.startswith(' '):
            formatted_info[-1] += ' ' + line.strip()
        else:
            formatted_info.append(line.strip())
    
    return "\n".join(formatted_info)


def GetVMName(CustomerName,Version):
    print(CustomerName)
    print(Version)
    cursor=conn.cursor()
    query="SELECT Server FROM Metadata where ServerInstance = ? and version = ?"
    cursor.execute(query, CustomerName,Version)
    VMName=cursor.fetchall()
    print(VMName[0][0])
    return VMName[0][0]



@app.route('/')
def index():
    return render_template('home.html')



@app.route('/appvalidation')
def appversion():
   return render_template('AppSearch.html')

@app.route('/ASearchResult', methods=['GET'])
def ASearchResult():
    CN = request.args.get('CustomerName', '').strip()

    if not CN:
        return render_template('index.html', error="Please enter a valid ServerInstance.")

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    query = "SELECT * FROM AppMetadata where ServerInstance = ?"
    cursor.execute(query,CN)
    data = cursor.fetchall()
    query="SELECT Version FROM Metadata WHERE ServerInstance = ?"
    cursor.execute(query, (CN,))
    version=cursor.fetchone()
    cursor.close()
    return render_template('AppVAL.html',CN =CN, results=data, version=version)




@app.route('/LicenseValidate')
def version():
    return render_template('LicenseSearch.html')

@app.route('/recommend')
def recommend():
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify(results=[])

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    cursor.execute("SELECT ServerInstance FROM Metadata WHERE ServerInstance LIKE ?", ('%' + query + '%',))
    
    results = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(results=results)

@app.route('/LSearchResult', methods=['GET'])
def LSearchResult():
    CN = request.args.get('CustomerName', '').strip()

    if not CN:
        return render_template('index.html', error="Please enter a valid ServerInstance.")

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    query = "SELECT LicenseInfo FROM Metadata WHERE ServerInstance = ?"
    print(query)
    cursor.execute(query, (CN,))
    data = cursor.fetchone()
    query="SELECT Version FROM Metadata WHERE ServerInstance = ?"
    cursor.execute(query, (CN,))
    version=cursor.fetchone()
    conn.close()

    if not data:
        return render_template('index.html', CN=CN, data="No data found.")

    formatted_data = format_license_info(data[0])
    
    return render_template('index.html', CN=CN, data=formatted_data,version=version)








@app.route('/Outagecheck')
def webversion():
   return render_template('WEBIN.html')


@app.route('/WSearchResult',methods=['Get'])
def weblookup():
   print("!!!!")
   CN = request.args.get('CustomerName', '').strip()
   if not CN:
        return render_template('index.html', error="Please enter a valid ServerInstance.")
   conn = pyodbc.connect(connection_string)
   cursor = conn.cursor()
   query="SELECT ServerInstance,Server,State,DatabaseName,DatabaseServer,Webclient,Odataurl,Odatastate,Soapurl,Soapstate FROM Metadata where ServerInstance = ?"
   cursor.execute(query,CN)
   rows = cursor.fetchall()
   print(rows)
   query="SELECT Version FROM Metadata WHERE ServerInstance = ?"
   cursor.execute(query, CN)
   version=cursor.fetchone()
   return render_template('Weblookup.html',CN=CN,results=rows,version=version)

if __name__ == '__main__':
    app.run(debug=True,port=5000)