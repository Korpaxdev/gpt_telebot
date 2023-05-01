import asyncio
from http import HTTPStatus

import aiohttp

from classes.base_dataclasses import OpenAiMessages, OpenAiRoles


class OpenAi:
    MODEL = 'gpt-3.5-turbo'
    BASE_URL = 'https://api.openai.com/v1'

    def __init__(self, api_key: str):
        self.__headers = {
            'Authorization': f'Bearer {api_key}'
        }

    async def send_message(self, user_messages: list[OpenAiMessages]) -> OpenAiMessages | None:
        url = self.__get_chat_completion_url()
        data = self.__set_chat_completion_data(user_messages)
        async with aiohttp.ClientSession(headers=self.__headers) as session:
            try:
                async with session.post(url, json=data) as response:
                    response_data = await response.json()
                    if response.status != HTTPStatus.OK:
                        return print(response_data.get('error'))
                    content = response_data['choices'][0]['message']['content']
                    message = OpenAiMessages(role=OpenAiRoles.ASSISTANT, content=content)
                    return message
            except (asyncio.TimeoutError, aiohttp.ClientError, Exception) as error:
                return print(error)

    def __get_chat_completion_url(self):
        return f"{self.BASE_URL}/chat/completions"

    def __set_chat_completion_data(self, user_messages: list[OpenAiMessages]):
        messages = [message.__dict__ for message in user_messages]
        return dict(model=self.MODEL, messages=messages)
