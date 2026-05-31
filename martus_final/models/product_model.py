import sqlite3
from typing import Optional


class ProductModel:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    #READ
    def get_all(self, query: str = "") -> list:
        """
        Return products with the username who added them via INNER JOIN.
        Products with no addedBy (NULL) are included via UNION + LEFT JOIN.
        Results ordered by prodCode ASC so Binary Search works correctly.
        """
        q = f"%{query.strip().lower()}%"
        sql = """
            SELECT p.prodID, p.prodCode, p.prodName, p.category,
                   p.price, p.stock, u.username AS addedBy
            FROM   PRODUCTS p
            INNER JOIN USERS u ON p.addedBy = u.userID
            WHERE (LOWER(p.prodCode) LIKE ?
               OR  LOWER(p.prodName) LIKE ?
               OR  LOWER(p.category) LIKE ?
               OR  LOWER(CAST(p.prodID AS TEXT)) LIKE ?)
            UNION
            SELECT p.prodID, p.prodCode, p.prodName, p.category,
                   p.price, p.stock, '—' AS addedBy
            FROM   PRODUCTS p
            WHERE  p.addedBy IS NULL
              AND (LOWER(p.prodCode) LIKE ?
               OR  LOWER(p.prodName) LIKE ?
               OR  LOWER(p.category) LIKE ?
               OR  LOWER(CAST(p.prodID AS TEXT)) LIKE ?)
            ORDER BY prodCode ASC
        """
        return self.conn.execute(sql, [q, q, q, q, q, q, q, q]).fetchall()

    def get_by_id(self, pid: int) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM PRODUCTS WHERE prodID=?", (pid,)
        ).fetchone()

    def get_sorted_codes(self) -> list:
        rows = self.conn.execute(
            "SELECT prodCode FROM PRODUCTS ORDER BY prodCode ASC"
        ).fetchall()
        return [r["prodCode"] for r in rows]

    #CREATE
    def add(self, code, name, cat, price, stock, added_by: int) -> None:
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO PRODUCTS "
                    "(prodCode,prodName,category,price,stock,addedBy) "
                    "VALUES (?,?,?,?,?,?)",
                    (code, name, cat, price, stock, added_by),
                )
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Duplicate product code '{code}'.") from e

    #UPDATE
    def update(self, pid, code, name, cat, price, stock) -> None:
        try:
            with self.conn:
                self.conn.execute(
                    "UPDATE PRODUCTS "
                    "SET prodCode=?,prodName=?,category=?,price=?,stock=? "
                    "WHERE prodID=?",
                    (code, name, cat, price, stock, pid),
                )
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Duplicate product code '{code}'.") from e

    #DELETE
    def delete(self, pid: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM PRODUCTS WHERE prodID=?", (pid,))

    #BULK INSERT
    def bulk_insert(self, rows: list, added_by: int) -> tuple:
        success, errors = 0, []
        for r in rows:
            try:
                self.add(
                    r["prodCode"], r["prodName"], r["category"],
                    float(r["price"]), int(r["stock"]), added_by,
                )
                success += 1
            except (ValueError, KeyError) as e:
                errors.append(str(e))
        return success, errors
