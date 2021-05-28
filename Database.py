from dateutil.parser import parse
from mysql.connector import connect, Error, MySQLConnection
from itertools import chain
from datetime import date

class DBManager:
    
    connection = None

    @staticmethod
    def getConnection():

        if(DBManager.connection is None):
            try:
                DBManager.connection = connect(
                                        host = "localhost",
                                        user = "hackademy",
                                        password = "Hack*21*P",
                                        database = "Presenze",
                                        charset="utf8"
                                    )
            except Error as e:
                print(e)
            
        return DBManager.connection

    @staticmethod
    def closeConnection():
        if(DBManager.connection is not None):
            DBManager.connection.close()
            DBManager.connection = None


class PresenzeDAO:

    #-----QUERIES-----

    @staticmethod
    def queryAllStudents():
        conn = DBManager.getConnection()
        stmt = "SELECT * FROM Studenti ORDER BY Nome"
        result = []
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            result = cursor.fetchall()
        return result

    @staticmethod
    def queryDate(date_in: date):
        conn = DBManager.getConnection()
        date = date_in.strftime('%Y-%m-%d')
        stmt = "SELECT Presenti FROM Giorni WHERE Giorno = DATE(%s)"
        result = []
        with conn.cursor() as cursor:
            cursor.execute(stmt, (date,))
            result = cursor.fetchall()
        return result

    @staticmethod
    def queryAvailableStudents():
        conn = DBManager.getConnection()
        stmt = "SELECT Nome, UltimaPresenza FROM Studenti WHERE Disponibilita = 'Disponibile' ORDER BY Nome"
        result = []
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            result = cursor.fetchall()
        return result

    @staticmethod
    def queryAvailableStudentsName():
        conn = DBManager.getConnection()
        stmt = "SELECT Nome FROM Studenti WHERE Disponibilita = 'Disponibile' ORDER BY Nome"
        result = []
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            result = cursor.fetchall()
        return result

    #-----INSERT-----

    @staticmethod
    def insertDate(date_in: str):
        result_query = PresenzeDAO.queryAvailableStudentsName()
        names = ", ".join(tuple(chain(*result_query)))

        conn = DBManager.getConnection()
        stmt = "INSERT INTO Giorni VALUES (DATE(%s), %s)"
        with conn.cursor() as cursor:
            cursor.execute(stmt, (date_in, names))
            conn.commit()

        stmt = "UPDATE Studenti SET UltimaPresenza = DATE('" + date_in + "'), Disponibilita = 'Non Disponibile' WHERE Nome = %s"
        with conn.cursor() as cursor:
            cursor.executemany(stmt, result_query)
            conn.commit()

    #-----UPDATE-----

    @staticmethod
    def updateAvailability(availability: str, name: str):
        conn = DBManager.getConnection()
        stmt = "UPDATE Studenti SET Disponibilita = %s WHERE Nome = %s"
        with conn.cursor() as cursor:
            cursor.execute(stmt, (availability, name))
            conn.commit()

        
        