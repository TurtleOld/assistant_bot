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
    file_info = await bot.get_file(message.document.file_id)
    file_name, file_extension = path.splitext(file_info.file_path)
    if file_extension == ".pdf":
        file = await file_info.download("converter")

        print(file)
        pdf_file = f"{file.name}"
        print(pdf_file)
        file_name_pdf, file_extension_pdf = path.splitext(file.name)
        print(file_name_pdf)
        docx_file = f"{file_name_pdf}.docx"
        print(docx_file)

        cv = Converter(pdf_file)
        cv.convert(docx_file)
        cv.close()