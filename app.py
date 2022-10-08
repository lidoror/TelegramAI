import os.path

import telebot
from utils import search_download_youtube_video
from loguru import logger


class Bot:

    def __init__(self, token):
        self.bot = telebot.TeleBot(token, threaded=False)
        self.bot.set_update_listener(self._bot_internal_handler)

        self.current_msg = None

    def _bot_internal_handler(self, messages):
        """Bot internal messages handler"""
        for message in messages:
            self.current_msg = message
            self.handle_message(message)

    def start(self):
        """Start polling msgs from users, this function never returns"""
        logger.info(f'{self.__class__.__name__} is up and listening to new messages....')
        logger.info('Telegram Bot information')
        logger.info(self.bot.get_me())

        self.bot.infinity_polling()

    def send_text(self, text):
        self.bot.send_message(self.current_msg.chat.id, text)

    def send_text_with_quote(self, text, message_id):
        self.bot.send_message(self.current_msg.chat.id, text, reply_to_message_id=message_id)

    def is_current_msg_photo(self):
        return self.current_msg.content_type == 'photo'

    def download_user_photo(self, quality=0):
        """
        Downloads photos sent to the Bot to `photos` directory (should be existed)
        :param quality: integer representing the file quality. Allowed values are [0, 1, 2, 3]
        :return:
        """
        if self.current_msg.content_type != 'photo':
            raise RuntimeError(
                f'Message content of type \'photo\' expected, but got {self.current_msg.content_type}')

        file_info = self.bot.get_file(self.current_msg.photo[quality].file_id)
        data = self.bot.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info

    def handle_message(self, message):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {message}')
        self.send_text(f'Your original message: {message.text}')


class QuoteBot(Bot):
    def handle_message(self, message):
        if message.text != 'Don\'t quote me please':
            self.send_text_with_quote(message.text, message_id=message.message_id)


class YoutubeBot(Bot):
    """
    the class getting message and searching in youtube for videos that have the same name as the message
    """

    def __init__(self, token):
        super().__init__(token)
        self.cache = {}

    def handle_message(self, message):
        """
        youtube bot message handler
        """

        if self.is_current_msg_photo():
            self.download_user_photo(quality=3)
            return


        if message.text in self.cache:
            file_path = os.path.join('./', self.cache.get(message.text))
            if self.file_exist(file_path):
                self.send_video(message, file_path)
                return

        video = self.download_video_from_youtube(message)
        self.cache[message.text] = video[0].get('filename')
        self.send_text(self.get_downloaded_video_link(video))

    def file_exist(self, file_path):
        return os.path.exists(file_path)

    def send_video(self, message, path):
        video = open(path, 'rb')
        self.bot.send_video(message.chat.id, video)

    def send_photo(self, message, path):
        photo = open(path, 'rb')
        self.bot.send_photo(message.chat.id, photo)

    def download_video_from_youtube(self, message):
        """
        ":param: message: the message sent from the user
        this method downloads video from youtube
        :return: the downloaded video
        """

        video = search_download_youtube_video(message.text)
        return video

    def get_downloaded_video_link(self, video):
        """
        :param: video: video sent to the method
        this method gets video
        :return: url of teh video
        """
        video_link = video[0].get("url")
        return video_link


if __name__ == '__main__':
    with open('.telegramToken') as f:
        _token = f.read()

    my_bot = YoutubeBot(_token)
    my_bot.start()
