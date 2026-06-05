# Fuck Bot Telegram 🤖

A powerful Telegram bot for searching and retrieving messages from public channels with advanced filtering and export capabilities.

## Features ✨

- 🔐 **Secure Token Input** - Safely provide your Bot API token
- 🔍 **Channel Search** - Search for messages in public Telegram channels
- 📊 **Smart Results** - View single or multiple matching messages
- 📁 **Export to File** - Download all results as a formatted text file
- ✅ **Validation** - Automatic channel access and permission checking
- 🎯 **Interactive UI** - Easy-to-use inline keyboards for selections

## Requirements 📦

- Python 3.9+
- python-telegram-bot >= 20.0

```bash
pip install python-telegram-bot
```
Installation 🚀
Clone the repository:
bash
git clone https://github.com/YoungVortex/fuck-bot-telegram.git
cd fuck-bot-telegram
Install dependencies:
bash
pip install -r requirements.txt
Run the bot:
bash
python bot.py
Usage 📖
Starting the Bot
Send the /start command to your bot on Telegram.

Step-by-Step Guide
Provide Bot API Token

Code
Your bot token: 123456789:ABCDefGHIjklMNOpqrsTUVwxyz
Provide Channel ID

Channel username: @mychannel
Channel ID: -1001234567890
Or just: mychannel
Enter Search Query

Bot will search for your keywords in channel messages
Example: hello, important, etc.
Select Result

Single result: Auto-displayed
Multiple results: Choose which one to view
View all: Export complete results to file
Commands
/start - Start the bot and begin search
/cancel - Cancel current operation
Output 📄
Search results are saved as search_results_YYYYMMDD_HHMMSS.txt containing:

Channel information
Search query and date
Total number of results
Each message with:
Message ID
Timestamp
Author username
Full message content
Example Output
Code
CHANNEL SEARCH RESULTS
============================================================
Channel ID: @mychannel
Search Query: hello
Total Results: 3
Search Date: 2026-06-05 15:30:45
============================================================

Result #1
------------------------------------------------------------
Message ID: 12345
Date: 2026-06-05 10:00:00
Author: john_doe
------------------------------------------------------------
Hello everyone, welcome to the channel!

Result #2
...
How to Gain Access 🔑
1. Get Your Bot Token
Talk to @BotFather on Telegram
Use /newbot command
Choose a name and username
Copy your token
2. Find Your Channel
Make sure the channel is PUBLIC
Get the channel username (starts with @)
Or find the channel ID (starts with -100)
3. Run the Bot
Execute python bot.py
Send /start to your bot
Input your token and channel ID
Start searching!
Bot Behavior 🎯
Channel Requirements
✅ Channel must be PUBLIC
⚠️ Bot does NOT need to be admin (can search public channels)
✅ Searches last 100 messages for performance
Permissions
Bot can read messages from public channels
No admin rights required
Works even if bot is not a member
File Structure 📁
Code
fuck-bot-telegram/
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
└── README.md          # This file
Creating Requirements File 📋
To create requirements.txt:

bash
pip install python-telegram-bot
pip freeze > requirements.txt
Or manually create it:

Text
python-telegram-bot==20.3
Error Handling ⚠️
Invalid Token Format - Re-enter with correct format
Channel Not Found - Check channel ID/username
Bot Not Authorized - Ensure channel is public
No Results - Try different search terms
Performance Tips ⚡
Search is limited to last 100 messages for speed
Use specific keywords for faster results
Results are temporarily stored in memory
Security Notes 🔒
Never share your bot token publicly
Only search channels you have permission to access
Files are deleted after sending
Troubleshooting 🔧
Bot doesn't respond
Check internet connection
Verify bot token is correct
Make sure bot is running (python bot.py)
Channel not found
Verify channel is public (has @ username)
Check correct channel ID format
Ensure bot token matches
No search results
Try different keywords
Check if messages exist in channel
Ensure search terms match message content
License 📄
This project is open source and available under the MIT License.

Support 💬
For issues or questions:

Check the troubleshooting section
Visit @BotFather for token help
Open an issue on GitHub
Author 👨‍💻
Created by YoungVortex

Happy Searching! 🎉
