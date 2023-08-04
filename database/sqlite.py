import sqlite3
import pandas as pd

class Order:
    
    def __init__(self):
        pass
    
    def open(self):
        self.conn = sqlite3.connect('./jupyter/orders.sqlite')
        self.cursor = self.conn.cursor()
        
    
    def recreateTable(self):
        self.dropTable()
        self.createTable()

    
    def dropTable(self):
        self.open()
        result = self.cursor.execute("DROP TABLE IF EXISTS orders")
        self.close()
        if (result):
            return True
        else:
            return False


    def createTable(self):
        self.open()
        query = '''CREATE TABLE orders
                 (id INTEGER PRIMARY KEY,
                  ticker varchar(20) NOT NULL,
                  position varchar(10) NOT NULL,
                  startdate timestamp NOT NULL,
                  strike_price REAL NOT NULL,
                  target REAL NOT NULL,
                  stop_loss REAL NOT NULL,
                  pnl REAL,
                  enddate timestamp,
                  result varchar(5))'''
        result = self.cursor.execute(query)
        self.close()
        if (result):
            return True
        else:
            return False

    
    def placeOrder(self, ticker, startdate, strikePrice, stoploss, target):
        self.open()
        position = 'LONG' if target > strikePrice else 'SHORT'

        query = '''INSERT INTO orders (
            ticker, 
            position, 
            startdate, 
            strike_price, 
            target, 
            stop_loss) VALUES (?, ?, ?, ?, ?, ?)'''
        values = (ticker, position, startdate, strikePrice, target, stoploss)

        result = self.cursor.execute(query, values)
        self.close()
        if (result):
            return True
        else:
            return False

    
    def closeOrder(self, id, pnl, enddate):
        self.open()
        result = 'W' if pnl > 0 else 'L'
        query = "UPDATE orders SET pnl = ?, result = ?, enddate = ? WHERE id = ?"
        data = (pnl, result, enddate, id)
        result = self.cursor.execute(query, data)
        self.close()
        if (result):
            return True
        else:
            return False

    
    def delete(self, id):
        self.open()
        query = "DELETE from orders where id = ?"
        result = self.cursor.execute(query, (id))
        self.close()
        if (result):
            return True
        else:
            return False


    def getOpenPositions(self):
        self.open()
        query = "SELECT * FROM orders WHERE result IS NULL"
        df = pd.read_sql_query(query, self.conn)
        self.close()
        return df


    def getClosedPositions(self):
        self.open()
        query = "SELECT * FROM orders WHERE result IS NOT NULL"
        df = pd.read_sql_query(query, self.conn)
        self.close()
        return df
    

    def read(self, query):
        self.open()
        df = pd.read_sql_query(query, self.conn)
        self.close()
        return df
    

    def close(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()