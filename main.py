from flask import Flask, render_template,request,redirect,url_for,session
import sqlite3
import os

current = ""
adminCh = False
DevKey = 'UvqPf2fGbH2YoWaetp1bA'

app = Flask(__name__)

app.secret_key = '\xf0\xa5\x9ewe6\x82RU\x8b\t\x0b\xb6\xcc\xf8\xb2\xdb\x02\x83\xab\x0f\x13\x15'

conn = sqlite3.connect("Users.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (first_name text NOT NULL,last_name text NOT NULL,email text PRIMARY KEY NOT NULL, password text NOT NULL, username text NOT NULL)")
c.execute("CREATE TABLE IF NOT EXISTS bullets (ID integer PRIMARY KEY AUTOINCREMENT, email text NOT NULL, username text NOT NULL, bullet text NOT NULL)")
c.close()
conn.close()

@app.route('/',methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    if request.method == 'POST':
        if request.form.get('first_name'):
            fname = request.form['first_name']
            lname = request.form['last_name']
            email = request.form['email']
            passw = request.form['password']
            cpass = request.form['cpassword']
            uname = request.form['username']
            t = (email.lower(),)
            c.execute("SELECT email FROM users WHERE email = ?", t)
            checkEmail = c.fetchone()
            if checkEmail != None:
                c.close()
                conn.close()
                return render_template('signup.html', error = "Email already in use")
            t = (uname.lower(),)
            c.execute("SELECT username FROM users WHERE username = ?", t)
            checkUser = c.fetchone()
            if checkUser != None:
                c.close()
                conn.close()
                return render_template('signup.html', error = "Username already in use")
            c.execute("INSERT INTO users VALUES(?,?,?,?,?)",(fname,lname,email,passw,uname))
            conn.commit()
            c.close()
            conn.close()
            return redirect(url_for('signin'))
    if current != '':
        c.execute("SELECT * FROM bullets")
        bulletList = c.fetchall()
        print (bulletList)
        return render_template('user.html', username = current, bullList = bulletList)
    c.close()
    conn.close()
    return render_template('signup.html', error = '')

@app.route('/signin' ,methods=['GET','POST'])
def signin():
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    global current
    if request.method == 'POST':
        emai = request.form['email']
        passc = request.form['password']
        if emai == "admin" and passc == "admin1234":
            c.close()
            conn.close()
            global adminCh
            adminCh = True
            return redirect(url_for('admin'))
        else:
            t = (emai.lower(),)
            c.execute("SELECT email, username, password FROM users WHERE email = ?",t)
            checkLogin = c.fetchone()
            if checkLogin == None:
                c.execute("SELECT email, username, password FROM users WHERE lower(username) = ?",t)
                checkLogin = c.fetchone()
                if checkLogin != None:
                    if checkLogin[2] == passc:
                        c.close()
                        conn.close()
                        current = checkLogin[1]
                        session['logged_in'] = True
                        session['username'] = checkLogin[0]
                        return redirect(url_for('index'))
                    else:
                        c.close()
                        conn.close()
                        return render_template('signin.html', error = "Username and password do not match.")
                c.close()
                conn.close()
                return render_template('signin.html', error = "Username or Email address doesn't exist. Signup first.")
            if checkLogin[2] == passc:
                c.close()
                conn.close()
                current = checkLogin[1]
                session['logged_in'] = True
                session['username'] = checkLogin[0]
                return redirect(url_for('index'))
            c.close()
            conn.close()
            return render_template('signin.html', error = "Email and password do not match.")
    if current != '':
        c.close()
        conn.close()
        return redirect(url_for('index'))
    c.close()
    conn.close()
    return render_template('signin.html', error = '')

@app.route('/addBulletin', methods = ['GET', 'POST'])
def addBulletin():
    if current == '':
        return redirect(url_for('index'))
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    if request.method == 'POST':
        content = request.form['content']
        t = session['username']
        c.execute("INSERT INTO bullets (email,username,bullet) VALUES(?,?,?)",(t,current,content))
        conn.commit()
        c.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('addBull.html', username = current)

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        tempId = int(request.form['submit'])
        conn = sqlite3.connect('Users.db')
        c = conn.cursor()
        c.execute('DELETE FROM bullets WHERE ID = ?',(tempId,))
        conn.commit()
        c.execute("SELECT * FROM bullets")
        bulletList = c.fetchall()
        return render_template('admin.html', username = "admin", bulletList = bulletList)
    global admin
    if adminCh == True:
        conn = sqlite3.connect('Users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM bullets")
        bulletList = c.fetchall()
        print (bulletList)
        return render_template('admin.html', username="admin", bulletList = bulletList)
    else:
        return redirect(url_for('signin'))

@app.route('/edit', methods = ['GET', 'POST'])
def edit():
    if request.method == 'POST':
        tempId = session['tempId']
        content = request.form['content']
        conn = sqlite3.connect('Users.db')
        c = conn.cursor()
        c.execute("UPDATE bullets SET bullet = ? WHERE ID = ?",(content,tempId))
        conn.commit()
        c.close()
        conn.close()
        return redirect(url_for('index'))
    if current == '':
        return redirect(url_for('index'))
    return render_template('edit.html', ID = session['tempId'])

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if request.method == 'POST':
        session['tempId'] = int(request.form['submit'])
        return redirect(url_for('edit'))
    if current == '':
        return redirect(url_for('index'))
    conn = sqlite3.connect("Users.db")
    c = conn.cursor()
    u = (session['username'],)
    c.execute("SELECT * FROM users WHERE email = ?",u)
    userData = c.fetchone()
    c.execute("SELECT * FROM bullets WHERE email = ?",u)
    bulletData = c.fetchall()
    print(userData)
    print(bulletData)
    return render_template('profile.html', username = current, userData = userData, bulletData = bulletData)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session['logged_in'] = False
    global adminCh
    global current
    adminCh = False
    current = ''
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug = True)
