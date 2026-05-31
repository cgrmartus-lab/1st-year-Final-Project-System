import os
from models.product_model import ProductModel
from utils.binary_search  import binary_search
from utils.csv_handler    import parse_csv
from utils.excel_exporter import export_to_excel


class ProductController:
    def __init__(self, product_model: ProductModel):
        self.model = product_model

    def get_products(self, query: str = "") -> list:
        return self.model.get_all(query)

    def add_product(self, code, name, cat, price, stock, added_by) -> tuple:
        try:
            self.model.add(code.strip(), name.strip(), cat,
                           float(price), int(stock), added_by)
            return True, f"'{name}' added to inventory."
        except ValueError as e:
            return False, str(e)

    def update_product(self, pid, code, name, cat, price, stock) -> tuple:
        try:
            self.model.update(pid, code.strip(), name.strip(), cat,
                              float(price), int(stock))
            return True, f"'{name}' updated successfully."
        except ValueError as e:
            return False, str(e)

    def delete_product(self, pid) -> tuple:
        row = self.model.get_by_id(pid)
        if not row:
            return False, f"Product ID {pid} not found."
        name = row["prodName"]
        self.model.delete(pid)
        return True, f"'{name}' deleted from inventory."

    def binary_search_by_code(self, target: str) -> tuple:
        codes = self.model.get_sorted_codes()
        idx, steps = binary_search(codes, target)
        found = None
        if idx >= 0:
            all_rows = self.model.get_all()
            found = next(
                (r for r in all_rows
                 if r["prodCode"].upper() == target.strip().upper()),
                None,
            )
        return idx, steps, found

    def import_csv(self, file_path: str, added_by: int) -> tuple:
        rows, parse_errors = parse_csv(file_path)
        if parse_errors:
            return 0, parse_errors
        ok, db_errors = self.model.bulk_insert(rows, added_by)
        return ok, db_errors

    def export_excel(self, query: str = "") -> tuple:
        try:
            rows = self.model.get_all(query)
            if not rows:
                return False, "No data to export."
            path = export_to_excel(rows, output_dir=os.getcwd())
            return True, f"Exported to: {path}"
        except Exception as e:
            return False, f"Export failed: {e}"

    @staticmethod
    def validate(code, name, cat, price, stock) -> list:
        errors = []
        if not str(code).strip():
            errors.append("Product Code is required.")
        if not str(name).strip():
            errors.append("Product Name is required.")
        if not cat:
            errors.append("Category is required.")
        try:
            if float(price) < 0:
                errors.append("Price must be >= 0.")
        except (ValueError, TypeError):
            errors.append("Price must be a number.")
        try:
            if int(stock) < 0:
                errors.append("Stock must be >= 0.")
        except (ValueError, TypeError):
            errors.append("Stock must be a whole number.")
        return errors
