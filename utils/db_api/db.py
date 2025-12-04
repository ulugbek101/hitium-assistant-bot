from typing import List, Dict, Union

import pymysql


class Database:
    def __init__(self, db_name, db_password, db_user, db_port, db_host) -> None:
        """
        Initializes variables for database
        """
        self.db_name = db_name
        self.db_password = db_password
        self.db_user = db_user
        self.db_port = db_port
        self.db_host = db_host

    def connect(self) -> pymysql.Connection:
        """
        Initiates connection to MySQL database
        """
        return pymysql.Connection(
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            cursorclass=pymysql.cursors.DictCursor
        )

    def execute(
            self,
            sql: str,
            params: tuple = (),
            commit: bool = False,
            fetchone: bool = False,
            fetchall: bool = False,
    ) -> Union[Dict, List, None]:
        """
        Executes SQL script
        """
        if fetchone and fetchall:
            raise ValueError("Cannot use both fetchone and fetchall at the same time.")

        data = None

        with self.connect() as database:
            with database.cursor() as cursor:
                cursor.execute(sql, params)

                if fetchone:
                    data = cursor.fetchone()

                elif fetchall:
                    data = cursor.fetchall()

                if commit:
                    database.commit()

        return data
