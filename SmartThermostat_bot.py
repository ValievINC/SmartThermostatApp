from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import subprocess
import os
import json

TOKEN = "6432892932:AAFfhsmg_Pjcvca8lAK8gza6cLiUIQ_wN9I"
MOSQUITTO_PATH = r"C:\Program Files\mosquitto"

# Словарь для настроек
settings = {
    "Температура": "desired_temperature",
    "Влажность": "desired_humidity",
    "Мощность_кондиционера(Температура)": "desired_power_conditioner_temperature",
    "Мощность_кондиционера(Влажность)": "desired_power_conditioner_humidity",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие на /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Вы попали в Термостат_Бот",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фунция, которая показывает доступные комманды, если ввести /help"""
    text = ("/change_mode [Manual/Automatic] - сменить режим на Ручной/Автоматическиий\n"
            "/set [setting] [float] - изменить настройки. Доступны настройки: Температура, Влажность Мощность кондиционера(Температура), Мощность кондиционера(Влажность)\n"
            "/get_statistics - получить данные с термостата")
    await update.message.reply_text(text)


async def change_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция, отвечающая за смену режима работы термостата"""
    args = context.args
    if args[0] in ["Manual", "Automatic"]:
        mode = args[0]
        os.chdir(MOSQUITTO_PATH)

        command = f'.\\mosquitto_pub -h localhost -t smart_thermostat -m "{{\\"mode\\": \\"{mode}\\"}}"'
        subprocess.run(command, shell=True)

        await update.message.reply_text(f"Режим термостата был установлен на {mode}")
    else:
        await update.message.reply_text(f"Введите режим работы термостата (Manual/Automatic)")


async def set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция, отвечающая за смену настроек термостата"""
    args = context.args
    if args[0] in ["Температура", "Влажность", "Мощность_кондиционера(Температура)", "Мощность_кондиционера(Влажность)"]:
        if args[0] == "Температура" and (float(args[1]) < 15 or float(args[1]) > 45):
            await update.message.reply_text(f"Температура может быть только в пределах от 15 до 45 градусов")
            return
        elif float(args[1]) > 100 or float(args[1]) < 0:
            await update.message.reply_text(f"{args[0]} может быть только в пределах от 0 до 100 %")
            return

        os.chdir(MOSQUITTO_PATH)

        command = f'.\\mosquitto_pub -h localhost -t smart_thermostat -m "{{\\"{settings[args[0]]}\\": \\"{float(args[1])}\\"}}"'
        subprocess.run(command, shell=True)

        await update.message.reply_text(f"Применена следующая настройка:\n{args[0]}: {args[1]}")
    else:
        await update.message.reply_text(f"Выберите настройку из списка: Температура, Влажность Мощность кондиционера(Температура), Мощность кондиционера(Влажность)")


async def get_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция, которая выводит информацию с датчиков на момент запроса"""
    MOSQUITTO_PATH = r"C:\Program Files\mosquitto"

    os.chdir(MOSQUITTO_PATH)
    command = r'.\mosquitto_sub -h localhost -t smart_thermostat'

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

    while True:
        output = process.stdout.readline()
        if not output and process.poll() is not None:
            break

        json_data = json.loads(output)

        data = json_data['log'].split("<new_line>")
        message = "\n".join(data)

        await update.message.reply_text(f"{message}")
        break


def main():
    """Построение телеграм-бота"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Команды термостата
    application.add_handler(CommandHandler("change_mode", change_mode, has_args=True))
    application.add_handler(CommandHandler("set", set, has_args=True))
    application.add_handler(CommandHandler("get_statistics", get_statistics))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()