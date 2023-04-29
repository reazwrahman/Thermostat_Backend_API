import serial
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_required, current_user

from . import gameSetup
from .. import db
from ..models import GameDetails, SelectedSquad
from .forms import GameSetupForm, ActiveGamesForm, AddScoreCardForm, DeactivateGameForm, UpdateGameDetailsForm

# Open the serial port at the specified baudrate
#ser = serial.Serial('/dev/cu.usbmodem14101', 9600)
#ser = serial.Serial('/dev/ttyACM0',9600)

@gameSetup.route('/', methods=['GET', 'POST']) 
def displayNavigations(): 
    return render_template ('gameSetup/gameSetupHomePage.html')

@gameSetup.route('/TurnOn', methods=['GET'])  
def TurnOn():  
    try:
        data = 'G'
        ser.write(data.encode())
        flash('led turned on')  
    except Exception as e: 
         flash('failed to turn led on') 
         print(e)
    return render_template ('gameSetup/gameSetupHomePage.html')
           


@gameSetup.route('/TurnOff', methods=['GET', 'POST']) 
def TurnOff(): 
    try:
        data = 'P'
        ser.write(data.encode())
        flash('led turned off')  
    except Exception as e: 
         flash('failed to turn led off')  
         print(e)
    return render_template ('gameSetup/gameSetupHomePage.html')




@gameSetup.route('/AddScoreCard_Part2', methods=['GET', 'POST']) 
@admin_required
@login_required 
def AddScoreCard_Part2(): 
    match_id = session.get('selected_game_id') 
    game_object = GameDetails.query.filter_by(match_id=match_id).first()

    form =  AddScoreCardForm()  
    if form.validate_on_submit(): 
        game_object.scorecard_link = form.score_card_link.data   
        game_object.points_per_run = form.points_per_run.data 
        game_object.points_per_wicket = form.points_per_wicket.data
        db.session.commit()  
        flash('Additional Game Details have been successfully updated in database')  
        return redirect (url_for('gameSetup.displayNavigations'))
    
    return render_template('gameSetup/addScoreCard.html', game_title=game_object.game_title, form=form) 



@gameSetup.route('/DeactivateGame', methods=['GET', 'POST']) 
@admin_required
@login_required 
def DeactivateGame(): 
    active_games_query = GameDetails.query.filter_by(game_status = 'Active')
    active_games_all=active_games_query.all()
    
    active_games_list=[]
    for each in active_games_all: 
        active_games_list.append((each.match_id,each.game_title))
    
    form= DeactivateGameForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id = form.game_selection.data  
        game_object = GameDetails.query.filter_by(match_id = selected_game_id).first() 
        squad_objects = SelectedSquad.query.filter_by(match_id  = selected_game_id).all()

        db.session.delete(game_object) 
        for each in squad_objects: 
            db.session.delete(each)
        db.session.commit() 
        flash('Selected Game has been Deactivated')

    return render_template('gameSetup/displayActiveGames.html',form=form) 



@gameSetup.route('/UpdateGameDetails', methods=['GET', 'POST']) 
@admin_required
@login_required 
def UpdateGameDetails(): 
    active_games_query = GameDetails.query.filter_by(game_status = 'Active')
    active_games_all=active_games_query.all()
    
    active_games_list=[]
    for each in active_games_all: 
        active_games_list.append((each.match_id,each.game_title))
    
    form= UpdateGameDetailsForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id = form.game_selection.data  
        game_object = GameDetails.query.filter_by(match_id = selected_game_id).first()  
        squad_link=form.updated_squad_link.data 
        game_start_time=form.game_start_time.data

        if len(squad_link) > 5:  ## just an arbitrary value to make sure it's not an empty string
            game_object.squad_link=squad_link
            db.session.commit()  
            flash ('Link for Potential Squad has been Updated') 

        if len(game_start_time) > 5:   ## just an arbitrary value to make sure it's not an empty string
            game_object.game_start_time=game_start_time
            db.session.commit()  
            flash ('Game Start Time Updated')

    return render_template('gameSetup/updateGameDetails.html',form=form)

