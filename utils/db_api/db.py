import logging

from datetime import datetime, date
from typing import List, Dict, Union

import pymysql


logger = logging.getLogger(__name__)

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
                lang VARCHAR(2) DEFAULT 'uz',
                first_name VARCHAR(50) NULL,
                last_name VARCHAR(50) NULL,
                middle_name VARCHAR(50) NULL,
                born_year DATE NULL,
                phone_number VARCHAR(12) NULL,
                type_of_document VARCHAR(20) NULL,
                card_number VARCHAR(16) NULL,
                card_holder_name VARCHAR(100) NULL,
                tranzit_number VARCHAR(50) NULL,
                bank_name VARCHAR(20) NULL,
                specialization VARCHAR(255) NULL,
                id_card_photo1 VARCHAR(255) NULL,
                id_card_photo2 VARCHAR(255) NULL,
                passport_photo VARCHAR(255) NULL
            )
        """
        self.execute(sql)

    def create_days_table(self) -> None:
        """
        Creates days table for working days
        """
        sql = """
            CREATE TABLE IF NOT EXISTS days(
                id INT PRIMARY KEY AUTO_INCREMENT,
                date DATE NOT NULL
            )
        """
        self.execute(sql)

    def create_attendance_table(self) -> None:
        """
        Creates attendance table to save workers attendance
        """
        sql = """
            CREATE TABLE IF NOT EXISTS attendance(
                id INT PRIMARY KEY AUTO_INCREMENT,
                worker INT NOT NULL REFERENCES users(id),
                day INT NOT NULL REFERENCES days(id),
                is_absent BOOL NOT NULL DEFAULT TRUE,
                start_time TIME,
                end_time TIME,

                CONSTRAINT unique_attendance_for_user_per_day UNIQUE(day, worker)
            )
        """
        self.execute(sql)

    def create_attendance_for_user(self, user_id: int, day_id: int) -> None:
        """
        Creates attendance for a particular user
        """
        sql = """
            INSERT INTO attendance(worker, day) VALUES(%s, %s)
        """
        self.execute(sql, (user_id, day_id), commit=True)

    def create_day(self, date: datetime.date) -> int:
        """
        Creates a working day
        """
        sql = """
            INSERT INTO days(date) VALUES(%s)
        """
        self.execute(sql, (date,), commit=True)

    def initial_registration(self, telegram_id: str) -> None:
        """
        Initial registration of a user
        """
        sql = """
            INSERT INTO users(telegram_id)
            VALUES (%s)
        """
        self.execute(sql, (telegram_id,), commit=True)

    def update_user_field(self, telegram_id: str, field_name: str, value: str) -> None:
        """
        Updates a certain field for a given user.
        """
        allowed_fields = [
            "first_name", "last_name", "middle_name", "phone_number",
            "type_of_document", "card_number", "card_holder_name",
            "tranzit_number", "bank_name", "specialization",
            "id_card_photo1", "id_card_photo2", "passport_photo",
            "lang", "born_year",
        ]

        if field_name not in allowed_fields:
            raise ValueError("Invalid field name")

        sql = f"UPDATE users SET {field_name} = %s WHERE telegram_id = %s"
        self.execute(sql, (value, telegram_id), commit=True)

    def update_user_attendance(self, user_id: int, is_absent: bool) -> None:
        """
        Updates user's attendance (is_absent) for today
        """
        today = date.today()
    
        # Get or create today's day
        day = self.get_day(today)
        if not day:
            day_id = self.create_day(today)
        else:
            day_id = day.get("id")
    
        # Update attendance
        sql = "UPDATE attendance SET is_absent = %s WHERE worker = %s AND day = %s"
        self.execute(sql, (is_absent, user_id, day_id), commit=True)

    def update_user_attendance_time(self, user_id: int, field_name: str, time: datetime.time):
        """
        Updates user's start_time or end_time for today
        """
        if field_name not in ["start_time", "end_time"]:
            raise ValueError("Should be 'start_time' or 'end_time'")
    
        today = date.today()
    
        # Get or create today's day
        day = self.get_day(today)
        if not day:
            day_id = self.create_day(today)
        else:
            day_id = day.get("id")
    
        # Ensure attendance exists
        attendance = self.get_attendance(user_id, day_id)
        if not attendance:
            try:
                self.create_attendance_for_user(user_id, day_id)
            except pymysql.IntegrityError as e:
                logger.warning(
                    "Attendance already exists (race condition). user_id=%s day_id=%s field=%s time=%s error=%s. Location: db.py, line: 209",
                    user_id, day_id, field_name, time, e
                )

        # Update the time
        sql = f"UPDATE attendance SET {field_name} = %s WHERE worker = %s AND day = %s"
        self.execute(sql, (time, user_id, day_id), commit=True)
    
        # Update the time
        sql = f"UPDATE attendance SET {field_name} = %s WHERE worker = %s AND day = %s"
        self.execute(sql, (time, user_id, day_id), commit=True)

    def get_user(self, telegram_id: str) -> dict:
        """
        Returns ceratin user from users table
        """
        sql = """
            SELECT * FROM users WHERE telegram_id = %s
        """
        return self.execute(sql, (telegram_id,), fetchone=True)

    def get_users(self) -> list[dict]:
        """
        Returns all users from users table
        """
        sql = """
            SELECT * FROM users
        """
        return self.execute(sql, fetchall=True)

    def get_user_language(self, telegram_id: str) -> str:
        """
        Returns telegram_id of a users
        """
        sql = """
            SELECT lang FROM users
            WHERE telegram_id = %s
        """
        result = self.execute(sql, (telegram_id,), fetchone=True)

        if result:
            return result.get('lang')
        return 'uz'

    def get_day(self, day_date: Union[datetime, date, str]) -> dict | None:
        """
        Returns day record from 'days' table
        Accepts datetime, date, or string 'YYYY-MM-DD'
        """
        if isinstance(day_date, datetime):
            day_date = day_date.date()
        elif isinstance(day_date, str):
            day_date = datetime.strptime(day_date, "%Y-%m-%d").date()
    
        sql = "SELECT * FROM days WHERE date = %s"
        return self.execute(sql, (day_date,), fetchone=True)

    def get_attendance(self, user_id: int, day_id: int) -> dict | None:
        """
        Returns attendance of a user or None if it doesn't exist
        """
        sql = """
            SELECT * FROM attendance WHERE worker = %s AND day = %s
        """
        return self.execute(sql, (user_id, day_id), fetchone=True)


    def get_users_with_open_attendance(self) -> list[dict]:
        """
        Returns users who:
        - have attendance for today
        - HAVE started their working day (start_time IS NOT NULL)
        - HAVE NOT ended their working day yet (end_time IS NULL)
        """
        sql = """
            SELECT
                u.*,
                a.id AS attendance_id,
                a.start_time,
                a.end_time,
                a.is_absent
            FROM attendance a
            JOIN users u ON u.id = a.worker
            JOIN days d ON d.id = a.day
            WHERE d.date = %s
            AND a.start_time IS NOT NULL
            AND a.end_time IS NULL
        """
        today = datetime.today().date()
        return self.execute(sql, (today,), fetchall=True)
