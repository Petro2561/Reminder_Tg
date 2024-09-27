from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend


from bot.config import load_config

config = load_config()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        
        if form['username'] == config.admin_config.admin_login and form['password'] == config.admin_config.admin_password:
            request.session.update({"token": config.admin_config.secret_key})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        return True