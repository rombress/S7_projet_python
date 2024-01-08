# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 13:39:42 2023

@author: Romain BRESSY
"""

from flask import Flask, render_template, request, redirect, url_for
from flask import session, jsonify
import action2 as a
import random, os
import sqlite3

app = Flask(__name__)

# Variable de contexte pour indiquer l'état de l'authentification
app.config['USER_AUTHENTICATED'] = False
app.secret_key = "tp"


# Variable pour le stockage des images
UPLOAD_FOLDER = "./static/uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route("/home")
def home():
    return render_template("layout.html", user_authenticated=app.config['USER_AUTHENTICATED'])

@app.route("/register", methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
    
        user = a.User(username, password)

        
        if user.ExistUser():
            
            #Si l'user' existe déjà, on renvoi la page avec une erreur
            return render_template("register.html", error=True, user_authenticated=app.config['USER_AUTHENTICATED'])
        else: 
            
            # Ajoutez l'user' à la base de données en utilisant la méthode AddCaveBDD
            user.AddUserBDD()

       
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    db = sqlite3.connect("Vin2.db")
    curseur = db.cursor()
    if request.method == 'POST':
        # Récupérer les informations du formulaire
        username = request.form['username']
        password = request.form['password']


        user_query = f"SELECT * FROM User WHERE username = '{username}' AND password = '{password}';"
        curseur.execute(user_query)
        result = curseur.fetchone()
      
        # Vérifier les identifiants
        if result:

           # Si les identifiants sont corrects, redirigez vers la page de connexion réussie
           User = a.User(username, password )
           # On enregiste l'objet user sous la forme d'un dictionnaire afin de l'utiliser dans toutes les fonctions
           session['user'] = User.__dict__
           app.config['USER_AUTHENTICATED'] = result[0]
           return redirect(url_for('connexion_reussie'))
    # Si les identifiants sont incorrects, afficher le formulaire de connexion
    db.commit()
    db.close()
    return render_template('login2.html')

@app.route("/touteslesbouteilles")
def touteslesbouteilles():
    
    # Récupération du filtre et de l'argument
    search_query = request.args.get('search', '')
    search_criteria = request.args.get('criteria', 'nom')  # La valeur par défaut est 'nom'

    db = sqlite3.connect("Vin2.db")
    cursor = db.cursor()

    # Si on détecte un envoi du formulaire, on filtre la séléction des bouteilles sinon on affiche tout
    if search_query:
        query = f"SELECT * FROM Bouteille WHERE {search_criteria} LIKE ?"
        cursor.execute(query, ('%'+search_query+'%',))
    else:
        cursor.execute("SELECT * FROM Bouteille")

    bouteilles = cursor.fetchall()
    db.close()
    
    return render_template("touteslesbouteilles.html", user_authenticated=app.config['USER_AUTHENTICATED'], bouteilles=bouteilles)


@app.route('/connexion_reussie')
def connexion_reussie():

    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    # On utilise cette méthode pour récupérer toutes les caves de l'user
    caves = user2.listCave()
    
    return render_template('home2.html', caves=caves, user_authenticated=app.config['USER_AUTHENTICATED'])

@app.route('/cave/<cave_id>')
def cave(cave_id):
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    # On crée une cave intermédiaire afin d'utiliser la méthode qui renvoi la liste des étagères de la cave
    cave_intermediaire = a.Cave(user2.username, cave_id)   
    etageres = cave_intermediaire.listEtagere()
    
    return render_template('liste_etagere.html', cave_id=cave_id, etageres=etageres, user_authenticated=app.config['USER_AUTHENTICATED'])

@app.route('/cave/<cave_id>/etagere/<etagere_id>')
def etagere(cave_id, etagere_id):
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    # On crée une étagère intermédiaire afin d'utiliser la méthode qui renvoi la liste des bouteilles de l'étagère'
    etagere_intermediaire = a.Etagere(user2.username, cave_id, etagere_id, "", 0)
    bouteilles = etagere_intermediaire.listBouteille()
    
    return render_template('liste_bouteille.html', bouteilles=bouteilles, user_authenticated=app.config['USER_AUTHENTICATED'], cave_id=cave_id, etagere_id=etagere_id)


@app.route("/ajouterCave", methods=['GET', 'POST'])
def ajouterCave():
    if request.method == 'POST':
        
        # Si la méthode est POST, traitez le formulaire soumis
        nomC = request.form['nomC']

        # Créez une instance de la classe Cave
        cave = a.Cave(app.config['USER_AUTHENTICATED'], nomC)

        # On teste si le nom de la Cave est bien unique
        if cave.ExistCave():
            
            #Si la cave existe déjà, on renvoi la page avec une erreur
            return render_template("ajouterCave.html", error=True, user_authenticated=app.config['USER_AUTHENTICATED'])
        else: 
            
            # Ajoutez la cave à la base de données en utilisant la méthode AddCaveBDD
            cave.AddCaveBDD()

        return redirect(url_for('connexion_reussie'))
    
    return render_template("ajouterCave.html", user_authenticated=app.config['USER_AUTHENTICATED'])

@app.route("/ajouterEtagere", methods=['GET', 'POST'])
def ajouterEtagere():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    # On liste toutes les caves de l'user afin de les proposer dans le formulaire 
    caves = user2.listCave()
    
    if request.method == 'POST':
        
        # Récupérez les données du formulaire
        nomC = request.form.get('cave')
        numero_etagere = request.form.get('numero')
        region_etagere = request.form.get('region')
        place_dispo_etagere = request.form.get('placeDispo')
        
        # Utilisez ces données pour créer un objet Etagere
        etagere = a.Etagere(
            username= user2.username,
            nomC= nomC,
            numero= numero_etagere,
            region= region_etagere,
            placeDispo= place_dispo_etagere)
        
        # On teste si l'étagère est unique
        if etagere.ExistEtagere():
            
            # Si elle existe, on renvoi la page avec une erreur
            return render_template("ajouterEtagere.html", error=True, caves=caves, user_authenticated=app.config['USER_AUTHENTICATED'])
        else :
            
            # On appelle la méthode pour ajouter l'étagère dans la BDD
            etagere.AddEtagereBDD()
            
    return render_template("ajouterEtagere.html", caves=caves, user_authenticated=app.config['USER_AUTHENTICATED'])


@app.route("/ajouterBouteille1", methods=['GET', 'POST'])
def ajouterBouteille1():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    # On liste toutes les caves de l'user afin de les proposer dans le formulaire 
    caves = user2.listCave()
    
    if request.method == 'POST':
        
        cave_choisie = request.form['cave']
        # Rediriger vers la page de formulaire avec l'ID de la cave sélectionnée
        return redirect(url_for('ajouterBouteille2', cave_id=cave_choisie))
    
    return render_template("ajouterBouteille1.html", caves=caves, user_authenticated=app.config['USER_AUTHENTICATED'])
    
    
@app.route("/ajouterBouteille2/<cave_id>", methods=['GET', 'POST'])
def ajouterBouteille2(cave_id):
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    # On crée une cave intermédiaire afin de lister les étagères de la cave choisi 
    cave_intermediaire = a.Cave(user2.username, cave_id)  
    etageres = cave_intermediaire.listEtagere()
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        numeroEtagere = request.form['etagere']
        nomB = request.form['nom']
        domaine = request.form['domaine'] 
        type_bouteille = request.form['type']
        annee = request.form['annee']
        region = request.form['region']
        notePerso = request.form['noteperso']
        prix = request.form['prix']
        
        # On prend un nombre random qui servira de nom pour le stockage de l'image
        nombre=random.randint(0,999999999999)
        
        # Obtient le fichier téléchargé depuis la requête
        uploaded_img = request.files['file']
        
        # Vérifie si le nom du fichier est valide (évite les injections)
        if uploaded_img.filename != '':
            # Déplace le fichier téléchargé dans le dossier UPLOAD_FOLDER
            img_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{nombre}.jpg")
            uploaded_img.save(img_filename)
       

        # Créer un objet Bouteille
        nouvelle_bouteille = a.Bouteille( domaine, nomB, type_bouteille, annee, region, notePerso, prix, f"{nombre}.jpg")
                                         
        # Ajouter à la base de données
        username = user2.username
        if nouvelle_bouteille.AddBouteilleBDD(numeroEtagere, cave_id, username) :

            return redirect(url_for('connexion_reussie'))
        
        else :
            return render_template("ajouterBouteille2.html", etageres=etageres, cave_id=cave_id, user_authenticated=app.config['USER_AUTHENTICATED'], error=True)
            
            
    return render_template("ajouterBouteille2.html", etageres=etageres, cave_id=cave_id, user_authenticated=app.config['USER_AUTHENTICATED'])
    
@app.route("/archive", methods=['GET', 'POST'])
def archive():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    # On liste les bouteilles archivé de l'utilisateur avec cette méthode
    bouteilles = user2.listArchive()
    
    if request.method == 'POST':
        
        id_B = request.form['bouteille_id']
        cave_id = request.form['cave_id']
        etagere_id = request.form['etagere_id']
        
        # On crée une bouteille intermédiaire pour applique la méthode qui déarchive une bouteille
        bouteille_intermediaire = a.Bouteille("", "", "", 0, "", 0, 0, "")
        
        # On test si il reste de la place dans l'étagère qui est censé contenir la bouteille
        if bouteille_intermediaire.DesarchiverBouteille( id_B, etagere_id, cave_id, user2.username) :
            return redirect(url_for('connexion_reussie'))
        
        else : 
            return render_template("archive.html", Error=True, user_authenticated=app.config['USER_AUTHENTICATED'], bouteilles=bouteilles)

   
    return render_template("archive.html", user_authenticated=app.config['USER_AUTHENTICATED'], bouteilles=bouteilles)

@app.route("/logout")
def logout():
    # Réinitialiser l'état de l'authentification à False lors de la déconnexion
    app.config['USER_AUTHENTICATED'] = False
    return redirect(url_for('home'))

@app.route('/get-region', methods=['GET'])
def get_region():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    user_id = user2.username
    etagere_id = request.args.get('etagereId')
    cave_id = request.args.get('caveId')
    region = ""
    
    # On crée une étagère afin d'appliquer la méthode qui récupère sa région 
    etagere_intermediaire = a.Etagere(user_id, cave_id, etagere_id, region, 0)
    region = etagere_intermediaire.GetRegion()
    
    return jsonify({'region': region})

@app.route('/supprimer_bouteille', methods=['POST'])
def supprimer_bouteille():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    bouteille_id = request.form['bouteille_id']
    cave_id = request.form['cave_id']
    etagere_id = request.form['etagere_id']
    
    # On crée une bouteille pour appliquer la méthode qui la supprime de la BDD
    bouteille_intermediaire = a.Bouteille("", "", "", 0, "", 0, 0, "")
    bouteille_intermediaire.DeleteBouteille( bouteille_id, etagere_id, cave_id, user2.username)
    
    return redirect(url_for('connexion_reussie'))

@app.route('/supprimer_etagere', methods=['POST'])
def supprimer_etagere():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    cave_id = request.form['cave_id']
    etagere_id = request.form['etagere_id']
    
    # On crée une étagère pour appliquer la méthode qui la supprime (ainsi que les bouteilles attachées) de la BDD
    etagere_intermediaire = a.Etagere(user2.username, cave_id, etagere_id, "", 0)
    etagere_intermediaire.DeleteEtagere()
    
    return redirect(url_for('connexion_reussie'))

@app.route('/supprimer_cave', methods=['POST'])
def supprimer_cave():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    cave_id = request.form['cave_id']

    # On crée une cave pour appliquer la méthode qui la supprime (ainsi que les étagère/sbouteilles attachées) de la BDD
    cave_intermediaire = a.Cave(user2.username, cave_id)
    cave_intermediaire.DeleteCave()
    
    return redirect(url_for('connexion_reussie'))

@app.route('/archiver_bouteille', methods=['POST'])
def archiver_bouteille():
    
    # On recrée l'objet User de l'utilisateur connecté
    user1 = session.get('user')
    user2 = a.User(**user1)
    
    id_B = request.form['bouteille_id']
    note_archive = request.form['note_archive']
    cave_id = request.form['cave_id']
    etagere_id = request.form['etagere_id']
    
    # On crée une bouteilles pour appliquer la méthode qui l'archive

    bouteille_intermediaire = a.Bouteille("", "", "", 0, "", 0, 0, "")
    bouteille_intermediaire.ArchiverBouteille( id_B, etagere_id, cave_id, user2.username, note_archive)
    
    return redirect(url_for('connexion_reussie'))



app.run(debug=True)