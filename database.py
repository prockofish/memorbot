import sqlite3

class DataBase:
    def __init__(self, db_name: str, table_name: str) -> None:
        self.db_name = db_name
        self.table_name = table_name
        self.connection = sqlite3.connect(self.db_name, timeout=10)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users( id INT, age TEXT, gender TEXT, param TEXT, dicts TEXT )")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS dicts( id INT, name TEXT, dict TEXT )")
        self.connection.commit()

    def close(self):
        self.connection.commit()
        self.connection.close()

    def create(self, page_id: str) -> None:
        if not self.get(page_id):
            self.cursor.execute(f"INSERT INTO {self.table_name} (id) VALUES (?)", (page_id,))
            self.connection.commit()

    def remove(self, page_id: int) -> None:
        if self.get(page_id):
            self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (page_id,))
            self.connection.commit()

    def enter(self, page_id: int, name: str, content: str) -> bool:
        rows = self.cursor.execute(f"UPDATE {self.table_name} SET {name} = ? WHERE id = ?", (content, page_id)).rowcount
        self.connection.commit()
        if rows == 0:
            return False
        return True

    def get(self, page_id: int, name: str = None) -> list:
        if name:
            data = self.cursor.execute(f"SELECT {name} FROM {self.table_name} WHERE id = ?", (page_id,)).fetchone()
            return data
        return self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (page_id,)).fetchone()

    def get_all(self) -> list:
        return self.cursor.execute(f"SELECT * FROM {self.table_name}").fetchall()

    def get_count_not_empty_in_page(self, page_id: int) -> int:
        page = self.get(page_id)
        if page:
            return len([item for item in page if item is not None])
        return 0

    def __del__(self):
        self.close()
