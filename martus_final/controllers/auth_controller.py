from models.user_model import UserModel


class AuthController:
    def __init__(self, user_model: UserModel):
        self.model = user_model
        self.current_user = None

    def login(self, username: str, password: str) -> tuple:
        if not username.strip() or not password.strip():
            return False, "Username and password are required."
        user = self.model.authenticate(username.strip(), password.strip())
        if user:
            self.current_user = user
            return True, f"Welcome, {user['username']}! (Role: {user['role']})"
        return False, "Invalid username or password."

    def logout(self):
        self.current_user = None

    @property
    def role(self) -> str:
        return self.current_user["role"] if self.current_user else "viewer"

    @property
    def user_id(self) -> int:
        return self.current_user["userID"] if self.current_user else 0

    def can_write(self) -> bool:
        return self.role in ("admin", "staff")

    def is_admin(self) -> bool:
        return self.role == "admin"
