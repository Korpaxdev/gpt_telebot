from telebot.util import content_type_media

ALLOWED_CONTENT_TYPES = ('text',)
NOT_ALLOWED_CONTENT_TYPES = tuple(filter(lambda t: t not in ALLOWED_CONTENT_TYPES, content_type_media))
MAX_HISTORY_MESSAGES = 10
