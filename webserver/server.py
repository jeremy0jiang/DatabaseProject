#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DB_USER = "sj2914"
DB_PASSWORD = "drs8pgf8"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  
  # DEBUG: this is debugging code to see what request looks like
  print request.args
  print "welcome to bugs"

  # select name
  cursor = g.conn.execute("SELECT name FROM users")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  context = dict(userNames = names)

  # select city
  city = []
  query = "SELECT cityname FROM city"
  cursor1 = g.conn.execute(query)
  for result in cursor1:
      city.append(result['cityname'])  # can also be accessed using result[0]
  cursor1.close()
  context['city'] = city 

  # select airlines
  airlines = []
  query = "SELECT name FROM airline"
  cursor2 = g.conn.execute(query)
  for result in cursor2:
      airlines.append(result['name'])  # can also be accessed using result[0]
  cursor2.close()
  context['airlines'] = airlines





  print context
  return render_template("index.html", **context)

@app.route('/another')
def another():
  return render_template("anotherfile.html")

@app.route('/ticket', methods=['POST','GET'])
def ticket():
  
  if request.method == 'POST':
      name = request.form.get('name_select')
      if name:
        print "good"
        query = "Select users.name, users.birthday, users.gender, c1.cityname as fromcity ,c2.cityname as tocity, airline.name as Airline,flight.takeofftime,flight.flightduration FROM airline,city c1,flight,tickets,users,city c2 WHERE users.name = '" + name +"'" "AND users.userid = tickets.userid AND flight.fromcityid=c1.cityid and flight.tocityid=c2.cityid and flight.airlineid=airline.airlineid and tickets.flightnum=flight.flightnum and tickets.takeofftime=flight.takeofftime"
        print query
        cursor = g.conn.execute(query)
        tickets = []
        for result in cursor:
          tickets.append(result)  # can also be accessed using result[0]
        cursor.close()
        print tickets
        return render_template("tickets.html", tickets = tickets)
      else:
        print "bad"
        error = "Not Found or Invalid Inputs"
        return render_template("tickets.html", error = error)

@app.route('/checkflight', methods=['POST','GET'])
def checkflight():
  try:
    if request.method == 'POST':
        fromcity = request.form.get('fromCity_select')
        tocity = request.form.get('toCity_select')
        print str(fromcity) + str(tocity)

        if fromcity and tocity:
          print "good"
          query = "Select Flight.flightnum,airline.name, c1.cityname, c2.cityname,jet.series from flight, city c1, city c2,airline, jet where c1.cityname='"+fromcity+ "'" "AND c2.cityname='"+tocity+"'" "AND flight.fromcityid=c1.cityid AND flight.tocityid=c2.cityid AND flight.airlineid=airline.airlineid AND jet.jetid=flight.jetid"
          print query
          cursor1 = g.conn.execute(query)
          flightlist = []
          for result in cursor1:
            flightlist.append(result)  # can also be accessed using result[0]
          cursor1.close()
          return render_template("checkflight.html", flightlist=flightlist)
        else:
          print "bad"
          error = "Not Found or Invalid Inputs"
          return render_template("checkflight.html", error = error)
  except:
      print "bad"
      return render_template("error.html")
        
@app.route('/addlikeairline', methods=['POST','GET'])
def addlikeairline():
  try:
    if  request.method == 'POST':
      username = request.form.get('userNames_like_select')
      airline = request.form.get('airline_like_select')
      print str(username) + str(airline)
    
    
      if username and airline:   
        # get userid
        query1 = "select userid from users where users.name='"+username+"'"
        cursor1 = g.conn.execute(query1)
        userid = -1
        for result in cursor1:
          userid = result['userid']
        cursor1.close()

        # get airlineid
        query1 = "select airlineid from airline where name='"+airline+"'"
        cursor1 = g.conn.execute(query1)
        airlineid = -1
        for result in cursor1:
          airlineid = result['airlineid']
        cursor1.close()

        
        query2="insert into likeairline (userid,airlineid) values("+str(userid)+","+str(airlineid)+")"
        g.conn.execute(query2)
        print query2
        return render_template("addlikeairline.html")
  except:
    print "bad"
    username = request.form.get('userNames_like_select')
    airline = request.form.get('airline_like_select')
    error = username + " has already liked " + airline + ". Please select another one" 
    return render_template("error.html", error = error)


@app.route('/deletelikeairline', methods=['POST','GET'])
def deletelikeairline():

  try:
    if request.method == 'POST':
      username = request.form.get('userNames_dislike_select')
      airline = request.form.get('airline_dislike_select')
      print str(username) + str(airline)
      
      if username and airline:   
        # get userid
        query1 = "select userid from users where users.name='"+username+"'"
        cursor1 = g.conn.execute(query1)
        userid = -1
        for result in cursor1:
          userid = result['userid']
        cursor1.close()

        # get airlineid
        query1 = "select airlineid from airline where name='"+airline+"'"
        cursor1 = g.conn.execute(query1)
        airlineid = -1
        for result in cursor1:
          airlineid = result['airlineid']
        cursor1.close()
    
        query2="DELETE FROM likeairline WHERE userid="+str(userid)+"AND airlineid="+str(airlineid)
        g.conn.execute(query2)
      
        return render_template("deletelikeairline.html")
  except:
    print "bad"
    username = request.form.get('userNames_like_select')
    airline = request.form.get('airline_like_select')
    error = username + " has never not liked " + airline + ". Please select another one" 
    return render_template("error.html", error = error)



@app.route('/showlikeairline', methods=['POST','GET'])
def showlikeline():

  try:
    if request.method == 'POST':
      username = request.form.get('username')
      print str(username)
      
      if username:   
        # get userid
        query1 = "select userid from users where users.name='"+username+"'"
        cursor1 = g.conn.execute(query1)
        userid = -1
        for result in cursor1:
          userid = result['userid']
        cursor1.close()
    
        query2="select A.name FROM likeairline,airline A WHERE likeairline.userid="+str(userid)+"AND A.airlineid=likeairline.airlineid"
        likelist=[]
        cursor2 = g.conn.execute(query2)
        for result in cursor2:
          likelist.append(result['name'])
        cursor2.close()
      
        return render_template("showlikeairline.html",likelist=likelist)
  except:
    print "bad"
    return render_template("error.html")

@app.route('/popularity', methods=['GET','POST'])
def popularity():
  query="with temp as (select likeairline.airlineid,count(*) as Likednum from likeairline group by likeairline.airlineid order by count(*) DESC) select airline.name, temp.likednum from airline,temp where airline.airlineid=temp.airlineid "
  cursor = g.conn.execute(query)
  ranklist=[]
  for result in cursor:
    ranklist.append(result)
  cursor.close()

  return render_template("popularity.html",ranklist=ranklist)
# # Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   cmd = 'INSERT INTO test(name) VALUES (:name1)'
#   g.conn.execute(text(cmd), name1 = name)
#   return redirect('/')



if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
