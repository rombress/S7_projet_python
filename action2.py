# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 15:19:05 2023

@author: Romain BRESSY
"""

import sqlite3
import os

db = sqlite3.connect("Vin2.db")
curseur = db.cursor()

class User:

    def __init__(self, username, password):

        self.username = username
        self.password = password



    def listCave(self):
        
        db = sqlite3.connect("Vin2.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT NomC FROM Cave WHERE id_ref_u = '{self.username}'")
        cave_list = cursor.fetchall()
        db.close()

        return cave_list


    def AddUserBDD(self):
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        req = f"INSERT INTO User (username, password) VALUES ('{self.username}', '{self.password}')"
        curseur.execute(req)
        db.commit()
        db.close()
        
    def listArchive(self):
        db = sqlite3.connect("Vin2.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Bouteille WHERE archive = ? AND id_ref_u = ?", (1, self.username))
        bouteilles = cursor.fetchall()
        
        
        db.close()

        return bouteilles
    
    def ExistUser(self):
        
        # Vérifier si le numéro d'étagère existe déjà dans la base de données
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        check_query = f"SELECT * FROM User WHERE username = '{self.username}' "
        curseur.execute(check_query)
        existing_user = curseur.fetchone()
        
        curseur.close()
        db.close()
        
        if existing_user:
            return True
        else:
            return False
        
    




class Cave(User):

    def __init__(self, username, nomC):
         # Récupérer le mot de passe associé à l'utilisateur depuis la base de données
        db = sqlite3.connect("Vin2.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT password FROM User WHERE username = '{username}'")
        result = cursor.fetchone()
        db.close()

        # Vérifier si l'utilisateur existe
        if result:
            super().__init__(username, password=result[0])  # Utiliser le mot de passe récupéré
            self.nomC = nomC
        else:
            print(f"L'utilisateur {username} n'existe pas.")


    def listEtagere(self):
        
        db = sqlite3.connect("Vin2.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM Etagere WHERE id_ref_c = '{self.nomC}' AND id_ref_c_u = '{self.username}' ")
        etageres = cursor.fetchall()
        db.close()

        return etageres

    
    def ExistCave(self):
        
        # Vérifier si le numéro d'étagère existe déjà dans la base de données
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        check_query = f"SELECT * FROM Cave WHERE NomC = '{self.nomC}' AND id_ref_U = '{self.username}'"
        curseur.execute(check_query)
        existing_cave = curseur.fetchone()
        
        if existing_cave:
            return True
        else:
            return False
    
    def AddCaveBDD(self):
        
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        req = f"INSERT INTO Cave (NomC, id_ref_u) VALUES ('{self.nomC}', '{self.username}')"
        curseur.execute(req)
        db.commit()
        db.close()
    
    def DeleteCave(self):
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()

        # Suppression de la Cave
        req = "DELETE FROM Cave WHERE nomC = ? AND id_ref_u = ?"
        param = (self.nomC, self.username)
        curseur.execute(req, param)
    
        # Suppression des Etageres rattachées
        req = "DELETE FROM Etagere WHERE id_ref_c = ? AND id_ref_c_u = ?"
        param = (self.nomC, self.username)
        curseur.execute(req, param)
    
        # Suppression des Bouteilles rattachées
        req = "DELETE FROM Bouteille WHERE nomCave = ? AND id_ref_u = ?"
        param = (self.nomC, self.username)
        curseur.execute(req, param)
    
        db.commit()
        curseur.close()
        db.close()
    

class Etagere(Cave):

    def __init__(self, username, nomC, numero, region, placeDispo):
        super().__init__(username, nomC)  # Appel du constructeur de la classe dérivée
        self.numero = numero
        self.region = region
        self.placeDispo = placeDispo
        self.NbBouteille = 0


    def listBouteille(self):
        db = sqlite3.connect("Vin2.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Bouteille WHERE numeroEtagere = ? AND nomCave = ? AND id_ref_u = ? AND archive = ?", (self.numero, self.nomC, self.username, 0))
        bouteilles = cursor.fetchall()
        
        
        db.close()

        return bouteilles

    def ExistEtagere(self):
        
        # Vérifier si le numéro d'étagère existe déjà dans la base de données
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        check_query = f"SELECT * FROM Etagere WHERE numero = {self.numero} AND id_ref_C = '{self.nomC}' AND id_ref_c_u = '{self.username}'"
        curseur.execute(check_query)
        existing_etagere = curseur.fetchone()
        
        curseur.close()
        db.close()
        
        if existing_etagere:
            return True
        else:
            return False
    
    def AddEtagereBDD(self):
        
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        req = f"INSERT INTO Etagere (numero, region, placeDispo, NbBouteille, id_ref_c, id_ref_c_u) VALUES ({self.numero}, '{self.region}', {self.placeDispo}, {self.NbBouteille}, '{self.nomC}', '{self.username}')"
        curseur.execute(req)
        db.commit()
        
        curseur.close()
        db.close()
        
    def GetRegion(self):
        
        db = sqlite3.connect('Vin2.db')
        curseur = db.cursor()
        curseur.execute("SELECT region FROM Etagere WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?", (self.numero,self.nomC,self.username))
        row = curseur.fetchone()
       
        if row:
            region = row[0]
            
      
        curseur.close()
        db.close()
        
        return region
    
    def DeleteEtagere(self):
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()

        # Suppression de la table Etagere
        req_etagere = "DELETE FROM Etagere WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?"
        params_etagere = (self.numero, self.nomC, self.username)
        curseur.execute(req_etagere, params_etagere)
    
        # Suppression des bouteilles attachées
        req_bouteille = "DELETE FROM Bouteille WHERE numeroEtagere = ? AND nomCave = ? AND id_ref_u = ?"
        params_bouteille = (self.numero, self.nomC, self.username)
        curseur.execute(req_bouteille, params_bouteille)
    
        db.commit()
        curseur.close()
        db.close()


class Bouteille():

    def __init__(self, domaine, nomB, type, annee, regionB, notePerso, prix, photo):
        
    

        self.domaine = domaine
        self.nomB = nomB
        self.type = type
        self.annee = annee
        self.regionB = regionB
        self.notePerso = notePerso
        self.prix = prix
        
        self.photo = photo
        self.commentaire = []
        self.noteMoy = 1
        self.archive = 0
        self.noteArchive = ""
        
    def AddBouteilleBDD(self, numeroEtagere, nomC, username):
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()

        # Vérifier si l'étagère a de la place disponible
        curseur.execute("SELECT placeDispo FROM Etagere WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?", (numeroEtagere,nomC,username))
        place_dispo = curseur.fetchone()
        if place_dispo[0] > 0:
            
            
            
            # Insérer la bouteille
            req = f"INSERT INTO Bouteille (nom, domaine, type, annee, region, notePerso, noteMoy, photo, prix, archive, noteArchive, numeroEtagere, nomCave, id_ref_u) VALUES ('{self.nomB}', '{self.domaine}', '{self.type}', {self.annee}, '{self.regionB}', {self.notePerso}, {self.noteMoy}, '{self.photo}', {self.prix}, {self.archive}, '{self.noteArchive}', {numeroEtagere}, '{nomC}', '{username}')"
            curseur.execute(req)

            # Mettre à jour l'étagère
            curseur.execute("UPDATE Etagere SET placeDispo = placeDispo - 1, NbBouteille = NbBouteille + 1 WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?", (numeroEtagere,nomC,username))
            db.commit()
            db.close()
            
            return True
        
        else:
            
            db.commit()
            db.close()
            
            return False
        
    def DeleteBouteille(self, id_B, numeroEtagere,nomC,username):
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        
        
        
       
        
        req = f"DELETE FROM Bouteille WHERE id_B = {id_B}"
        curseur.execute(req)
            
        # Mettre à jour l'étagère
        curseur.execute("UPDATE Etagere SET placeDispo = placeDispo + 1, NbBouteille = NbBouteille - 1 WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?", (numeroEtagere,nomC,username))
       
            
        db.commit()
        db.close()
    
    def ArchiverBouteille(self, id_B, numeroEtagere,nomC,username, note_archive):
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()
        
        # Mettre à jour la bouteille
        curseur.execute("UPDATE Bouteille SET archive = 1 , noteArchive= ? WHERE id_B = ?", (note_archive, id_B))    
        # Mettre à jour l'étagère
        curseur.execute("UPDATE Etagere SET placeDispo = placeDispo + 1, NbBouteille = NbBouteille - 1 WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?", (numeroEtagere,nomC,username))
       
        db.commit()
        db.close()
    
    def DesarchiverBouteille(self, id_B, numeroEtagere,nomC,username):
        db = sqlite3.connect("Vin2.db")
        curseur = db.cursor()

        # Vérifier si l'étagère a de la place disponible
        curseur.execute("SELECT placeDispo FROM Etagere WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?", (numeroEtagere,nomC,username))
        place_dispo = curseur.fetchone()
        if place_dispo[0] > 0 :  
            # Mettre à jour la bouteille
            curseur.execute("UPDATE Bouteille SET archive = ?, noteArchive = ? WHERE id_B = ?", (0,'', id_B))    
            # Mettre à jour l'étagère
            curseur.execute("UPDATE Etagere SET placeDispo = placeDispo - 1, NbBouteille = NbBouteille + 1 WHERE numero = ? AND id_ref_c = ? AND id_ref_c_u = ?", (numeroEtagere,nomC,username))
            db.commit()
            db.close()
            return True
        else :
            db.commit()
            db.close()
            return False
    


        
      

