import yadisk
import requests
from loguru import logger
from aiogram import Bot, Dispatcher, executor, types

from keyboards import kb

from auth_data import YA_TOKEN, TELEGRAM_TOKEN

logger.add("debug.log", format="{time} {level} {message}")

headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {YA_TOKEN}'}


def replace_invalid_characters(file_name: str) -> str:
    invalid_characters = '<>:"/\|?*'
    
    for char in invalid_characters:
        file_name = file_name.replace(char, ' ')
    
    return file_name



def upload_photo(participate, file_url, ya_token, text, ext, user):
    y = yadisk.YaDisk(token=ya_token)
    file_name = text.replace('#', '_') + '.' + ext
    file_name = replace_invalid_characters(file_name)
    image_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload?url={file_url}&path=/{participate}/{file_name}"
    try:
        y.mkdir(f"/{participate}")
    except Exception as e:
        logger.warning(e)
    try:
        logger.debug(f"User with id={user.id} and username={user.username} try to upload photo.")
        response = requests.post(url=image_url, headers=headers)
        logger.debug(response.json())        
    except Exception as e:
        logger.error(e)



bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.from_user.id, text=f"Привет, {message.from_user.first_name}!", reply_markup=kb)



@dp.message_handler(text = 'О боте')
async def process_about_command(message: types.Message):
    await bot.send_message(message.from_user.id, text="Я - бот школы 548 для отправки фотоподтверждения посещения площадок Олимпиады 'Музеи. Парки. Усадьбы' нашими учениками", reply_markup=kb)


@dp.message_handler(text = 'Инструкция')
async def process_help_command(message: types.Message):
    await bot.send_message(message.from_user.id, text="Для того, чтобы отправить фотографию, нужно:\n1. Прикрепить изображение.\n2. Добавить подпись к изображению - хэштег вида #МПУ2022 #у1234567 #Название музея/парка/усадьбы.", reply_markup=kb)


@dp.message_handler(content_types=['photo', 'document'])
async def scan_message(msg: types.Message):

    if msg.content_type == 'photo':
        document_id = msg.photo[-1].file_id
    elif msg.content_type == 'document':
        if not msg.document.mime_base == 'image':
            logger.debug(f"User with id={msg.from_user.id} and username={msg.from_user.username} try to upload a document that is not an image (mime_base={msg.document.mime_base}).")
            await bot.send_message(msg.from_user.id, "Необходимо прикрепить изображение.", reply_markup=kb)
            return
        document_id = msg.document.file_id

    file_info = await bot.get_file(document_id)

    file_path = file_info.file_path
    ext = file_path.split('.')[-1]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    text = msg.caption
    
    try:        
        _, olimp, participant, place = text.split('#')
        print(olimp, participant, place)
        if not olimp.strip() == 'МПУ2022':
            raise Exception
        if not participant.startswith('у'):
            raise Exception        
        upload_photo(participant, file_url, YA_TOKEN, text, ext, msg.from_user)
        await bot.send_message(msg.from_user.id, "Фотография отправлена. Спасибо!")
    except Exception as e:
        logger.error(e)
        await bot.send_message(msg.from_user.id, "Хэштег введён некорректно.\nПопробуйте ещё раз.")


@dp.message_handler(content_types=["text", "audio", "sticker", "video", "video_note", "voice", "location",
"contact", "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
"group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id", "migrate_from_chat_id",
"pinned_message", "web_app_data", "poll"])
async def scan_message(msg: types.Message):
    logger.debug(f"User with id={msg.from_user.id} and username={msg.from_user.username} try to upload {msg.content_type}.")
    await bot.send_message(msg.from_user.id, "Необходимо прикрепить изображение с хэштегом.", reply_markup=kb)



if __name__ == "__main__":
    executor.start_polling(dp)