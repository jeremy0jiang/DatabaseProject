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
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



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

  cursor = g.conn.execute("SELECT name FROM users")
  names = []
  
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  context = dict(userNames = names)
  print context
  return render_template("index.html", **context)

@app.route('/another')
def another():
  return render_template("anotherfile.html")

@app.route('/ticket', methods=['POST','GET'])
def ticket():
  
  if request.method == 'POST':
      name = request.form['userName']
      year = request.form['year']
      if name and year:
        print "good"
        query = "SELECT * " + "FROM users, tickets " + "WHERE name = '" + name + "'" + " AND users.userid = tickets.userid " + "AND extract(year from users.birthday) = " + year
        print query
        cursor = g.conn.execute(query)
        tickets = []
        for result in cursor:
          tickets.append(result)  # can also be accessed using result[0]
        cursor.close()
        return render_template("tickets.html", tickets = tickets)
      else:
        print "bad"
        error = "Not Found or Invalid Inputs"
        return render_template("tickets.html", error = error)
     




# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  cmd = 'INSERT INTO test(name) VALUES (:name1)'
  g.conn.execute(text(cmd), name1 = name)
  return redirect('/')



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
