# **ColossusBot**

![alt text](ColossusBot.webp)

ColossusBot is a **feature-rich, modular, and database-driven Giga Chad Discord bot** designed for **community management, event automation, and advanced moderation**. It comes with a **modern web dashboard**, **an API**, **centralized database integration**, and a **highly customizable state-of-the-art architecture**, making it a powerful tool for both developers and server administrators. This thing is better than every other open-source general-purpose bot and it isn't even close.

---

- [**ColossusBot**](#colossusbot)
  - [**Key Features**](#key-features)
    - [**1. Modular Architecture**](#1-modular-architecture)
    - [**2. Advanced Database Integration**](#2-advanced-database-integration)
    - [**3. Real-Time Event Handling**](#3-real-time-event-handling)
    - [**4. AI-Powered Features**](#4-ai-powered-features)
    - [**5. Web Dashboard**](#5-web-dashboard)
    - [**6. Scalability and Flexibility**](#6-scalability-and-flexibility)
  - [**Security Features**](#security-features)
    - [**How ColossusBot Protects Your Server**:](#how-colossusbot-protects-your-server)
  - [**Project Structure**](#project-structure)
  - [**Detailed Component Overview**](#detailed-component-overview)
    - [**Client Handler**](#client-handler)
    - [**Database Handler**](#database-handler)
      - [**Key Features**](#key-features-1)
      - [**Example Usage**](#example-usage)
    - [**Event Handler**](#event-handler)
      - [**Key Features**](#key-features-2)
        - [**1. Message Events**](#1-message-events)
        - [**2. Reaction Events**](#2-reaction-events)
        - [**3. Periodic Tasks**](#3-periodic-tasks)
    - [**Web Dashboard**](#web-dashboard)
      - [**Key Features**](#key-features-3)
  - [**Dependencies**](#dependencies)
  - [**Setup Instructions**](#setup-instructions)
    - [**Prerequisites**](#prerequisites)
  - [**Installation Steps**](#installation-steps)
  - [**Development Practices**](#development-practices)
    - [**Best Practices for Development**](#best-practices-for-development)
    - [**Command and Cog Templates**](#command-and-cog-templates)
      - [**Command Template**](#command-template)
      - [**Cog Template**](#cog-template)
  - [**Configuration Options**](#configuration-options)
    - [**Core Variables**](#core-variables)
  - [**Cog Reference**](#cog-reference)
    - [**1. `admin_commands.py`**](#1-admin_commandspy)
    - [**2. `aichatbot.py`**](#2-aichatbotpy)
    - [**3. `channel_access_manager.py`**](#3-channel_access_managerpy)
    - [**4. `channel_archiver.py`**](#4-channel_archiverpy)
    - [**5. `ticket_checker.py`**](#5-ticket_checkerpy)
    - [**6. `listeners/`**](#6-listeners)
      - [**1. `active_alert_checker.py`**](#1-active_alert_checkerpy)
      - [**2. `flagged_words_alert.py`**](#2-flagged_words_alertpy)
      - [**3. `nsfw_checker.py`**](#3-nsfw_checkerpy)
      - [**4. `repeated_message_alert.py`**](#4-repeated_message_alertpy)
      - [**How Reactions Work in Listeners**](#how-reactions-work-in-listeners)
  - [**Command Reference**](#command-reference)
    - [**1. `!active`**](#1-active)
    - [**2. `!catfish`**](#2-catfish)
    - [**3. `!define`**](#3-define)
    - [**4. `!google`**](#4-google)
    - [**5. `!image`**](#5-image)
    - [**6. `!keywords`**](#6-keywords)
    - [**7. `!purge_user`**](#7-purge_user)
    - [**8. `!restrict_role`**](#8-restrict_role)
    - [**9. `!say`**](#9-say)
    - [**10. `!suggest`**](#10-suggest)
    - [**11. `!todo`**](#11-todo)
    - [**12. `!vibecheck`**](#12-vibecheck)
    - [**13. `!vote`**](#13-vote)
    - [**14. `!wiki`**](#14-wiki)
  - [**Contributing**](#contributing)
  - [**License**](#license)

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

## **Security Features**

**Security** is one of the **biggest selling points** of ColossusBot. In the world of self-hosted bots, **Discord** provides very little protection once a server or account is compromised. With ColossusBot, however, you have complete control over your server's security, especially in the event that an admin or mod account becomes compromised.

### **How ColossusBot Protects Your Server**:

1. **Self-Hosting with Elevated Bot Permissions**:
   ColossusBot is designed to be self-hosted, giving you full control over its configuration. Once hosted, you can assign the bot the **highest role** in your server, giving it ultimate control over sensitive server actions. This ensures that the bot can manage potentially dangerous situations that would otherwise be beyond its control.

2. **Event Listeners to Prevent Malicious Actions**:
   ColossusBot uses **event listeners** to detect any suspicious activity, such as changes to roles, permissions, or server settings. These event listeners are built to **prevent compromised mods or admins from causing harm**—for instance, it will stop malicious users from:
   - Changing key server configurations.
   - Kicking or banning high-level users.
   - Deleting important channels or messages.
   - Mass moderation actions by hacked accounts.
   
   This built-in protection is an essential feature, as it provides a safeguard against those who have taken control of admin privileges but cannot take full control of the bot.

3. **Server Ownership and Role Hierarchy Best Practices**:
   - **Lock the server behind a burner account**: A **burner account** should be used as a first line of defense to **lock down** access to your server. This account is used to prevent anyone from gaining unauthorized access or making drastic changes to server settings.
   
   - **Rotate ownership regularly**: **Rotate bot ownership** periodically to ensure it remains under the control of a trusted individual. This can help mitigate risks from potential internal threats or external hacks.

   - **Bot Role Above Everyone Except the Owner**: The bot's role should be positioned **above** all other users, including moderators and admins. This ensures that only the bot itself (or the owner) can execute important actions such as:
     - Preventing server nuking.
     - Reversing permission changes made by compromised accounts.

   - **Use your main account with limited permissions**: After setting up the bot with a high-level role, the **main user** should place their main account **below the bot** in the role hierarchy and limit permissions. This way, even if the main account is compromised, the bot cannot be controlled or its actions undone by malicious users.

4. **A Full Security Barrier Against Hacks**:
   With these techniques, ColossusBot helps ensure that **hackers cannot easily take over or nuke your server**. ColossusBot will effectively act as an additional line of defense, providing real-time monitoring of the server’s activities and mitigating risks before they escalate.

By combining these self-hosting best practices with the bot's built-in event listeners and role configurations, **ColossusBot offers robust protection against the threats of server takeover** and helps ensure the integrity of your server.

## **Project Structure**

Below is the directory structure of ColossusBot:

```plaintext
ColossusBot/
├── .env                          # Default environment variables (editable)
├── .gitignore                    # Excluded files and directories
├── config.py                     # Centralized bot configuration
├── FolderStructure.py            # Tool for analyzing folder structure
├── keep_alive.py                 # Keeps the bot process alive in hosted environments
├── LICENSE                       # License for the project
├── main.py                       # Entry point for the bot
├── README.md                     # Documentation
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Runtime environment file for hosting
├── colossusCogs/                 # Modular bot features (cogs)
│   ├── _cog_template.py          # Template for creating new cogs
│   ├── admin_commands.py         # Administrative commands (mute, kick, warn, etc.)
│   ├── aichatbot.py              # AI-powered mod chatbot
│   ├── channel_access_manager.py # Manage channel access
│   ├── channel_archiver.py       # Archive inactive channels
│   ├── listeners.py              # Event listeners for message monitoring
│   ├── manual.py                 # Manual moderation tools
│   ├── pings.py                  # Ping monitoring
│   ├── roles.py                  # Role management commands
│   ├── ticket_checker.py         # Inactivity monitoring for ticket channels (off by default)
│   ├── utility.py                # Miscellaneous utility commands
│   ├── .gitignore/
│   │   └── .gitkeep              # Placeholder for ignored content
│   ├── Config/
│   │   └── activeAlertsConfig.py # Configuration for active alerts
│   └── Listeners/
│       ├── active_alert_checker.py  # Checks for active alerts
│       ├── flagged_words_alert.py   # Detects flagged words
│       ├── nsfw_checker.py          # Scans for NSFW content
│       ├── repeated_message_alert.py # Detects repeated messages
│       └── Flags/
│           ├── flagged_words.py      # List of flagged words
│           └── nsfw_words.py         # List of NSFW words
├── commands/                     # Command-specific handlers (standalone and simple features)
│   ├── _command_template.py      # Template for creating new commands
│   ├── active.py                 # Active channel commands
│   ├── catfish.py                # Catfish detection commands
│   ├── define.py                 # Word definition commands
│   ├── google.py                 # Google search integration
│   ├── image.py                  # Image manipulation commands
│   ├── keywords.py               # Keyword management commands
│   ├── purge_user.py             # User message purge commands
│   ├── restrict_role.py          # Role restriction commands
│   ├── say.py                    # Echo a message
│   ├── suggest.py                # Suggestions command
│   ├── todo.py                   # Task management
│   ├── vibecheck.py              # Vibe check command
│   ├── vote.py                   # Voting system
│   ├── wiki.py                   # Wikipedia search
│   └── helpers/
│       └── progress_bar.py       # Progress bar generation utility
├── dashboard/                    # Web interface and templates
│   ├── renderer.py               # Flask template renderer
│   ├── __init__.py               # Python module indicator
│   ├── static/
│   │   ├── icon.ico              # Favicon
│   │   ├── css/
│   │   │   └── style.css         # Dashboard styles
│   │   └── js/
│   │       └── script.js         # Dashboard scripts
│   └── templates/
│       ├── base.html             # Base HTML layout
│       ├── index.html            # Dashboard home page
│       └── console.html          # Console logs view
└── handlers/                     # Core backend logic
    ├── client_handler.py         # Initializes the bot client
    ├── commands_handler.py       # Routes and executes commands
    ├── database_handler.py       # Handles database trans.
    ├── event_handler.py          # Handles Discord events
    └── web_handler.py            # Manages web interface
```

## **Detailed Component Overview**

### **Client Handler**

The `ClientHandler` manages **Discord bot initialization**, including the setup of:
- **Intents**: Determines what events the bot listens to.
- **Command Prefix**: Configurable via `.env`.

### **Database Handler**

The `DatabaseHandler` is a **centralized solution for managing SQL queries** and database schema. It supports **SQLite** (default) and **MySQL**, ensuring scalability for both development and production environments.

#### **Key Features**
1. **Schema Management**
2. **Centralized Queries**
3. **Thread-Safe**
4. **Flexible Database Support**

#### **Example Usage**
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

### **Event Handler**

The `EventHandler` cog serves as the centralized controller for handling a wide variety of Discord events. It listens to key events, such as incoming messages and reactions, and routes them to the appropriate listeners or modules for processing.

#### **Key Features**

1. **Message Events**: Process messages through various listeners.
2. **Reaction Events**: Respond to staff reactions on alerts.
3. **Periodic Tasks**: Includes checks for ticket channel inactivity. By default, ticket monitoring is disabled. Use the `!ticketmonitor` command to enable or disable this feature.

##### **1. Message Events**

- **listeners** like `NSFWChecker`, `FlaggedWordsAlert`, and `RepeatedMessageAlert` process and respond to messages in real-time.

##### **2. Reaction Events**

- Allows staff to approve, dismiss, or escalate actions on detected content via reactions.

##### **3. Periodic Tasks**

- Checks ticket channels (named `ticket-*`) for inactivity every 5 minutes.
- If inactive for more than 60 minutes, the bot can close and remove the ticket channel.
- This ticket monitoring is disabled by default. Enable it with `!ticketmonitor on`.

### **Web Dashboard**

The web dashboard provides a **real-time interface** for managing and monitoring ColossusBot.

#### **Key Features**

1. **Index Page (index.html)**
2. **Console Logs (console.html)**
3. **API Endpoints**

## **Dependencies**

| Dependency           | Purpose                                          |
|----------------------|--------------------------------------------------|
| aiohttp              | Asynchronous HTTP client library.                |
| aiosqlite            | Async SQLite integration.                        |
| aiomysql             | Async MySQL integration.                         |
| asyncio              | Async programming framework.                     |
| Flask                | Web dashboard framework.                         |
| googlesearch-python  | Google search API wrapper.                       |
| numpy                | Numerical computations.                          |
| openai               | Integration with OpenAI's API.                   |
| Pillow               | Image processing and manipulation.               |
| vaderSentiment       | Sentiment analysis.                              |
| wikipedia-api        | Modern Wikipedia API wrapper.                    |

To install dependencies, run:
```bash
pip install -r requirements.txt
```

## **Setup Instructions**

### **Prerequisites**

1. **Python 3.8 or higher**
2. **Discord Bot Token** from [Discord Developer Portal](https://discord.com/developers/applications).
3. **Database Setup**:
   - SQLite (default) requires no additional setup.
   - MySQL requires configuring credentials in `.env`.

## **Installation Steps**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/ColossusBot.git
   cd ColossusBot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   In `.env`:
   ```env
   BOT_TOKEN=your-discord-bot-token
   BOT_PREFIX=!
   DB_ENGINE=sqlite
   DB_NAME=colossusbot.db
   OPENAI_API_KEY=your-openai-api-key (optional)
   ```

4. **Launch the Bot**:
   ```bash
   python main.py
   ```

## **Development Practices**

### **Best Practices for Development**

1. **Use the Provided Templates** for commands and cogs.
2. **Centralize Database Operations** via `DatabaseHandler`.
3. **Separate Logic and Presentation**.
4. **Logging**: Use built-in logging for traceability.

### **Command and Cog Templates**

#### **Command Template**

Use `_command_template.py` for simple, self-contained commands.

#### **Cog Template**

Use `_cog_template.py` for features that require database or event integration.

## **Configuration Options**

### **Core Variables**

| Variable       | Description                                           | Default            |
|----------------|-------------------------------------------------------|--------------------|
| `BOT_TOKEN`    | The token for the Discord bot.                        | None               |
| `BOT_PREFIX`   | The prefix for bot commands.                          | `!`                |
| `DB_ENGINE`    | Database type (`sqlite` or `mysql`).                  | `sqlite`           |
| `DB_NAME`      | SQLite file or MySQL database name.                   | `colossusbot.db`   |
| `OPENAI_API_KEY` | API key for OpenAI integrations (optional).         | None               |

## **Cog Reference**

### **1. `admin_commands.py`**

Provides administrative commands for moderation.

### **2. `aichatbot.py`**

Integrates AI-based responses and moderation insights.

### **3. `channel_access_manager.py`**

Manages access control and permissions for channels.

### **4. `channel_archiver.py`**

Archives and unarchives channels based on activity.

### **5. `ticket_checker.py`**

Toggles the periodic ticket inactivity monitoring. By default, ticket monitoring is **off**.

**Usage**:
```plaintext
!ticketmonitor on
!ticketmonitor off
!ticketmonitor
```

- `!ticketmonitor` with no arguments shows the current status (on/off).
- `on` enables the monitoring of `ticket-*` channels every 5 minutes.
- `off` disables the monitoring.

### **6. `listeners/`**

**Listeners** react to events such as messages, reactions, and periodic tasks:

#### **1. `active_alert_checker.py`**

- Logs channel activity when it becomes active again after inactivity.

#### **2. `flagged_words_alert.py`**

- Detects messages containing flagged words.
- Sends alerts to staff with reaction options to approve or dismiss.
- Penalties: ⚠️ (warn), 🔇 (mute), 👢 (kick), 🔨 (ban).

#### **3. `nsfw_checker.py`**

- Detects NSFW content.
- Alerts staff, allowing them to approve or dismiss actions.
- Penalties: ⚠️ (warn), 🔇 (mute), 👢 (kick), 🔨 (ban).

#### **4. `repeated_message_alert.py`**

- Detects repeated messages across servers.
- Alerts staff to take action via reactions.
- Penalties: ⚠️ (warn), 🔇 (mute), 👢 (kick), 🔨 (ban).

#### **How Reactions Work in Listeners**

- **✅**: Confirm the alert action.
- **❌**: Dismiss the alert.
- **⚠️**: Warn the user.
- **🔇**: Mute the user.
- **👢**: Kick the user.
- **🔨**: Ban the user.

## **Command Reference**

### **1. `!active`**

Shows the bot's current active status.

### **2. `!catfish`**

Searches for catfish-related terms.

### **3. `!define`**

Defines a word using an online dictionary.

### **4. `!google`**

Performs a Google search.

### **5. `!image`**

Fetches an image related to a search term.

### **6. `!keywords`**

Displays detected flagged keywords.

### **7. `!purge_user`**

Purges messages from a specified user over a timeframe.

### **8. `!restrict_role`**

Restricts a user’s role permissions.

### **9. `!say`**

Bot repeats the given message.

### **10. `!suggest`**

Records a user suggestion.

### **11. `!todo`**

Adds a task to the bot’s to-do list.

### **12. `!vibecheck`**

Analyzes the sentiment of recent chat activity.

### **13. `!vote`**

Creates a voting poll.

### **14. `!wiki`**

Fetches a Wikipedia summary.

## **Contributing**

Contributions are welcome! Use the provided templates for commands and cogs, and ensure all changes align with the project's style and best practices.

## **License**

ColossusBot is open-source and released under the MIT License.
```