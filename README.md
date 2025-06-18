# Vanna1 Telegram Bot

This project is a Telegram bot that answers questions about a DVD rental database using AI and SQL. It leverages OpenAI, LangChain, and a Postgres database, and is designed to be run as a simple Python script.

## Features

- Connects to a Postgres database with a DVD rental schema.
- Uses OpenAI for natural language understanding and answer generation.
- Answers user questions via Telegram chat.
- Trains on DDL, documentation, and sample SQL queries for improved accuracy.

## Requirements

- Python 3.8+
- A Postgres database (with the DVD rental schema)
- Telegram Bot Token
- OpenAI API Key

## Installation

1. **Clone the repository** and navigate to the `vanna1` directory.

2. **Install dependencies**:
    ```sh
    pip install python-telegram-bot python-dotenv langchain-openai langchain-core
    ```

3. **Set up environment variables**:

    - Copy `.env-sample` to `.env`:
      ```sh
      cp .env-sample .env
      ```
    - Fill in your credentials in `.env`:
      - `OPENAI_API_KEY`
      - `OPENAI_MODEL_NAME`
      - `POSTGRES_HOST`
      - `POSTGRES_DB_NAME`
      - `POSTGRES_USER`
      - `POSTGRES_PASSWORD`
      - `POSTGRES_PORT`
      - `TELEGRAM_BOT_TOKEN`

4. **Ensure your Postgres database is running and accessible.**

## Usage

To start the Telegram bot, run:

```sh
cd vanna1
python3 telegram_bot.py
```

The bot will train itself on the schema and documentation if needed, then listen for messages on Telegram.

## File Structure

- [`telegram_bot.py`](vanna1/telegram_bot.py): Main entry point for the Telegram bot.
- [`vanna_extractor.py`](vanna1/vanna_extractor.py): Handles AI and database logic.
- [`constants.py`](vanna1/constants.py): Contains schema, documentation, and sample queries.
- [`sentence_former.py`](vanna1/sentence_former.py): Formats answers using LangChain.
- [`utils.py`](vanna1/utils.py): Utility functions.
- `.env-sample`: Example environment configuration.

## Notes

- Make sure to keep your `.env` file secure and **never commit it to version control**.
- The bot will print logs to the console for debugging and training status.

## License

MIT License

---

Inspired by the [DVD Rental sample database](https://neon.com/postgresqltutorial/dvdrental.zip).