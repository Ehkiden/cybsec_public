from datetime import datetime

from cybsec import db
from cybsec.models import timesheet


class TS:
    # Initialize the class with arguments
    def __init__(self, userid):
        self.userid = userid

    # mainly used for updating clock in and clock out status
    def ts_action(self, sub_time):
        # query the db to get the lastest entry
        timesheet_results = timesheet.query.filter_by(user_id=self.userid).order_by(timesheet.date.desc()).first()

        # if we get nothing then the user hasnt clocked in before or if end time is filled then create a new row
        if (not timesheet_results) or (timesheet_results.end):
            timesheet_results = timesheet(user_id=self.userid, date=sub_time, start=sub_time)
            db.session.add(timesheet_results)
        # if the end time is null, then fill the column with the passed in value
        elif timesheet_results.end is None:
            timesheet_results.end = sub_time
        else:
            return False

        db.session.commit()
        return True


    # update the desired row
    def ts_update(self, request):
        # convert passed in time into a datetime obj
        start_temp = request.form['date']+' '+request.form['start']+":00"

        try:
            start_temp = datetime.strptime(start_temp, '%B %d, %Y %H:%M:%S')
        except:
            try:
                start_temp = datetime.strptime(start_temp, '%Y-%m-%d %H:%M:%S')
            except:
                return False
        
        try:
            # we can assume the start and end time will always be in %H:%M:%S
            # this should convert the string input into a datetime obj
            # row_id = request.form['row_id']
            # start_temp = request.form['date']+' '+request.form['start']+":00"
            end_temp = request.form['date']+' '+request.form['end']+":00"

            # start_temp = datetime.strptime(start_temp, '%B %d, %Y %H:%M:%S')
            end_temp = datetime.strptime(end_temp, '%B %d, %Y %H:%M:%S')
        except:
            try:
                end_temp = datetime.strptime(end_temp, '%m-%d-%Y %H:%M:%S')
            except:
                end_temp = None
        # get the comments 
        try:
            comment = request.form["comment"]
        except:
            comment = ''
            pass

        if request.form['action'] == "Update":
            row_id = request.form['row_id']
            # find by row and update fields
            ts_results = timesheet.query.filter_by(id=row_id).first()

            ts_results.start = start_temp
            ts_results.end = end_temp
            ts_results.comment = comment

        
        elif request.form['action'] == 'Add':
            ts_row = timesheet(user_id=self.userid, date=start_temp, start=start_temp, end=end_temp, comment=comment)
            db.session.add(ts_row)

        db.session.commit()
        return True

    # deletes the entry
    def ts_delete(self, request):
        row_id = request.form['row_id']
        ts_results = timesheet.query.filter_by(id=row_id).first()
        db.session.delete(ts_results)
        db.session.commit()
        return True
