from flask import Flask, redirect, flash,render_template, request, session, url_for
from models import User, List, Card, db
from datetime import datetime
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib



# create a Flask Instance
app = Flask(__name__)
# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tododb.sqlite3'

db.init_app(app)
app.app_context().push()
app.secret_key = 'straky'

@app.before_first_request
def create_db():
	db.create_all(app=app)
	

@app.route("/", methods=['GET', 'POST'])
def register():
	if request.method == 'POST': 
		name = request.form.get('Name')
		user_name = request.form.get('User_name')
		password = request.form.get('Password')
		user = User.query.filter_by(user_name=user_name).first()
		if not user:
			new_user = User(user_name=user_name, name=name, password=password)
			db.session.add(new_user)
			db.session.commit()
			flash('New account created!')
			return redirect(url_for('login'))
		else:
			flash('This User_name already exists.Create a new one.', category='error')
			return render_template('signup.html')
	return render_template('signup.html')
  
@app.route("/login", methods=['GET', 'POST'])
def login(): 
	if request.method == 'POST': 
		user_name = request.form.get('user_name')
		password = request.form.get('pswd')       
		user = User.query.filter_by(user_name=user_name, password=password).first()
		if not user: 
			flash('Incorrect User_name/Password, please try again.', category='error')
			return render_template('login.html')
		else:
			return redirect(url_for('index',uid=user.uid))
	return render_template('login.html')


@app.route("/index/<int:uid>")
def index(uid): 
	lists = List.query.filter_by(user_id = uid).all()
	user = User.query.filter_by(uid=uid).first()
	d={}
	for each in lists:
		d[each.list_name]= []
		cards=Card.query.filter_by(list_id=each.lid).all()
		for c in cards:
			d[each.list_name].append({"cid":c.cid,"card_title":c.card_title,"content":c.content,"deadline":c.deadline,"flag":c.flag})
	return render_template('index.html', get_cards = d,uid = uid,name = user.name)

@app.route("/<int:uid>/create_list", methods=["GET", "POST"])
def createnewlist(uid): 
	userlist = List.query.filter_by(user_id=uid).all()
	if request.method == "GET":
		return render_template('create-list.html',uid = uid)

	elif request.method == "POST":
		l_name = request.form['Lname']
		l_desc = request.form['desc']
		found = False
		for l in userlist:
			found = (l.list_name==l_name)
		if not found:
			createlist = List(list_name=l_name, description=l_desc,user_id = uid)
			db.session.add(createlist)
			db.session.commit()
			flash('New List Created')
			return redirect(url_for('index',uid=uid))
		else:
			flash('This list name already exist,try using something different!',category='error')
			return render_template('create-list.html',uid=uid)

@app.route("/<int:uid>/<string:lname>/editlist", methods=["GET", "POST"])
def edit_list(uid,lname): 
	ulist=List.query.filter_by(user_id=uid).all()
	for l in ulist:
		if (l.list_name==lname):
			y = l
	if request.method == "GET":
		return render_template('list_edit.html', y=y)
	elif request.method == "POST":
		lname = request.form['l_name']
		description = request.form['desc']
		List.query.filter_by(lid=y.lid).update({'list_name':lname, 'description': description})
		db.session.commit()
		flash('List Edited!')
		return redirect(url_for('index',uid = y.user_id))
		

@app.route("/<int:uid>/<string:lname>/deletelist")
def listdetail(uid,lname): 
	ulist=List.query.filter_by(user_id=uid).all()
	for l in ulist:
		if (l.list_name==lname):
			y = l
	l={}
	cards=Card.query.filter_by(list_id=y.lid).all()
	for c in cards:
		l[c] = []
		l[c].append({"cid":c.cid,"card_title":c.card_title,"content":c.content,"deadline":c.deadline,"flag":c.flag})
		
	return render_template('listdetail.html',d=l,uid = y.user_id,list_id = y.lid)

@app.route("/<int:card_id>/<int:uid>/shiftcard", methods=["GET", "POST"])
def shiftcard(card_id,uid):
	card = Card.query.filter_by(cid = card_id).first()
	curlist=List.query.filter_by(lid=card.list_id).first()
	lname = curlist.list_name
	clist = List.query.filter_by(user_id = uid).all()
	if request.method=="GET":
		return render_template("shiftcard.html",x = card, clist = clist,uid=uid,lname =lname)
	else :  
		list_id = request.form["list"]  
		Card.query.filter_by(cid=card.cid).update({'list_id':list_id})
		db.session.commit()
		flash('Card Shifted!')
		return redirect(url_for('listdetail',lname = lname,uid=uid))
		
@app.route("/<int:list_id>/<int:user_id>/delete_list")
def delete_entirelist(list_id,user_id):
	curlist=List.query.filter_by(lid=list_id).first()
	cards=Card.query.filter_by(list_id=curlist.lid).all()
	lname = curlist.list_name
	for card in cards: 
            db.session.delete(card)
	db.session.delete(curlist)
	db.session.commit()
	flash('List with its cards is deleted!')
	return redirect(url_for('index',uid=user_id))
	
	
@app.route("/<int:uid>/<string:lname>/newcard",methods=["GET","POST"])
def create_card(uid,lname):

	get_list = List.query.filter_by(user_id = uid).all()
	
	if request.method=="GET":
        	return render_template("create-card.html",uid=uid,get_list=get_list)
	else:
		list_id = request.form["list"]
		title = request.form["Title"]
		content = request.form["Content"]
		deadline = request.form["Deadline"]
		#date_time_str = deadline
		flag = request.form["Flag"]
		created=datetime.now()
		card = Card(card_title=title,content=content,card_created = created,deadline=deadline,list_id=list_id,flag=flag)
		db.session.add(card)
		db.session.commit()
		flash('New Card Created!')
		return redirect(url_for('index',uid=uid))



@app.route("/<int:cid>/<int:uid>/updatecard", methods=["GET", "POST"])
def edit_card(cid,uid):
	card = Card.query.filter_by(cid = cid).first()
	card_list = List.query.filter_by(user_id = uid).all()
	if request.method=="GET":
		return render_template("card_edit.html",c = card, clist = card_list,uid=uid)
	else :  
		list_id = request.form["list"]  
		title = request.form['Title']
		content = request.form['Content']
		deadline = request.form["Deadline"]
		flag = request.form["Flag"]

		Card.query.filter_by(cid=card.cid).update({'card_title':title, 'content' : content,'deadline' : deadline,'list_id' : list_id,'flag' : flag})
		db.session.commit()
		flash('Card Edited!')
		return redirect(url_for('index',uid=uid))
		
		
@app.route("/<int:cid>/<int:uid>/deletecard", methods=["GET"])
def delete_card(cid,uid):
	c = Card.query.filter_by(cid=cid).first()
	db.session.delete(c)
	db.session.commit()
	flash('Card Deleted!')
	return redirect(url_for('index',uid=uid))
       
@app.route("/summary/<int:uid>")
def Summary(uid):
	plotlist={}
	lists = List.query.filter_by(user_id=uid).all()
	for l in lists:
		plotlist[l.list_name]=[]		
		comp,incomp,deadpass=0,0,0
		cards=Card.query.filter_by(list_id=l.lid).all()
		for c in cards:

			if c.flag == "on" :
				comp+=1
			else:
				incomp+=1
			today=datetime.today()
			deadl = datetime.strptime(c.deadline, "%Y-%m-%d").strftime("%Y-%m-%d")
			newdate1 = datetime.strptime(deadl,"%Y-%m-%d")
			if newdate1 < today:
				deadpass+=1	
		x  = ["completed","not completed","deadline passed"]
		y= [comp,incomp,deadpass]
		plotlist[l.list_name].append({"Completed":comp,"Incompleted":incomp,"deadline":deadpass})		
		fig = CreateFigure(x, y)
		fig.savefig('static/imgs/'+l.list_name+'.png')

	return render_template('summary.html',uid = uid,plotlist = plotlist)

				
def CreateFigure(x, y):
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.bar(x, y)
	return fig		


		

if __name__ == "__main__":
    # run the flask app
    app.run(host='0.0.0.0', debug=True, port=5000) # running on localhost/0.0.0.0/127.0.0.1 having port 5000 with debugging



@app.route("/logout", methods=['GET'])
def logout(): 
    flash('Logged out!')    
    return redirect(url_for(login))
   
