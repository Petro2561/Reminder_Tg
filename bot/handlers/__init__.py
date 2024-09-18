from aiogram import Router

from . import handlers_notes, handlers_user

router = Router()
router.include_routers(handlers_user.router, handlers_notes.router)
