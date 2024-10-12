from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from deutsche_bahn_api.api_authentication import ApiAuthentication
from deutsche_bahn_api.station_helper import StationHelper
from deutsche_bahn_api.timetable_helper import TimetableHelper

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

class SearchForm(FlaskForm):
    station_name = StringField('Station Name', validators=[DataRequired()])
    submit = SubmitField('Search')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        api = ApiAuthentication("1dce76c7798e66b4a324360281c3fca7", "45341ce84c462ebd3ad4cd1a1781223e")
        success: bool = api.test_credentials()

        station_helper = StationHelper()
        station_helper.load_stations()
        name = form.station_name.data
        found_stations = station_helper.find_stations_by_name(name)
        
        # Check if found_stations has elements
        if found_stations:
            timetable_helper = TimetableHelper(found_stations[0], api)
            trains = timetable_helper.get_timetable(21)
            trains_with_changes = timetable_helper.get_timetable_changes(trains)
            
            train_data = []
            for train in trains_with_changes:
                train_info = {}
                if hasattr(train, 'train_number'):
                    train_info['train_number'] = train.train_number
                if hasattr(train, 'departure'):
                    train_info['departure'] = train.departure
                if hasattr(train, 'arrival'):
                    train_info['arrival'] = train.arrival
                if hasattr(train, 'stations'):
                    train_info['stations'] = train.stations.split('|')
                if hasattr(train, 'train_changes'):
                    train_info['changes'] = train.train_changes.messages
                
                train_data.append(train_info)
            
            return render_template('timetable.html', form=form, train_data=train_data)
        else:
            flash('No stations found matching the given name.', 'error')
            return redirect(url_for('search'))
    
    return render_template('search.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)