import psycopg2 as p
import pandas as pd

# DATABASE_NAME = 'postgres'
# USERNAME      = 'postgres'
# PASSWORD      = 'arkana'
# HOSTNAME      = 'localhost'
# PORT          = '5432'

# DATABASE_NAME = 'customer'
# USERNAME      = 'postgres'
# PASSWORD      = 'postgres'
# HOSTNAME      = 'localhost'
# PORT          = '5432'

# def fetchdatabase():
def fetchdatabase(DATABASE_NAME='customer', USERNAME='postgres', PASSWORD='postgres', HOSTNAME='localhost', PORT='5432'):
    db = "dbname="+DATABASE_NAME+" user="+USERNAME+" password="+PASSWORD+" host="+HOSTNAME+" port="+PORT
    try:
        connection = p.connect(db)
        cursor = connection.cursor() #, t3.name, productname, qty, price \
        specificDate = 'WHERE t2."date" BETWEEN '+ "'2018-12-03'" + " AND " +"'2019-03-31'"
        query = 'SELECT t1."companyId", t2."storeId", t2."date", t4."name" AS "categoryName", t3."name" AS "productName", t1."qty", t1."price" \
                    FROM ((("pos-transaction-item" AS t1 \
                        INNER JOIN "pos-transaction" AS t2 \
                        ON t1."transactionId" = t2."id") \
                        INNER JOIN "pos-product" AS t3 \
                        ON t1."productId" = t3."id" ) \
                        INNER JOIN "pos-product-category" AS t4 \
                        ON t3."categoryId" = t4."id") ' + specificDate
        queryPrice = 'SELECT "companyId", "storeId", "name", "price" FROM "pos-product"'
        # cursor.execute(query)
        # rows = cursor.fetchall()
        df = pd.read_sql(query, connection)
        dfPrice = pd.read_sql(queryPrice, connection)
    except (Exception, p.Error) as error:
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    
    return df, dfPrice
