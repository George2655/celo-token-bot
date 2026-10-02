# CELO Token Bot

A lightweight Telegram bot that tracks a token price on the Celo network using the Dexscreener API.

The bot automatically checks the latest token price and sends updates to subscribed Telegram users.

## Features

- Live token price from Dexscreener
- Celo network support
- Automatic Telegram price updates
- `/start` command to subscribe
- `/stop` command to unsubscribe
- `/price` command to check the current price
- Background price monitoring
- Environment variable support for sensitive credentials

## Tech Stack

- Python
- Flask
- Telegram Bot API
- Dexscreener API

## Installation

Clone the repository:

```bash
git clone https://github.com/George2655/celo-token-bot.git
cd celo-token-bot
