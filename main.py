from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = ?", (session['email'], ))
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM cart WHERE userId = ?", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

def getSellerStatus():
    if 'email' not in session:
        sellerStatus = 0
    else:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, sellerId FROM users WHERE email = ?", (session['email'], ))
            userId, sellerId= cur.fetchone()
            if sellerId > 0:
                sellerStatus = 1
            else:
                sellerStatus = 0
        conn.close()
    return sellerStatus

# def getProductDetails():
#     with sqlite3.connect('database.db') as conn:
#         cur = conn.cursor()
#         if 'email' not in session:
#             loggedIn = False

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

# Routing and API

@app.route("/")
def root():
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    query = request.args.get('searchQuery')
    if query is None:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            if loggedIn:
                cur.execute("SELECT sellerId FROM users WHERE email = ?", (session['email'], ))
                sellerId = cur.fetchone()[0]
                cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE sellerId != ?', (sellerId,))
                itemData = cur.fetchall()
            else:
                cur.execute('SELECT productId, name, price, description, image, stock FROM products')
                itemData = cur.fetchall()
            cur.execute('SELECT categoryId, name FROM categories')
            categoryData = cur.fetchall()
        itemData = parse(itemData)   
        return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, sellerStatus=sellerStatus)
    else:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            if loggedIn:
                cur.execute("SELECT sellerId FROM users WHERE email = ?", (session['email'], ))
                sellerId = cur.fetchone()[0]
                cur.execute("SELECT productId, name, price, description, image, stock FROM products WHERE name LIKE ? AND sellerId = ?", ('%' + query + '%', sellerId))
                itemData = cur.fetchall()
            else:
                cur.execute("SELECT productId, name, price, description, image, stock FROM products WHERE name LIKE ?", ('%' + query + '%', ))
                itemData = cur.fetchall()
            cur.execute('SELECT categoryId, name FROM categories')
            categoryData = cur.fetchall()
        itemData = parse(itemData)   
        return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData, query=query, sellerStatus=sellerStatus)

@app.route("/registrationForm")
def registrationForm():
    with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT addressBuilding FROM address')
            collegeBuildingData = cur.fetchall()
    return render_template("register.html", collegeBuildingData=collegeBuildingData)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        addressBuilding = request.form['address1']
        phone = request.form['phone']
        weChatId = request.form['weChatId']
        seller = 1 if 'seller' in request.form else 0
        if seller == 1:
            weChatPayCodeImg = request.files['payCodeImage']
            if weChatPayCodeImg and allowed_file(weChatPayCodeImg.filename):
                filename = secure_filename(weChatPayCodeImg.filename)
                weChatPayCodeImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagename = filename

        with sqlite3.connect('database.db') as con:
            try:
                if seller:                       
                    cur = con.cursor()
                    cur.execute('INSERT INTO seller (weChatPayCode) VALUES (?)', (imagename,))
                    cur.execute('SELECT * FROM seller ORDER BY sellerId DESC LIMIT 1')
                    sellerId = cur.fetchone()
                    cur.execute('INSERT INTO users (password, email, firstName, lastName, addressBuilding, phone, weChatId, sellerId) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, addressBuilding, phone, weChatId, sellerId[0]))
                    con.commit()

                    msg = "Registered Successfully"
                else:
                    cur = con.cursor()
                    cur.execute('INSERT INTO users (password, email, firstName, lastName, addressBuilding, phone, weChatId) VALUES (?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, addressBuilding, phone, weChatId))
                    con.commit()
                    msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

@app.route("/add")
def admin():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT sellerId FROM users WHERE email = ?", (session['email'], ))
            sellerId = cur.fetchone()[0]
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId, sellerId) VALUES (?, ?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId, sellerId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/account/products")
def addProduct():
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT sellerId FROM users WHERE email = ?", (session['email'], ))
        sellerId = cur.fetchone()[0]

    query = request.args.get('searchQuery')
    if query is None:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE sellerId = ?', (sellerId,))
            itemData = cur.fetchall()
        itemData = parse(itemData)   
        return render_template('your_products.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, sellerStatus=sellerStatus)
    else:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT productId, name, price, description, image, stock FROM products WHERE name LIKE ? AND sellerId = ?", ('%' + query + '%', sellerId))
            itemData = cur.fetchall()
        itemData = parse(itemData)   
        return render_template('your_products.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, query=query, sellerStatus=sellerStatus)


@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        sellerStatus = getSellerStatus()
        categoryId = request.args.get("categoryId")
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?", (categoryId, ))
            data = cur.fetchall()
            cur.execute("SELECT name FROM categories WHERE categoryId = ?", (categoryId, ))
            categoryName = cur.fetchone()[0]
        conn.close()
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName, sellerStatus=sellerStatus)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems, sellerStatus=sellerStatus)

@app.route("/editProduct")
def editProduct():
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template("edit_product.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems, categories=categories, sellerStatus=sellerStatus)

@app.route("/updateProduct", methods=["GET", "POST"])
def updateProduct():
    if request.method == 'POST':
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT sellerId FROM users WHERE email = ?", (session['email'], ))
            sellerId = cur.fetchone()[0]
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename

        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''UPDATE products SET name = ?, price = ?, description = ?, image = ?, stock = ?, categoryId = ?, sellerId = ?''', (name, price, description, imagename, stock, categoryId, sellerId))
                conn.commit()
                msg="edited successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT sellerId FROM users WHERE email = ?", (session['email'], ))
        sellerId = cur.fetchone()[0]
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE sellerId = ?', (sellerId,))
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, sellerStatus=sellerStatus)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('root'))


@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, sellerStatus=sellerStatus)

@app.route("/account/profile/view")
def view():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, addressBuilding, phone, weChatId FROM users WHERE email = ?", (session['email'], ))
        profileData = cur.fetchone()
        userId = profileData[0]
        cur.execute('SELECT addressBuilding FROM address')
        collegeBuildingData = cur.fetchall()

    conn.close()
    return render_template("viewProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, collegeBuildingData=collegeBuildingData, sellerStatus=sellerStatus)


@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    sellerStatus = getSellerStatus()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, addressBuilding, phone, weChatId FROM users WHERE email = ?", (session['email'], ))
        profileData = cur.fetchone()
        userId = profileData[0]
        cur.execute('SELECT addressBuilding FROM address')
        collegeBuildingData = cur.fetchall()

    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, collegeBuildingData=collegeBuildingData, sellerStatus=sellerStatus)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'], ))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        #Parse form data    
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        addressBuilding = request.form['address1']
        phone = request.form['phone']
        weChatId = request.form['weChatId']
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, addressBuilding = ?, phone = ?, weChatId = ? WHERE email = ?', (firstName, lastName, addressBuilding, phone, weChatId, email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('editProfile'))

@app.route("/sellerForm") 
def sellerForm():
    return render_template("seller.html")

@app.route("/seller", methods = ['GET', 'POST'])
def seller():
    if request.method == 'POST':
        weChatPayCodeImg = request.files['payCodeImage']
        if weChatPayCodeImg and allowed_file(weChatPayCodeImg.filename):
            filename = secure_filename(weChatPayCodeImg.filename)
            weChatPayCodeImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        
    with sqlite3.connect('database.db') as con:
        try:                     
            cur = con.cursor()
            cur.execute('INSERT INTO seller (weChatPayCode) VALUES (?)', (imagename,))
            cur.execute('SELECT * FROM seller ORDER BY sellerId DESC LIMIT 1')
            sellerId = cur.fetchone()
            cur.execute('INSERT INTO users (sellerId) VALUES (?)', (sellerId[0],))
            con.commit()

            msg = "Registered Successfully"
        except:
            con.rollback()
            msg = "Error Occured"
    con.close()
    return render_template("profileHome.html", error = msg)



if __name__ == '__main__':
    app.run(debug=True)