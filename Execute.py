from flask import Flask,request, session, render_template, redirect, url_for, abort, flash,jsonify
from datetime import date,datetime
from flask_wtf import FlaskForm
from wtforms import StringField,TextField


import sqlite3,os


app = Flask(__name__)
app.secret_key = 'random_secret_string'




class ArticleForm(FlaskForm):
    title = TextField("Title")
    post = TextField("Post")


   

# class ExampleForm(FlaskForm):
#     example = StringField()

@app.route('/')
def root():
	return render_template('Register.html')

@app.route("/signup",methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		UID = request.form['userId']
		Name = request.form['name']
		Email = request.form['email']
		pwd = request.form['pwd']
		cfrmPwd = request.form['cpwd']
		print("welcome***")
		if(pwd==cfrmPwd):
			 with sqlite3.connect('database.db') as con:
			 	cur = con.cursor()
			 	cur.execute('INSERT INTO users(rollnum,name,email,password) VALUES(?,?,?,?)',(UID,Name,Email,pwd))
			 	con.commit()
			 	message = "registered successfull"
			 	flash(message)
		else:
			message = "not registered"
			flash(message)
		
	return redirect(url_for('root'))

@app.route("/login",methods=['POST','GET'])
def login():
	if request.method=='POST':
		UID=request.form['userId']#UID = userId #pwd=password
		pwd=request.form['pwd']
		if is_valid(UID,pwd):
			session['rollnum']=UID
			universal=UID
			return redirect(url_for('homepage'))
		else:
			message = "enter correct credentials"
			flash(message)
	return render_template('Login.html')		



@app.route("/homepage")
def homepage():
	loggedIn,Name = getLoginDetails()
	print(Name)
	with sqlite3.connect('database.db') as conn:
		if loggedIn:
			cur = conn.cursor()
			cur.execute('SELECT title,post,postId,createddate,Tupvotes,Tdownvotes FROM posts ORDER BY createddate')
			Data=cur.fetchall()
			return render_template('Home.html',UserName=Name,UserPosts=Data)#UserName is u can find that variable in .html file
	return render_template('Login.html')

@app.route("/signout")
def signout():
	session.pop('rollnum', None)
	return redirect(url_for('root'))

@app.route("/addblog")
def addblog():
	if 'rollnum' in session:
		return render_template('addblog.html')
	return redirect(url_for("homepage"))

@app.route("/createpost",methods=['GET','POST'])
def createpost():
	if 'rollnum' in session:
		 loggedIn,Name = getLoginDetails()
		 today=date.today()
		 print("get in...")
		 print(session['rollnum'])
		 if request.method=='POST':
		 	print("get in...")
		 	title=request.form['title']
		 	post = request.form['post']
		 	with sqlite3.connect('database.db') as con:
		 		cur=con.cursor()
		 		cur.execute('INSERT INTO posts(rollnum,title,post,createddate,Tupvotes,Tdownvotes) VALUES(?,?,?,?,?,?)',(session['rollnum'],title,post,today,0,0))
		 		con.commit()
		 	con.close()
	return redirect(url_for('homepage'))





@app.route("/myposts",methods=['GET','POST'])
def myposts():
	if 'rollnum' in session:
		loggedIn,Name = getLoginDetails()
		with sqlite3.connect('database.db') as conn:
				x = session['rollnum']
				cur = conn.cursor()
				select_stmt = "SELECT title,post,createddate,postId FROM posts WHERE rollnum=?"
				cur.execute(select_stmt,(x,))
				Data=cur.fetchall()
		conn.close()
	return render_template("myposts.html",UserPosts=Data)






@app.route("/comment/<pid>",methods=['GET','POST'])
def comment(pid):
	print(pid)
	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		select_posts = "SELECT title,post,postId FROM posts WHERE postId=?"
		cur.execute(select_posts,(pid,))
		P_Data=cur.fetchall()
		cur.close()
		print(P_Data)
		cur = conn.cursor()
		select_comments="SELECT comment FROM comments WHERE postId=?"
		cur.execute(select_comments,(pid,))
		C_Data=cur.fetchall()
		print(C_Data)
		cur.close()
	if request.method=='POST' and 'rollnum' in session:
		comment=request.form['comment']
		# print("RollNo is:"+session['rollnum']+comment)
		cur=conn.cursor()
		cur.execute('INSERT INTO comments(postId,comment,rollnum) VALUES(?,?,?)',(pid,comment,session['rollnum']))
		conn.commit()
		cur.close()
		cur2 = conn.cursor()
		select_comments="SELECT comment FROM comments WHERE postId=?"
		cur2.execute(select_comments,(pid,))
		C_Data=cur2.fetchall()
		print(C_Data)
		cur2.close()
		render_template("comments.html",PostData=P_Data,Comments=C_Data,PID=pid)
		# conn.close()
	
	return render_template("comments.html",PostData=P_Data,Comments=C_Data,PID=pid)






@app.route('/like', methods = ['GET','POST'])
def like():
	if 'rollnum' in session:
		pid=request.form['post_id']
		with sqlite3.connect('database.db') as conn:
			cur = conn.cursor()
			select_rollnums = "SELECT rollnum FROM votes WHERE postId=?"
			cur.execute(select_rollnums,(pid,))
			RLst=cur.fetchall()#roll nums list
			cur.close()
		# conn.close()
		flag=0
		for rnum in RLst:
			# print(rnum)
			with sqlite3.connect('database.db') as conn:
				if(rnum[0]==session['rollnum']):
					flag=1
					cur = conn.cursor()
					print("okay"+rnum[0]+session['rollnum'])
					cur.execute("UPDATE votes SET upvote=?,downvote=? WHERE postId=? AND rollnum=?",(1,0,pid,session['rollnum']))
					# conn.commit()
					cur.close()
					# conn.close()
			# conn.commit()
		if(flag==0):
			cur=conn.cursor()
			cur.execute('INSERT INTO votes(postId,upvote,downvote,rollnum) VALUES(?,?,?,?)',(pid,1,0,session['rollnum']))
			conn.commit()
			cur.close()


		cur = conn.cursor()
		cur.execute("SELECT upvote FROM votes WHERE postId=?",(pid,))
		upVlist=cur.fetchall()
		cur.close()
		# /print(upV)
		cur = conn.cursor()
		cur.execute("SELECT downvote FROM votes WHERE postId=?",(pid,))
		downVlist=cur.fetchall()
		cur.close()
		sum1=0
		sum2=0
		for e in upVlist:
			sum1+=e[0]
		for e in downVlist:
			sum2+=e[0]
	# print("rollnums are ")
		print(str(sum1)+" "+str(sum2))
	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		cur.execute("UPDATE posts SET Tupvotes=?,Tdownvotes=? WHERE postId=?",(sum1,sum2,pid))
		cur.close()
	conn.close()

	u=sum1
	d=sum2
	return jsonify({'u':u,'d':d})




@app.route('/dislike', methods = ['GET','POST'])
def dislike():
	if 'rollnum' in session:
		pid=request.form['post_id']
		with sqlite3.connect('database.db') as conn:
			cur = conn.cursor()
			select_rollnums = "SELECT rollnum FROM votes WHERE postId=?"
			cur.execute(select_rollnums,(pid,))
			RLst=cur.fetchall()#roll nums list
			cur.close()
		# conn.close()
		flag=0
		for rnum in RLst:
			# print(rnum)
			with sqlite3.connect('database.db') as conn:
				if(rnum[0]==session['rollnum']):
					flag=1
					cur = conn.cursor()
					print("okay"+rnum[0]+session['rollnum'])
					cur.execute("UPDATE votes SET upvote=?,downvote=? WHERE postId=? AND rollnum=?",(0,1,pid,session['rollnum']))
					# conn.commit()
					cur.close()
					# conn.close()
			# conn.commit()
		if(flag==0):
			cur=conn.cursor()
			cur.execute('INSERT INTO votes(postId,upvote,downvote,rollnum) VALUES(?,?,?,?)',(pid,0,1,session['rollnum']))
			conn.commit()
			cur.close()


		cur = conn.cursor()
		cur.execute("SELECT upvote FROM votes WHERE postId=?",(pid,))
		upVlist=cur.fetchall()
		cur.close()
		# /print(upV)
		cur = conn.cursor()
		cur.execute("SELECT downvote FROM votes WHERE postId=?",(pid,))
		downVlist=cur.fetchall()
		cur.close()
		sum1=0
		sum2=0
		for e in upVlist:
			sum1+=e[0]
		for e in downVlist:
			sum2+=e[0]

	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		cur.execute("UPDATE posts SET Tupvotes=?,Tdownvotes=? WHERE postId=?",(sum1,sum2,pid))
		cur.close()

	conn.close()
	u=sum1
	d=sum2
	return jsonify({'u':u,'d':d})






@app.route("/editpost/<pid>",methods=['GET','POST'])
def editpost(pid):
	print(pid)
	form = ArticleForm(request.form)
	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		cur.execute("SELECT * FROM posts WHERE postId=?",[pid])
		result = cur.fetchone()
		cur.close()
		form.title.data=result[1]
		form.post.data  = result[2]
		print(result[1]+"  "+result[2])
	if request.method=='POST':
		print("welcome to post")
		title = request.form['title']
		post = request.form['post']
		cur = conn.cursor()
		print(title+"****"+post)
		cur.execute("UPDATE posts SET title=?,post=? WHERE postId=?",(title,post,pid))
		conn.commit()
		cur.close()
		flash("successfull")
		return redirect(url_for('myposts'))
	return render_template('editblog.html',form=form)



@app.route("/deletepost/<pid>",methods=['GET','POST'])
def deletepost(pid):
	print(pid)
	with sqlite3.connect('database.db') as conn:
		cur = conn.cursor()
		cur.execute("DELETE FROM posts WHERE postId=?",[pid])	
		cur.close()

		cur = conn.cursor()
		cur.execute("DELETE FROM comments WHERE postId=?",[pid])	
		cur.close()

		cur = conn.cursor()
		cur.execute("DELETE FROM votes WHERE postId=?",[pid])	
		cur.close()

	return redirect(url_for('myposts'))



def getLoginDetails():
	if 'rollnum' not in session:
		loggedIn=False
		name=''
		return (loggedIn,name)
	else:
		with sqlite3.connect('database.db') as conn:
			cur = conn.cursor()
			loggedIn=True
			cur.execute("SELECT name FROM users WHERE rollnum='"+session['rollnum']+"'")
			name=cur.fetchone()[0]#fetchone() method gets all the row in db
		conn.close()
		return (loggedIn,name)


def is_valid(userId,password):
	con = sqlite3.connect('database.db')
	cur = con.cursor()
	cur.execute('SELECT rollnum,password FROM users')
	data = cur.fetchall()
	for row in data:
		if row[0]==userId and row[1]==password:
			return True
	return False

if __name__=='__main__':
	app.run(debug=True)

