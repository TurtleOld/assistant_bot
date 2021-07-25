from pdf2docx import Converter
from main import dp, bot
from os import getenv, listdir, remove, path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types

load_dotenv()
admin_id = getenv("admin_id")
user_id_required = getenv("user_id_required")


@dp.message_handler(content_types=['document'])
async def convert_pdf_to_docx(message: types.Message):
    user_id = message.from_user.id
    file_info = await bot.get_file(message.document.file_id)
    file_name, file_extension = path.splitext(file_info.file_path)

    if file_extension == ".pdf":
        file = await file_info.download("converter")

        pdf_file = f"{file.name}"

        file_name_pdf, file_extension_pdf = path.splitext(file.name)

        docx_file = f"{file_name_pdf}.docx"

        cv = Converter(pdf_file)
        cv.convert(docx_file)
        cv.close()

        await bot.send_message(user_id, "Пожалуйста, вот твой готовый файл в формате DOCX:")
        await bot.send_document(user_id, open(docx_file, "rb"))
