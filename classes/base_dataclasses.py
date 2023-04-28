from dataclasses import dataclass
from typing import Type


@dataclass(frozen=True)
class BaseMessages:
    START_MESSAGE = '<pre>Привет. Через меня вы можете использовать ChapGTP.\n' \
                    'Для этого достаточно просто достаточно ввести запрос, который вы хотите отправить нейросети.\n' \
                    'Так же ваш контекст общения сохраняется в пределах 10 сообщений.</pre>'

    NOT_AUTHORIZED = '<pre>К сожалению вы не авторизированны</pre>'
    MESSAGE_WAS_SEND = '<pre>Ваше сообщение было отправлено нейросети. Дождитесь ответа</pre>'
    TOO_MAY_MESSAGES = '<pre>Нейросеть еще не ответила на ваше прошлое сообщение.' \
                       ' Дождитесь ответа от нейросети</pre>'
    REQUEST_ERROR = '<pre>Произошла ошибка при запросе. Повторите свою попытку позже</pre>'

    ONLY_TEXT = '<pre>В настоящий момент общение с ботом доступно только с помощью текста </pre>'


@dataclass(frozen=True)
class UserStatements:
    PENDING = 'PENDING'


@dataclass(frozen=True)
class OpenAiRoles:
    USER = 'user'
    ASSISTANT = 'assistant'


@dataclass
class OpenAiMessages:
    role: Type[OpenAiRoles] | str
    content: str
