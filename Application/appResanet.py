#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet


app = Flask( __name__ )
app.secret_key = 'resanet'


@app.route( '/' , methods = [ 'GET' ] )
def index() :
	return render_template( 'vueAccueil.html' )

@app.route( '/usager/session/choisir' , methods = [ 'GET' ] )
def choisirSessionUsager() :
	return render_template( 'vueConnexionUsager.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect( '/usager/reservations/lister' )
				
			else :
				return render_template('vueConnexionUsager.html', carteBloquee = True , echecConnexion = False , saisieIncomplete = False )
		else :
			return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)


@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations():
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )

	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )

	solde = '%.2f' % ( soldeCarte , )

	aujourdhui = datesResanet.getDateAujourdhuiISO()

	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	dates = []
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )
		
		if uneDateISO <= aujourdhui :
			uneDate[ 'verrouillee' ] = True
		else :
			uneDate[ 'verrouillee' ] = False

		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
		else :
			uneDate[ 'reservee' ] = False
			
		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True
			
			
		dates.append( uneDate )
	
	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False

	jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi"]

	return render_template( 'vueListeReservations.html' , laSession = session , leSolde = solde , lesDates = dates , soldeInsuffisant = soldeInsuffisant , jours = jours)


	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )


@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire() :
	return render_template('vueConnexionGestionnaire.html')

@app.route( '/gestionnaire/seConnecter' , methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	login = request.form['login']
	mdp = request.form['mdp']

	if login != '' and mdp != '':
		gestionnaire = modeleResanet.seConnecterGestionnaire(login, mdp)
		if len(gestionnaire) != 0:
			session['nom'] = gestionnaire['nom']
			session['prenom'] = gestionnaire['prenom']
			session['mdp'] = mdp

			return render_template('vueEnteteGestionnaire.html')

		else:
			return render_template('vueConnexionGestionnaire.html', echecConnexion=True, saisieIncomplete=False)

	else:
		return render_template('vueConnexionGestionnaire.html', echecConnexion=False, saisieIncomplete=True)


@app.route( '/gestionnaire/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterGestionnaire() :
	session.pop( 'mdp' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/gestionnaire/personnel/lister/avecCarte' , methods = [ 'GET' ] )
def listerPersonnelAvecCarte() :

	personnels = modeleResanet.getPersonnelsAvecCarte()

	return render_template('vuePersonnelAvecCarte.html' , personnels = personnels , nbPersonnels = len(personnels) )


@app.route( '/gestionnaire/personnel/lister/sansCarte' , methods = [ 'GET' ] )
def listerPersonnelSansCarte() :

	personnels = modeleResanet.getPersonnelsSansCarte()

	return render_template('vuePersonnelSansCarte.html' , personnels = personnels , nbPersonnels = len(personnels) )


@app.route( '/gestionnaire/personnel/carte/bloquer/<numeroCarte>' , methods = [ 'GET' ] )
def bloquerCarte(numeroCarte):

	bloquer = modeleResanet.bloquerCarte(numeroCarte)

	return redirect('/gestionnaire/personnel/lister/avecCarte')


@app.route( '/gestionnaire/personnel/carte/activer/<numeroCarte>' , methods = [ 'GET' ] )
def activerCarte(numeroCarte):

	activer = modeleResanet.activerCarte(numeroCarte)

	return redirect('/gestionnaire/personnel/lister/avecCarte')



@app.route( '/gestionnaire/personnel/carte/initMDP/<numeroCarte>' , methods = [ 'GET' ] )
def initMdp(numeroCarte):

	mdp = modeleResanet.reinitialiserMdp(numeroCarte)

	return redirect('/gestionnaire/personnel/lister/avecCarte')


@app.route( '/gestionnaire/personnel/sansCarte/creerCarte/<numeroCarte>' , methods = [ 'POST' ] )
def creerCarte( numeroCarte ):
	activee = False
	if request.form.get('etat') == '1':
		activee = True

	modeleResanet.creerCarte( numeroCarte , activee )

	return redirect('/gestionnaire/personnel/lister/sansCarte')

@app.route( '/gestionnaire/personnel/carte/crediter/<numeroCarte>' , methods = [ 'POST' ] )
def crediterCarte( numeroCarte ):

	somme = request.form['crediter']
	modeleResanet.crediterCarte(numeroCarte, somme)

	return redirect('/gestionnaire/personnel/lister/avecCarte')


@app.route( '/gestionnaire/getDateReservation/', methods = [ 'GET' , 'POST' ] )
def getDateReservation() :
	date = request.values.get('date')
	personnels = []
	if date != 0 :
		personnels = modeleResanet.getReservationsDate(date)
		return render_template( 'vuePersonnelReservation.html', data = personnels, request = "Date")
	else:
		return redirect('/')

@app.route( '/gestionnaire/getCarteReservation/', methods = [ 'GET' , 'POST' ] )
def getPersonnelReservation() :
	matricule = request.values.get('matricule')
	debut = request.values.get('debut')
	fin = request.values.get('fin')
	date = []
	if matricule != 0 :
		date = modeleResanet.getReservationsCarte(matricule, debut, fin)
		print(date)
		return render_template( 'vuePersonnelReservation.html', data = date, request = "Carte" )
	else:
		return redirect('/')



if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )







