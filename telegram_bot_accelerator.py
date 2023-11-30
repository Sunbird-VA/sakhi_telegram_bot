import logging
import urllib
from typing import Union, TypedDict
import requests
from telegram import __version__ as TG_VER
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import os
from dotenv import load_dotenv
from pitaras import *


"""
start - Start the bot
set_engine - To choose the engine 
set_language - To choose language of your choice
"""

load_dotenv()

botName = os.environ['botName']

bot = Bot(token=os.environ['token'])
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_meesage_to_bot(chat_id, text, parse_mode = "Markdown") -> None:
    """Send a message  to bot"""
    await bot.send_message(chat_id=chat_id, text=text, parse_mode = parse_mode)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_name = update.message.chat.first_name
    await send_meesage_to_bot(update.effective_chat.id, f"Hello, {user_name}! I am **{botName}**, your companion. \n\nI can assist you in finding stories, rhymes, puzzles, and a variety of other enjoyable activities.  \n\nFurthermore, I can also answer your questions  or offer assistance with any other needs you may have.\n\nAdditionally, you can easily access activities that ignite your interest from the left-side hamburger menu within the chatbox.")
    await send_meesage_to_bot(update.effective_chat.id, "What would you like to do today?")
    await relay_handler(update, context)


async def relay_handler(update: Update, context: CallbackContext):
    # setting engine manually
    language = context.user_data.get('language')

    if language is None:
        await language_handler(update, context)
    # else:
        # await keyword_handler(update, context)

async def language_handler(update: Update, context):
    english_button = InlineKeyboardButton('English', callback_data='lang_English')
    hindi_button = InlineKeyboardButton('हिंदी', callback_data='lang_Hindi')
    kannada_button = InlineKeyboardButton('ಕನ್ನಡ', callback_data='lang_Kannada')

    inline_keyboard_buttons = [[english_button], [hindi_button], [kannada_button]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)

    await bot.send_message(chat_id=update.effective_chat.id, text="Choose a Language:", reply_markup=reply_markup)


async def preferred_language_callback(update: Update, context: CallbackContext):
    
    callback_query = update.callback_query
    preferred_language = callback_query.data.lstrip('lang_')
    context.user_data['language'] = preferred_language

    text_message = ""
    if preferred_language == "English":
        text_message = "You have chosen English. \nPlease give your query now"
    elif preferred_language == "Hindi":
        text_message = "आपने हिंदी चुना है। \nआप अपना सवाल अब हिंदी में पूछ सकते हैं।"
    elif preferred_language == "Kannada":
        text_message = "ಕನ್ನಡ ಆಯ್ಕೆ ಮಾಡಿಕೊಂಡಿದ್ದೀರಿ. \nದಯವಿಟ್ಟು ಈಗ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ನೀಡಿ"

    await send_meesage_to_bot(update.effective_chat.id, text_message)

    # await keyword_handler(update, context)

async def keyword_handler(update: Update, context: CallbackContext):
    inline_keyboard_buttons = [
        [InlineKeyboardButton('Toys', callback_data='djp_category_toys')], [InlineKeyboardButton('Games', callback_data='djp_category_games')],
        [InlineKeyboardButton('Stories', callback_data='djp_category_stories')], [InlineKeyboardButton('FlashCards', callback_data='djp_category_flashc')],
        [InlineKeyboardButton('Activities', callback_data='djp_category_activitys')], [InlineKeyboardButton('Manuals', callback_data='djp_category_manuals')]]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)
    await bot.send_message(chat_id=update.effective_chat.id, text="What is your mood today? Select the activity that you want to explore:", reply_markup=reply_markup)

async def preferred_keyword_callback(update: Update, context: CallbackContext):
    callback_query = update.callback_query
    preferred_keyword = callback_query.data
    context.user_data['keyword'] = preferred_keyword
    inline_pitaras_buttons = []
    response = get_all_collection(preferred_keyword)
    for result in response["result"]["content"]:
        inline_pitaras_buttons.append([InlineKeyboardButton(result["name"], callback_data=f'pitara_{result["identifier"]}')])
    reply_markup = InlineKeyboardMarkup(inline_pitaras_buttons)

    await bot.sendMessage(chat_id=update.effective_chat.id, text= "You're making such an awesome choice! we're going to have a blast together!")
    await bot.sendMessage(chat_id=update.effective_chat.id, text=f'Here are the Jadui Pitaras for you to explore... \nMake a wish and open a treasure chest, may the angels be by your side'
                          , reply_markup = reply_markup)
    
async def preferred_pitaras_callback(update: Update, context: CallbackContext):
    callback_query = update.callback_query
    preferred_pitara = callback_query.data.lstrip('pitara_')
    context.user_data['pitara'] = preferred_pitara
    inline_content_buttons = []
    contents = get_metadata_of_children(preferred_pitara)
    for content in contents:
        inline_content_buttons.append([InlineKeyboardButton(content["name"], url=content["artifactUrl"] ,callback_data=f'content_{content["name"]}')])
    reply_markup = InlineKeyboardMarkup(inline_content_buttons)

    await bot.sendMessage(chat_id=update.effective_chat.id, text=f'Are you excited about the contents with in the Pitara? Which one caught your attention?',reply_markup = reply_markup)

async def preferred_content_callback(update: Update, context: CallbackContext):
    callback_query = update.callback_query
    preferred_content = callback_query.data.lstrip('content_')
    context.user_data['content'] = preferred_content
    await bot.sendMessage(chat_id=update.effective_chat.id, text=f'You have chosen *{preferred_content}*.', parse_mode = "Markdown")
    return query_handler

async def converse_handler(update: Update, context: CallbackContext):
    converse = context.user_data.get('converse')
    preferred_language = context.user_data.get('language')
    if converse is None:
        context.user_data['converse'] = True 
    else:
        context.user_data['converse'] = not converse

    text_message = ""
    if preferred_language == "Hindi":
        text_message = "मैं आपकी रुचियों से मेल खाने वाली सामग्री ढूंढने और आपके किसी भी प्रश्न का उत्तर देने में आपकी सहायता कर सकता हूं। कृपया मुझसे अब आप प्रश्न पूछ सकते हैं"
    elif preferred_language == "Kannada":
        text_message = "ನಿಮ್ಮ ಆಸಕ್ತಿಗಳಿಗೆ ಹೊಂದಿಕೆಯಾಗುವ ವಿಷಯವನ್ನು ಹುಡುಕಲು ಮತ್ತು ನೀವು ಹೊಂದಿರುವ ಯಾವುದೇ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಲು ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ದಯವಿಟ್ಟು ನನಗೆ ಒಂದು ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಲು ಹಿಂಜರಿಯಬೇಡಿ."    
    else:
        text_message = 'I can help you find content that aligns with your interests and to answer any questions you may have. Please feel free to ask me a question'

    if not context.user_data['converse']:
        text_message = 'Conversation is now Off. You can not generate questions or summaries.'

    await bot.send_message(chat_id=update.effective_chat.id, text=text_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


class ApiResponse(TypedDict):
    query: str
    answer: str
    source_text: str

class ApiError(TypedDict):
    error: Union[str, requests.exceptions.RequestException]

async def get_query_response(query: str, voice_message_url: str, voice_message_language: str, converse: bool) -> Union[ApiResponse, ApiError]:
    _domain = os.environ['upstream']
    try:
        if voice_message_url is None:
            if voice_message_language == "English":
                params = {
                    'query_string': query,
                    'skip_cache': True,
                    'converse': converse
                }

                url = f'{_domain}/generate_answers?' \
                      + urllib.parse.urlencode(params)
            else:
                params = {
                    'query_text': query,
                    'audio_url': "",
                    'input_language': voice_message_language,
                    'output_format': 'Text',
                    'converse': converse
                }
                url = f'{_domain}/query-using-voice?' \
                      + urllib.parse.urlencode(params)
        else:
            params = {
                'audio_url': voice_message_url,
                'input_language': voice_message_language,
                'output_format': 'Voice',
                'converse': converse
            }
            url = f'{_domain}/query-using-voice?' \
                  + urllib.parse.urlencode(params)

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {'error': e}
    except (KeyError, ValueError):
        return {'error': 'Invalid response received from API'}

async def response_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await query_handler(update, context)

async def query_handler(update: Update, context: CallbackContext):
    voice_message_language = context.user_data.get('language') or 'English'
    converse = context.user_data.get('converse') or False
    voice_message = None
    query = None
    if update.message.text:
        query = update.message.text
    elif update.message.voice:
        voice_message = update.message.voice

    voice_message_url = None
    if voice_message is not None:
        voice_file = await voice_message.get_file()
        voice_message_url = voice_file.file_path
    # await bot.send_message(chat_id=update.effective_chat.id, text=f'Just a few seconds...')
    await bot.sendChatAction(chat_id=update.effective_chat.id, action="typing")
    await handle_query_response(update, query, voice_message_url, voice_message_language, converse)
    return query_handler

def markdown_escape_characters(text):
  """Escapes Markdown characters in the given text.

  Args:
    text: The text to escape.

  Returns:
    A string with all Markdown characters escaped.
  """
  
  escape_chars = {
    "*": "\\*",
    "_": "\\_",
    "`": "\\`",
    "{": "\\{",
    "}": "\\}",
    "[": "\\[",
    "]": "\\]",
    "<": "\\<",
    ">": "\\>",
    "#": "\\#",
    "+": "\\+",
    "-": "\\-",
    "=": "\\=",
    "(": "\\(",
    ")": "\\)",
    ".": "\\.",
    "!": "\\!",
    ">": "\\>",
    "|": "\\|",
  }

  for char in escape_chars:
    text = text.replace(char, escape_chars[char])

  return text

async def handle_query_response(update: Update, query: str, voice_message_url: str, voice_message_language: str, converse: bool):
    response = await get_query_response(query, voice_message_url, voice_message_language, converse)
    if "error" in response:
        await bot.send_message(chat_id=update.effective_chat.id, text='An error has been encountered. Please try again.')
    else:
        answer = response['answer']
        # escaped_text = markdown_escape_characters(answer)
        await bot.send_message(chat_id=update.effective_chat.id, text=answer,  parse_mode = "Markdown")
        if "audio_output_url" in response:
            audio_output_url = response['audio_output_url']
            audio_request = requests.get(audio_output_url)
            audio_data = audio_request.content
            await bot.send_voice(chat_id=update.effective_chat.id, voice=audio_data)

def main() -> None:
    logger.info('################################################')
    logger.info('# Telegram bot name %s', os.environ['botName'])
    logger.info('################################################')
    application = ApplicationBuilder().bot(bot).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler('select_language', language_handler))
    application.add_handler(CommandHandler('select_category', keyword_handler))
    application.add_handler(CommandHandler('enable_conversation', converse_handler))

    application.add_handler(CallbackQueryHandler(preferred_language_callback, pattern=r'lang_\w*'))
    application.add_handler(CallbackQueryHandler(preferred_keyword_callback, pattern=r'djp_\w*'))
    application.add_handler(CallbackQueryHandler(preferred_pitaras_callback, pattern=r'pitara_\w*'))
    application.add_handler(CallbackQueryHandler(preferred_content_callback, pattern=r'content_\w*'))
    
    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, response_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
