import sys
from pathlib import Path

parent = Path(__file__).parents[1]
sys.path.append(str(parent))

import psycopg2
from psycopg2 import errorcodes, ProgrammingError
from gen_util.error_type import ErrorType


class DBResType:
    def __init__(self):
        self.status = None
        self.response = None
        self.errors = None

class RunQuery:
    def __init__(self):
        pass

    def run_query(self, query, tuple_=None):
        from decouple import config
        import boto3

        # DBNAME = config('DB')
        # USER = config('DB_USER')
        # HOST = config('DB_HOST')
        # PASSWORD = config('DB_PASSWORD')
        # input_str = "dbname={} user={} host={} password={}".format(DBNAME, USER, HOST, PASSWORD)
        # conn = psycopg2.connect(input_str)
        
        ENDPOINT = config('AWS_ENDPOINT')
        PORT = config('AWS_PORT')
        USER = config('AWS_USER')
        REGION = config('AWS_REGION')
        DBNAME = config('AWS_DBNAME')
        PASSWORD = config('AWS_PASSWORD')

        client = boto3.client("rds")
        token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)

        res = DBResType()
        cur = conn.cursor()

        try:
            if tuple_:
                cur.execute(query, tuple_)
            else:
                cur.execute(query)

            response = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()

            res.response = response
            res.status = 200

        except ProgrammingError:
            err_type, err_val, traceback = sys.exc_info()
            conn = None
            print(err_val)

        except TypeError as err:
            res.errors = [self.print_error(query, err)]
            res.status = 400

        return res

    def print_error(self, query, err_mess):
        field = query
        message = err_mess
        err = ErrorType(field=field, message=message)

        return err
