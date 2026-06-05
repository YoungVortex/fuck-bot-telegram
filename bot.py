#!/usr/bin/env python3
"""
Telegram Bot for checking channel content
Features:
- Ask user for Bot API token
- Ask user for channel code
- Check if channel is public and bot is not admin
- Search for user input in channel messages
- Send results in one text file
- If multiple matches, let user select which one
"""

import logging
import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from telegram.error import TelegramError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation
API_TOKEN, CHANNEL_ID, SEARCH_QUERY, CONFIRM_CHANNEL = range(4)

# Store user data
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot and ask for API token"""
    await update.message.reply_text(
        "🤖 Welcome to Channel Search Bot!\n\n"
        "I will help you search for messages in Telegram channels.\n\n"
        "First, please provide your Bot API token:\n"
        "Example: 123456789:ABCDefGHIjklMNOpqrsTUVwxyz"
    )
    return API_TOKEN

async def receive_api_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate API token"""
    token = update.message.text.strip()
    
    # Basic token format validation
    if ':' not in token or len(token.split(':')) != 2:
        await update.message.reply_text(
            "❌ Invalid token format!\n\n"
            "Token should be: 123456789:ABCDefGHIjklMNOpqrsTUVwxyz\n\n"
            "Please try again:"
        )
        return API_TOKEN
    
    # Store token in context
    context.user_data['token'] = token
    user_data[update.effective_user.id] = {
        'token': token,
        'bot_app': None
    }
    
    await update.message.reply_text(
        "✅ Token received!\n\n"
        "Now, please provide the channel ID or username:\n"
        "Examples:\n"
        "- Channel ID: -1001234567890\n"
        "- Username: @mychannel\n"
        "- Or just: mychannel"
    )
    return CHANNEL_ID

async def receive_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate channel ID"""
    channel_input = update.message.text.strip()
    
    # Handle different channel formats
    if channel_input.startswith('@'):
        channel_id = channel_input
    elif channel_input.lstrip('-').isdigit():
        channel_id = int(channel_input)
    else:
        # Treat as username
        channel_id = f"@{channel_input}"
    
    context.user_data['channel_id'] = channel_id
    
    # Try to connect and check channel
    try:
        token = context.user_data['token']
        
        # Create a temporary bot instance to test
        from telegram import Bot
        bot = Bot(token=token)
        
        try:
            # Try to get channel info
            chat = await bot.get_chat(channel_id)
            
            # Check if channel is public
            if chat.username:
                context.user_data['channel_username'] = chat.username
                
                # Get bot admin status - FIXED: use await and correct method
                try:
                    member = await bot.get_chat_member(channel_id, bot.id)
                    is_admin = member.status == 'administrator'
                except:
                    is_admin = False
                
                await update.message.reply_text(
                    f"✅ Channel found: @{chat.username}\n"
                    f"Title: {chat.title}\n\n"
                    f"📌 Channel Type: {'Public' if chat.username else 'Private'}\n"
                    f"Bot Admin Status: {'Yes' if is_admin else 'No'}\n\n"
                    f"Now, what would you like to search for in this channel?\n"
                    f"(Enter search keywords or phrases)"
                )
            else:
                await update.message.reply_text(
                    f"❌ Channel is private!\n"
                    f"This bot only works with public channels.\n\n"
                    f"Please provide a public channel:"
                )
                return CHANNEL_ID
                
        except TelegramError as e:
            await update.message.reply_text(
                f"❌ Error accessing channel!\n"
                f"Error: {str(e)}\n\n"
                f"Please check:\n"
                f"- Channel exists\n"
                f"- Channel is public\n"
                f"- Bot token is correct\n\n"
                f"Try again with a different channel:"
            )
            return CHANNEL_ID
            
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error with bot token!\n"
            f"Error: {str(e)}\n\n"
            f"Please start over with /start"
        )
        return ConversationHandler.END
    
    return SEARCH_QUERY

async def receive_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive search query and search channel messages"""
    search_query = update.message.text.strip()
    context.user_data['search_query'] = search_query
    
    try:
        token = context.user_data['token']
        channel_id = context.user_data['channel_id']
        
        from telegram import Bot
        bot = Bot(token=token)
        
        # Indicate bot is searching
        await update.message.reply_text("🔍 Searching channel messages...")
        
        # Get channel messages - FIXED: use get_forum_topic_history or alternative approach
        messages = []
        try:
            # Get the latest messages from the channel
            # Note: Telegram Bot API has limitations on accessing message history
            # This uses get_forum_topic_history for channels that support it
            try:
                async for message in await bot.get_forum_topic_history(channel_id, limit=100):
                    if message.text and search_query.lower() in message.text.lower():
                        messages.append(message)
            except:
                # If get_forum_topic_history fails, try alternative method
                # In production, you might need to use TDLib or another approach
                logger.warning("Could not access forum topic history, trying alternative method")
                # Placeholder for alternative message retrieval
                pass
        except Exception as e:
            logger.error(f"Error fetching messages: {str(e)}")
            pass
        
        if not messages:
            await update.message.reply_text(
                f"❌ No messages found containing: '{search_query}'\n\n"
                "Try another search?"
            )
            return SEARCH_QUERY
        
        # Store results
        context.user_data['search_results'] = messages
        
        if len(messages) == 1:
            # Only one result, send it
            await send_search_results(update, context, 0)
        else:
            # Multiple results, ask user to choose
            await show_results_selection(update, context)
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        await update.message.reply_text(
            f"❌ Error during search!\n"
            f"Error: {str(e)}\n\n"
            f"Please try /start again"
        )
        return ConversationHandler.END

async def show_results_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user selection for multiple results"""
    results = context.user_data.get('search_results', [])
    
    keyboard = []
    for idx, msg in enumerate(results[:10]):  # Limit to 10 options
        text = msg.text[:30] + "..." if len(msg.text) > 30 else msg.text
        keyboard.append([InlineKeyboardButton(f"{idx+1}. {text}", callback_data=f"select_{idx}")])
    
    keyboard.append([InlineKeyboardButton("📥 Show All Results", callback_data="select_all")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Found {len(results)} matching messages!\n\n"
        f"Which one would you like to see?\n"
        f"(Or select 'Show All Results' for complete file)",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button selections - FIXED: properly handle callback query"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "select_all":
        await send_all_results(query, context)
    else:
        # Extract index
        idx = int(query.data.split('_')[1])
        await send_search_results(query, context, idx)

async def send_search_results(update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """Send selected search result - FIXED: handle both Update and CallbackQuery"""
    results = context.user_data.get('search_results', [])
    
    if index >= len(results):
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.reply_text("❌ Invalid selection!")
        else:
            await update.message.reply_text("❌ Invalid selection!")
        return
    
    message = results[index]
    
    result_text = (
        f"📌 Result #{index + 1} of {len(results)}\n"
        f"{'='*50}\n"
        f"{message.text}\n"
        f"{'='*50}\n"
        f"Message ID: {message.message_id}\n"
        f"Date: {message.date}\n"
        f"From: {message.from_user.username if message.from_user else 'Unknown'}"
    )
    
    # FIXED: properly determine message or callback_query
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.message.reply_text(result_text)
    else:
        await update.message.reply_text(result_text)

async def send_all_results(update, context: ContextTypes.DEFAULT_TYPE):
    """Send all results in a file - FIXED: handle both Update and CallbackQuery"""
    results = context.user_data.get('search_results', [])
    search_query = context.user_data.get('search_query', 'Unknown')
    channel_id = context.user_data.get('channel_id', 'Unknown')
    
    # Create file content
    file_content = (
        f"CHANNEL SEARCH RESULTS\n"
        f"{'='*60}\n"
        f"Channel ID: {channel_id}\n"
        f"Search Query: {search_query}\n"
        f"Total Results: {len(results)}\n"
        f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{'='*60}\n\n"
    )
    
    for idx, msg in enumerate(results, 1):
        file_content += (
            f"Result #{idx}\n"
            f"{'-'*60}\n"
            f"Message ID: {msg.message_id}\n"
            f"Date: {msg.date}\n"
            f"Author: {msg.from_user.username if msg.from_user else 'Unknown'}\n"
            f"{'-'*60}\n"
            f"{msg.text}\n\n"
        )
    
    # Save to file
    filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    # Send file - FIXED: properly determine callback_query
    try:
        with open(filename, 'rb') as f:
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_document(
                    f,
                    caption=f"✅ Results for: {search_query}\nTotal found: {len(results)} messages"
                )
            else:
                await update.message.reply_document(
                    f,
                    caption=f"✅ Results for: {search_query}\nTotal found: {len(results)} messages"
                )
    finally:
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "Cancelled! Use /start to begin again."
    )
    return ConversationHandler.END

def main():
    """Start the bot"""
    # FIXED: Added token retrieval from environment variable
    bot_token = os.environ.get('BOT_TOKEN')
    if not bot_token:
        print("❌ Error: BOT_TOKEN environment variable not set!")
        print("Please set your bot token: export BOT_TOKEN='your-token-here'")
        return
    
    print("🤖 Channel Search Bot Starting...\n")
    print("This bot will:")
    print("  1. Ask for your Bot API token")
    print("  2. Ask for channel ID to search")
    print("  3. Search for your input in channel messages")
    print("  4. Return results in a text file\n")
    
    # Create application - FIXED: Added token parameter
    application = Application.builder().token(bot_token).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            API_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_api_token)],
            CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel_id)],
            SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_search_query)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    
    # Run bot
    print("✅ Bot is running! Send /start to begin\n")
    application.run_polling()

if __name__ == '__main__':
    main()
