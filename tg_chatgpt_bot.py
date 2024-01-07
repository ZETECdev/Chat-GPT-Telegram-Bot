import asyncio
from TELEBOT.async_telebot import AsyncTeleBot
from requests import post
from os.path import dirname, abspath
from json import dump, load

# GENERAL
path = dirname(abspath(__file__))

with open(path + '/chatgpt_bot.json', 'r') as cgptb:
    try:
        data = load(cgptb)
    except FileNotFoundError:
        data = {}
        data['OPENAIAPIKEY'] = input('Add your OPENAI API KEY')
        data['GPT_MODEL'] = input('Add the GPT Model. Latest free model is gpt-3.5-turbo-1106')
        data['INSTRUCTIONS'] = input('Directions / Instructions of your custom Chat GPT Bot')
        data['TELEGRAM_BOT_API_KEY'] = input('Add the TElegram Bot API KEY')
        with open(path + '/chatgpt_bot.json', 'w') as cgptb:
            dump(data, cgptb)

tg = AsyncTeleBot(data['TELEGRAM_BOT_API_KEY'], parse_mode='Markdown')
chats = {}

# HANDLER
@tg.message_handler(commands = ['e'])
async def gpt_assistant(message):
    user_id = message.from_user.id
    if user_id not in chats:
        chats[user_id] = []
    try:
        msg = message.text[3:]
        chats[user_id].append({"role": "user", "content": msg})
        response = await gpt_response(chats[user_id], msg)
        if response is not None:
            chats[user_id].append({"role": "assistant", "content": response})
            await tg.reply_to(message, f'_{response}_')
        else:
            await tg.reply_to(message, '_API Error_')
    except: return

# HANDLER RESET CONVERSATION FOR A SINGLE USER
@tg.message_handler(commands = ['reset'])
async def reset_conversation(message):
    user_id = message.from_user.id
    if user_id in chats:
        chats[user_id] = []
        await tg.reply_to(message, f'*@{message.from_user.username}* _conversation reset_')
        await asyncio.sleep(30)
        await tg.delete_message(message.chat.id, message.message_id)

def gpt_response(messages, msg):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {data["OPENAIAPIKEY"]}'
        }
    data = {
        'model': data["GPT_MODEL"],
        'messages': messages + [{"role": "system", "content": data["INSTRUCTIONS"]}, {"role": "user", "content": msg}]
        }
    response = post('https://api.openai.com/v1/chat/completions', headers = headers, data = dump(data))
    if response.status_code == 200:
        response = load(response.text)['choices'][0]['message']['content']
        return response


asyncio.run(tg.infinity_polling())
