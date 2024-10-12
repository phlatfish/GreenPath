from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import deutsche_bahn_api
from deutsche_bahn_api import StationHelper, TimetableHelper, ApiAuthentication

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

class SearchForm(FlaskForm):
    station_name = StringField('Station Name', validators=[DataRequired()])
    submit = SubmitField('Search')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        # Simplified station search
        station_helper = StationHelper()
        stations = station_helper.find_stations_by_name(form.station_name.data)
        
        if stations:
            return redirect(url_for('timetable', station_id=stations[0].id))
        else:
            flash('Station not found.', 'error')
    
    return render_template('search.html', form=form)

@app.route('/timetable/<int:station_id>')
def timetable(station_id):
    api_auth = ApiAuthentication("1dce76c7798e66b4a324360281c3fca7", "45341ce84c462ebd3ad4cd1a1781223e")
    success = api_auth.test_credentials()
    if not success:
        flash('API authentication failed. Please check your credentials.', 'error')
        return redirect(url_for('index'))

    station_helper = StationHelper()
    station = station_helper.find_station_by_id(station_id)
    if not station:
        flash('Invalid station ID.', 'error')
        return redirect(url_for('index'))

    timetable_helper = TimetableHelper(station, api_auth)
    trains = timetable_helper.get_timetable()

    return render_template('timetable.html', trains=trains)

if __name__ == '__main__':
    app.run(debug=True)
