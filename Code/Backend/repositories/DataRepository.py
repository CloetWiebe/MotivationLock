from .Database import Database

class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_avg_temp():
        sql="SELECT TRUNCATE(AVG(Waarde),2) AS `Gemiddelde`  FROM Historiek WHERE Actiedatum BETWEEN DATE_SUB(NOW(), INTERVAL 1 MINUTE) AND NOW() AND ActieID = 'GetTemp'"
        return Database.get_one_row(sql)
    
    @staticmethod
    def read_avg_hearrate():
        sql="SELECT TRUNCATE(AVG(Waarde),2) AS `Gemiddelde`  FROM Historiek WHERE Actiedatum BETWEEN DATE_SUB(NOW(), INTERVAL 1 MINUTE) AND NOW() AND ActieID = 'GetHeartrate'"
        return Database.get_one_row(sql)

    @staticmethod
    def read_moved():
        sql="SELECT Waarde FROM Historiek Where DeviceId = 'MovedSens' ORDER BY HistoriekId DESC LIMIT 1;"
        return Database.get_one_row(sql)
    
    @staticmethod
    def insert_hearrate(value):
        sql="INSERT INTO Historiek (DeviceId, ActieId,Waarde) VALUES('HeartSens', 'GetHeartrate', %s)"
        params=[value]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_moved(value):
        sql = "INSERT INTO Historiek (DeviceId, ActieId, Waarde) VALUES ('MovedSens', 'GetMoved', %s)"
        params = [value]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def insert_temp(value):
        sql = "INSERT INTO Historiek (DeviceId, ActieId,Waarde) VALUES('TempSens', 'GetTemp', %s)"
        params = [value]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_cal(value):
        sql = "INSERT INTO Historiek (DeviceId, ActieId,Waarde) VALUES('RaspCalBurned', 'InsertBurnedCal', %s)"
        params = [value]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def get_total_cal_by_day():
        sql = "SELECT Round(Sum(Waarde), 2) AS `Totaal`, concat(day(actiedatum), '/', month(actiedatum)) as `Datum`, dayname(actiedatum) as `Dag` FROM Historiek WHERE DeviceId = 'RaspCalBurned' GROUP BY day(actiedatum)LIMIT 7;"
        return Database.get_rows(sql)

    @staticmethod
    def insert_color(value):
        sql = "INSERT INTO Historiek (DeviceId, ActieId, Waarde) VALUES ('LightsAc', 'ShowprogressLed', %s);"
        params = [value]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def get_recent_color():
        sql= "SELECT Waarde FROM Historiek WHERE DeviceId = 'LightsAc' ORDER BY HistoriekId DESC LIMIT 1;"
        return Database.get_one_row(sql)

    @staticmethod
    def insert_lock():
        sql ="INSERT INTO Historiek (DeviceId, ActieId, Waarde) VALUES ('ServoAc', 'Lockdoor', 1);"
        return Database.execute_sql(sql)

    @staticmethod
    def insert_unlock():
        sql= "INSERT INTO Historiek (DeviceId, ActieId, Waarde) VALUES ('ServoAc', 'Unlockdoor', 1);"
        return Database.execute_sql(sql)
