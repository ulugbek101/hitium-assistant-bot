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

    def create_users_table(self) -> None:
        """
        Creates users table
        """
        sql = """
            CREATE TABLE IF NOT EXISTS users(
                id INT PRIMARY KEY AUTO_INCREMENT,
                telegram_id VARCHAR(255) NOT NULL UNIQUE,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                middle_name VARCHAR(50),
                phone_number VARCHAR(12),
                type_of_document VARCHAR(20),
                card_number VARCHAR(16),
                card_holder_name VARCHAR(100),
                tranzit_number VARCHAR(50),
                bank_name VARCHAR(20),
                specialization VARCHAR(255),
                id_card_photo1 VARCHAR(255),
                id_card_photo2 VARCHAR(255),
                passport_photo VARCHAR(255)
            )
        """
        self.execute(sql)

    def initial_registration(self, telegram_id: str) -> None:
        """
        Initial registration of a user
        """
        sql = """
            INSERT INTO users(telegram_id) 
            VALUES (%s)
        """
        self.execute(sql, (telegram_id,), commit=True)

    def register_user(self,
                      telegram_id: str,
                      first_name: str,
                      last_name: str,
                      middle_name: str,
                      phone_number: str,
                      type_of_document: str,
                      card_number: str,
                      card_holder_name: str,
                      tranzit_number: str,
                      bank_name: str,
                      specialization: str,
                      id_card_photo1: str | None,
                      id_card_photo2: str | None,
                      passport_photo: str | None
                      ):
        """
        Registers users in users table
        """
        sql = """
            INSERT INTO users (
                telegram_id, first_name, last_name, middle_name, 
                phone_number, type_of_document, card_number, 
                card_holder_name, tranzit_number, bank_name, 
                specialization, id_card_photo1, id_card_photo2, passport_photo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        params = (
            telegram_id, first_name, last_name, middle_name,
            phone_number, type_of_document, card_number,
            card_holder_name, tranzit_number, bank_name,
            specialization, id_card_photo1, id_card_photo2, passport_photo
        )
        self.execute(sql, params=params, commit=True)

    def update_field(self, telegram_id: str, field_name: str, value: str) -> None:
        """
        Updates a certain field for a given user.
        """
        allowed_fields = [
            "first_name", "last_name", "middle_name", "phone_number",
            "type_of_document", "card_number", "card_holder_name",
            "tranzit_number", "bank_name", "specialization",
            "id_card_photo1", "id_card_photo2", "passport_photo"
        ]

        if field_name not in allowed_fields:
            raise ValueError("Invalid field name")

        sql = f"UPDATE users SET {field_name} = %s WHERE telegram_id = %s"
        self.execute(sql, (value, telegram_id), commit=True)
