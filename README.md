# **ColossusBot**

ColossusBot is a **feature-rich, modular, and database-driven Giga Chad Discord bot** designed for **community management, event automation, and advanced moderation**. It comes with a **modern web dashboard**, centralized database integration, and a highly customizable architecture, making it a powerful tool for both developers and server administrators. This thing is better than every other open-source general purpose bot and it isn't even close.

---

## **Table of Contents**

1. [Key Features](#key-features)
2. [Project Structure](#project-structure)
3. [Detailed Component Overview](#detailed-component-overview)
    - [Database Handling](#databasehandler)
    - [Web Application](#web-dashboard)
    - [Client Handling](#clienthandler)
    - [Event Handling](#event-handling)
4. [Setup Instructions](#setup-instructions)
5. [Development Practices](#development-practices)
6. [Command and Cog Templates](#command-and-cog-templates)
7. [Configuration Options](#configuration-options)
8. [Dependencies](#dependencies)
9. [Contribution Guidelines](#contribution-guidelines)
10. [Future Enhancements](#future-enhancements)
11. [License](#license)

---

## **Key Features**

### **1. Modular Architecture**
- **Cogs**: Extendable modules to handle specific bot features, including commands, events, and integrations.
- **Handlers**: Centralized logic for managing clients, databases, and web interfaces.

### **2. Advanced Database Integration**
- **DatabaseHandler**: A robust solution for managing SQLite or MySQL databases.
- **Schema Management**:
  - Automatic table creation and migration.
  - Centralized query management to maintain clean code.
- **Query Safety**: Fully parameterized queries to prevent SQL injection.

### **3. Real-Time Event Handling**
- **listeners**:
  - NSFW detection and alerts.
  - Flagged keyword detection.
  - Automated ticket and channel management.
- **Task Loops**: Automated background tasks to handle repetitive or time-sensitive actions.

### **4. AI-Powered Features**
- Integration with OpenAI’s GPT models for:
  - Moderation insights.
  - Natural language-based responses.
  - Sentiment analysis.

### **5. Web Dashboard**
- **Flask-Powered**: Lightweight and responsive web dashboard.
- **Features**:
  - Real-time log viewing.
  - Bot status and command inspection.
  - Configuration of settings via APIs.

### **6. Scalability and Flexibility**
- Fully customizable with `.env` configurations.
- Modular codebase for easy integration of new features.

---

## **Project Structure**

Below is the directory structure of ColossusBot:

```plaintext
ColossusBot/
├── .env
├── .gitignore
├── config.py
├── LICENSE
├── main.py
├── README.md
├── requirements.txt
├── runtime.txt
├── colossusCogs/
│   ├── admin_commands.py
│   ├── aichatbot.py
│   ├── channel_access_manager.py
│   ├── channel_archiver.py
│   ├── _cog_template.py
│   ├── .gitignore/
│   │   └── .gitkeep
│   ├── config/
│   │   └── .gitkeep
│   └── listeners/
│       ├── active_alert_checker.py
│       ├── flagged_words_alert.py
│       ├── nsfw_checker.py
│       ├── repeated_message_alert.py
│       └── Flags/
│           ├── flagged_words.py
│           └── nsfw_words.py
├── commands/
│   ├── active.py
│   ├── catfish.py
│   ├── define.py
│   ├── google.py
│   ├── image.py
│   ├── keywords.py
│   ├── purge_user.py
│   ├── restrict_role.py
│   ├── say.py
│   ├── suggest.py
│   ├── todo.py
│   ├── vibecheck.py
│   ├── vote.py
│   ├── wiki.py
│   ├── _command_template.py
│   └── helpers/
│       └── progress_bar.py
├── dashboard/
│   ├── renderer.py
│   ├── static/
│   │   ├── icon.ico
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js
│   └── templates/
│       ├── base.html
│       ├── console.html
│       └── index.html
└── handlers/
    ├── client_handler.py
    ├── commands_handler.py
    ├── database_handler.py
    ├── event_handler.py
    └── web_handler.py
```

---

## **Detailed Component Overview**

### **DatabaseHandler**

The `DatabaseHandler` is a **centralized solution for managing SQL queries** and database schema. It supports **SQLite** (default) and **MySQL**, ensuring scalability for both development and production environments.

#### **Key Features**
1. **Schema Management**:
   - Automatically creates tables on startup.
   - Handles schema migrations when tables are updated.
2. **Centralized Queries**:
   - Encapsulates all SQL logic to keep other files clean.
   - Use functions like `execute`, `fetchone`, and `fetchall` for consistent query execution.
3. **Thread-Safe**:
   - Supports asynchronous connections for high-performance environments.

#### **Example Usage**
Define a schema in `setup` and access it from other components:
```python
# Create a guild configuration table
async def setup(self):
    query = """
        CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            log_channel_id INTEGER,
            owner_id INTEGER
        )
    """
    await self.execute(query)

# Insert or update a guild's configuration
async def set_guild_config(self, guild_id: int, log_channel_id: int, owner_id: int):
    query = """
        INSERT INTO guild_config (guild_id, log_channel_id, owner_id)
        VALUES (?, ?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET
        log_channel_id = ?, owner_id = ?
    """
    await self.execute(query, (guild_id, log_channel_id, owner_id, log_channel_id, owner_id))
```

---

### **Web Dashboard**

The dashboard provides a **Flask-based UI** for monitoring and controlling ColossusBot.

#### **Features**
- **Index Page** (`index.html`):
  - Welcome page with links to logs and status pages.
- **Log Viewer** (`console.html`):
  - Real-time display of bot logs.
  - Toggle autoscroll for better usability.
- **Dynamic Updates**:
  - Powered by AJAX calls using `script.js`.

#### **Styling**
- **Responsive Design**:
  - Uses `style.css` for consistent styling across pages.
- **Key Components**:
  - Sticky header for easy navigation.
  - Scrollable log viewer with monospace font for readability.

---

### **ClientHandler**

The `ClientHandler` manages **Discord bot initialization**, including the setup of:
- **Intents**: Determines what events the bot listens to.
- **Command Prefix**: Configurable via `.env`.

---

### **Event Handling**

The `EventHandler` organizes listeners for:
1. **Message Events**:
   - NSFW detection.
   - Flagged keyword alerts.
2. **Reaction Events**:
   - Custom behavior on specific emoji reactions.

---

## **Setup Instructions**

### **Prerequisites**

To run ColossusBot, you will need the following:

1. **Python 3.8 or higher**:
   - Ensure `pip` is installed for managing dependencies.
2. **Discord Bot Token**:
   - Create a bot application in the [Discord Developer Portal](https://discord.com/developers/applications).
   - Copy the token for use in the `.env` file.
3. **Database Setup**:
   - SQLite is the default option (no additional setup required).
   - For MySQL, ensure you have a MySQL server running and provide the appropriate credentials in the `.env` file.

---

### **Installation Steps**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/ColossusBot.git
   cd ColossusBot
   ```

2. **Install Dependencies**:
   Install the required Python libraries using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file and provide the necessary configuration:
   ```env
   BOT_TOKEN=your-discord-bot-token
   BOT_PREFIX=!
   DB_ENGINE=sqlite
   DB_NAME=colossusbot.db
   OPENAI_API_KEY=your-openai-api-key (optional)
   ```

4. **Launch the Bot**:
   Start the bot with:
   ```bash
   python main.py
   ```

---

### **Configuration Options**

ColossusBot is configured using environment variables stored in the `.env` file.

#### **Core Variables**

| Variable         | Description                                    | Default Value         |
|------------------|------------------------------------------------|-----------------------|
| `BOT_TOKEN`      | Discord bot token.                            | Required              |
| `BOT_PREFIX`     | Command prefix for bot commands.              | `!`                  |
| `DB_ENGINE`      | Database engine (`sqlite` or `mysql`).        | `sqlite`             |
| `DB_NAME`        | SQLite file name or MySQL database name.      | `colossusbot.db`     |
| `DB_HOST`        | MySQL server hostname.                        | `localhost`          |
| `DB_USER`        | MySQL username.                               | `root`               |
| `DB_PASSWORD`    | MySQL password.                               | Empty                |
| `OPENAI_API_KEY` | API key for OpenAI features.                  | None                 |

#### **Local Overrides**

For development, create an `.env.local` file to override variables. These will take precedence over `.env`.

---

## **Development Practices**

### **Best Practices for Development**

1. **Use the Provided Templates**:
   - Leverage the `_command_template.py` and `_cog_template.py` files for creating new commands and features.
   - Keep logic modular to avoid duplicating code.

2. **Centralize Database Operations**:
   - Avoid writing SQL queries directly in cogs or commands.
   - Use the `DatabaseHandler` for consistent and maintainable query management.

3. **Separate Logic and Presentation**:
   - Keep UI logic (dashboard HTML/CSS) separate from backend operations (handlers).
   - Use the `Renderer` class to manage HTML rendering.

4. **Logging**:
   - Use the built-in logging framework to log errors and events.
   - Avoid printing directly to the console unless necessary for debugging.

---

### **Command and Cog Templates**

#### **Command Template**

The `commands/` directory is for **simple, self-contained commands**. Use the `_command_template.py` to create new commands.

Example:
```python
"""
Template Command: Example Command for ColossusBot
-------------------------------------------------
Use this template to create and add new commands to the bot.
"""

from discord.ext import commands
from discord import Embed
import logging

# Initialize logging for debugging purposes
logger = logging.getLogger("ColossusBot")

class CommandTemplate(commands.Cog):
    """
    A template cog for creating commands in ColossusBot.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the CommandTemplate cog.

        :param client: The Discord bot client instance.
        """
        self.client = client
        logger.info("CommandTemplate initialized successfully.")

    @commands.command(name="example", help="An example command to demonstrate functionality.")
    async def example_command(self, ctx: commands.Context, *, input_text: str = "Default Response") -> None:
        """
        Responds with a user-provided message or a default response.

        :param ctx: The command context.
        :param input_text: The input text provided by the user (optional).
        """
        logger.info(f"Executing 'example_command' with input: {input_text}")

        # Create an embed to display the response
        embed = Embed(
            title="Example Command",
            description=f"You said: {input_text}",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name="another_example", help="Another example command to show usage with arguments.")
    async def another_example_command(self, ctx: commands.Context, number: int) -> None:
        """
        Multiplies a number by 2 and returns the result.

        :param ctx: The command context.
        :param number: A number provided by the user.
        """
        logger.info(f"Executing 'another_example_command' with number: {number}")

        result = number * 2
        await ctx.send(f"Double of {number} is {result}!")


async def setup(client: commands.Bot) -> None:
    """
    Registers the CommandTemplate cog with the bot.

    :param client: The Discord bot client instance.
    """
    logger.info("Setting up CommandTemplate cog...")
    await client.add_cog(CommandTemplate(client))
    logger.info("CommandTemplate cog setup complete.")
```

---

#### **Cog Template**

For **complex features with database or event integrations**, use the `_cog_template.py`.

Example:
```python
"""
Template Cog for ColossusBot
----------------------------
Use this template for creating new cogs with handler integration.
"""

from discord.ext import commands
import logging
from handlers.database_handler import DatabaseHandler

logger = logging.getLogger("ColossusBot")


class CogTemplate(commands.Cog):
    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        self.client = client
        self.db_handler = db_handler

    @commands.command(name="example", help="An example command with database integration.")
    async def example_command(self, ctx: commands.Context) -> None:
        await self.db_handler.insert_record("example_table", {"key": "value"})
        await ctx.send("Record added to the database.")

    async def background_task(self) -> None:
        records = await self.db_handler.fetch_records("example_table")
        logger.info(f"Fetched {len(records)} records from example_table.")


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    await client.add_cog(CogTemplate(client, db_handler))
```

---

### **Web Dashboard**

The web dashboard provides a **real-time interface** for managing and monitoring ColossusBot.

#### **Features**
1. **Index Page (`index.html`)**:
   - Displays a welcome message and links to other sections.
2. **Console Logs (`console.html`)**:
   - Shows real-time logs with a toggle for autoscroll.
3. **API Endpoints**:
   - `/api/status`: Returns bot status (online, latency, guild count).
   - `/api/console`: Fetches the latest console logs.
   - `/api/commands`: Returns metadata for all available commands.

---

## **Dependencies**

ColossusBot relies on the following Python libraries:

| Dependency         | Purpose                                   |
|--------------------|-------------------------------------------|
| `aiohttp`          | Asynchronous HTTP client library.        |
| `aiosqlite`        | Async SQLite integration.                |
| `aiomysql`         | Async MySQL integration.                 |
| `asyncio`          | Async programming framework.             |
| `Flask`            | Web dashboard framework.                 |
| `googlesearch-python` | Google search API wrapper.            |
| `numpy`            | Numerical computations.                  |
| `openai`           | Integration with OpenAI's API.           |
| `Pillow`           | Image processing and manipulation.       |
| `vaderSentiment`   | Sentiment analysis.                      |
| `wikipedia-api`    | Modern Wikipedia API wrapper.            |

To install dependencies, run:
```bash
pip install -r requirements.txt
```

---

## **Contribution Guidelines**

1. Fork the repository.
2. Create a feature branch.
3. Use templates in `commands/` or `colossusCogs/`.
4. Ensure all new database queries use the `DatabaseHandler`.
5. Submit a pull request with a detailed description.

---

## **Future Enhancements**

- **Bot Analytics**:
   - Add visualizations for message activity and command usage.
- **Docker Support**:
   - Streamline deployment with containerization.
- **Plugin System**:
   - Enable admins to dynamically add or remove cogs via the dashboard.
- **Multi-language Support**:
   - Add localization options for the dashboard and commands.

---

## **License**

ColossusBot is licensed under the MIT License. See `LICENSE` for details.
