import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, User

from classes.base_dataclasses import BaseMessages, UserStatements, OpenAiRoles, OpenAiMessages
from classes.open_ai import OpenAi
from models import Base, Users, UserMessagesHistory


class TelegramBot:
    MAX_MESSAGES = 10

    def __init__(self, env_config: dict[str, str | None]):
        self._bot = AsyncTeleBot(env_config.get('TELEGRAM_TOKEN'))
        self._engine = create_engine(env_config.get('DB_NAME'))
        self._openai = OpenAi(env_config.get('OPENAI_API_KEY'))
        Base.metadata.create_all(self._engine)

    async def __start_handler(self, message: Message):
        await self.__send_html_message(message.chat.id, BaseMessages.START_MESSAGE)

    async def __message_handler(self, message: Message):
        user = message.from_user
        chat_id = message.chat.id
        user_state = await self._bot.get_state(user.id)
        self.__add_user_into_db_if_not_exist(user)

        if not self.__is_authenticated(user.id):
            return await self.__send_html_message(chat_id, BaseMessages.NOT_AUTHORIZED)
        if user_state == UserStatements.PENDING:
            return await self.__send_html_message(chat_id, BaseMessages.TOO_MAY_MESSAGES)

        await self._bot.set_state(user.id, UserStatements.PENDING)
        self.__add_history_in_bd(user, OpenAiMessages(role=OpenAiRoles.USER, content=message.text))
        messages = self.__get_user_history()
        await self.__send_html_message(chat_id, BaseMessages.MESSAGE_WAS_SEND)
        openai_message = await self._openai.send_message(messages)
        if not openai_message:
            return await self.__send_html_message(chat_id, BaseMessages.REQUEST_ERROR)
        self.__add_history_in_bd(user, openai_message)
        await self._bot.reply_to(message, openai_message.content)
        await self._bot.delete_state(user.id)

    async def __send_html_message(self, chat_id: int, message: str):
        await self._bot.send_message(chat_id, message, parse_mode='html')

    def __create_session(self):
        return Session(bind=self._engine)

    def __is_authenticated(self, telegram_id: int):
        with self.__create_session() as session:
            return session.query(Users).filter_by(telegram_id=telegram_id, is_authorized=True).first()

    def __add_user_into_db_if_not_exist(self, user: User):
        with self.__create_session() as session:
            if not (session.query(Users).filter_by(telegram_id=user.id, username=user.username).first()):
                user = Users(telegram_id=user.id, username=user.username)
                session.add(user)
                session.commit()

    def __add_history_in_bd(self, user: User, messages: OpenAiMessages):
        with self.__create_session() as session:
            user = session.query(Users).filter_by(telegram_id=user.id, username=user.username).first()
            if not user:
                return
            messages_query = session.query(UserMessagesHistory).order_by('created_at')
            messages_count = messages_query.count()
            if messages_count >= self.MAX_MESSAGES:
                first_message = messages_query.first()
                session.delete(first_message)
            message = UserMessagesHistory(user=user.id, role=messages.role, content=messages.content)
            session.add(message)
            session.commit()

    def __get_user_history(self):
        with self.__create_session() as session:
            messages = session.query(UserMessagesHistory).all()
            return [OpenAiMessages(role=message.role, content=message.content) for message in messages]

    async def __other_handlers(self, message: Message):
        return await self.__send_html_message(message.chat.id, BaseMessages.ONLY_TEXT)

    def start(self):
        self._bot.message_handler(commands=['start'])(self.__start_handler)
        self._bot.message_handler(content_types=['text'])(self.__message_handler)
        self._bot.message_handler(content_types=['video', 'document', 'location', 'contact', 'sticker'])(
            self.__other_handlers)
        asyncio.run(self._bot.polling())
