from datetime import datetime

from users_core.config import BOT_TOKEN, postgres_url, scheduler, WEBHOOK_DOMAIN, WEBHOOK_PATH

from db.base import Base
from db.engine import create_async_engine, get_session_maker, proceed_models
from users_core.handlers.start_handler import start_router
from users_core.callbacks.get_content_callbacks.feedback_callback import feedback_router
from users_core.callbacks.get_content_callbacks.return_to_main_menu_callback import (
    main_menu_router,
)
from users_core.callbacks.menu_callbacks.settings_callback import settings_router
from users_core.callbacks.get_content_callbacks.buy_subscription_callback import (
    new_subscription_router,
)
from users_core.callbacks.get_content_callbacks.extend_subscription_callback import (
    renew_subscription_router,
)
from users_core.callbacks.get_content_callbacks.support_callback import support_router
from users_core.callbacks.get_content_callbacks.instruction_callback import (
    instruction_router,
)
from users_core.callbacks.menu_callbacks.notifications_menu_callback import (
    notifications_menu_router,
)
from users_core.callbacks.menu_callbacks.bank_menu_callback import bank_menu_router
from users_core.callbacks.menu_callbacks.activities_menu_callback import (
    activities_menu_router,
)
from users_core.callbacks.set_content_callbacks.set_notificatioin_callback import (
    set_notifications_router,
)
from users_core.callbacks.set_content_callbacks.set_bank_callback import set_bank_router
from users_core.callbacks.set_content_callbacks.set_activity_callback import (
    set_activity_router,
)
from users_core.utils.commands import set_commands

from admins_core.handlers.start_admin_panel_handler import start_admin_panel_router
from admins_core.callbacks.create_post_callbacks import (
    create_post_router,
    send_post_router,
)
from admins_core.callbacks.users_settings import users_settings_router
from admins_core.callbacks.return_to_admin_pannel_callback import (
    return_to_admin_panel_router,
)
from admins_core.callbacks.admins_route_callback import admins_route_router
from admins_core.callbacks.simple_admins_settings_callback import (
    simple_admins_settings_router,
    add_simple_admin_router,
    delete_simple_admin_router,
)
from admins_core.callbacks.super_admins_settings_callback import (
    super_admins_settings_router,
)
from admins_core.callbacks.payment_info_callback import payment_info_router
from admins_core.callbacks.show_payment_info_callback import show_payment_info_router
from admins_core.callbacks.add_cancel_sub_callbacks import add_cancel_sub_router
from admins_core.callbacks.add_delele_simple_admins_callbacks import (
    add_delete_simple_admins_router,
)
from admins_core.callbacks.add_delete_super_admins_callbacks import (
    add_delete_super_admins_router,
)
from admins_core.callbacks.add_cancel_sub_callbacks import (
    add_cancel_sub_router,
    get_end_date_for_add_sub_router,
    get_id_for_add_sub_router,
    delete_sub_router,
)
from users_core.callbacks.get_content_callbacks.calendar_callbacks import (
    calendar_router,
    show_event_router,
)
from admins_core.callbacks.super_admins_settings_callback import (
    add_super_admin_router,
    delete_super_admin_router,
    super_admins_settings_router,
)

import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from apsched.check_subscribs import check_subscribs

from fastapi import FastAPI
import uvicorn


bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

async_engine = create_async_engine(postgres_url)
session_maker = get_session_maker(async_engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_DOMAIN + WEBHOOK_PATH:
        await set_commands(bot)

        await proceed_models(async_engine)

        dp.include_routers(
            start_router,
            feedback_router,
            main_menu_router,
            settings_router,
            new_subscription_router,
            renew_subscription_router,
            support_router,
            instruction_router,
            notifications_menu_router,
            bank_menu_router,
            activities_menu_router,
            set_notifications_router,
            set_bank_router,
            set_activity_router,
            start_admin_panel_router,
            create_post_router,
            users_settings_router,
            return_to_admin_panel_router,
            admins_route_router,
            simple_admins_settings_router,
            super_admins_settings_router,
            payment_info_router,
            show_payment_info_router,
            add_cancel_sub_router,
            add_delete_simple_admins_router,
            add_delete_super_admins_router,
            get_end_date_for_add_sub_router,
            get_id_for_add_sub_router,
            delete_sub_router,
            send_post_router,
            calendar_router,
            add_simple_admin_router,
            delete_simple_admin_router,
            show_event_router,
            add_super_admin_router,
            delete_super_admin_router,
        )

        scheduler.add_job(
            check_subscribs,
            trigger="cron",
            hour=12,
            start_date=datetime.now(),
            kwargs={"bot": bot, "session_maker": session_maker},
        )
        scheduler.start()

        await bot.set_webhook(url=WEBHOOK_DOMAIN + WEBHOOK_PATH)

    yield
    await bot.delete_webhook()


app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)


@app.get("/ping")
async def ping():
    return {"response": "ok"}


@app.post(WEBHOOK_PATH)
async def bot_webhook(update):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update, session_maker=session_maker)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    uvicorn.run(app, host="127.0.0.1", port=8000)
