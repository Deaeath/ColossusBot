# **ColossusBot**

ColossusBot is a **feature-rich, modular, and database-driven Giga Chad Discord bot** designed for **community management, event automation, and advanced moderation**. It comes with a **modern web dashboard**, centralized database integration, and a highly customizable architecture, making it a powerful tool for both developers and server administrators. This thing is better than every other open-source general-purpose bot and it isn't even close.

---

## **Table of Contents**

1. [Key Features](#key-features)
1. [Project Structure](#project-structure)
1. [Detailed Component Overview](#detailed-component-overview)
    - [Database Handling](#databasehandler)
    - [Web Application](#web-dashboard)
    - [Client Handling](#clienthandler)
    - [Event Handling](#event-handling)
1. [Setup Instructions](#setup-instructions)
1. [Development Practices](#development-practices)
1. [Command and Cog Templates](#command-and-cog-templates)
1. [Cog Reference](#cog-reference)
1. [Command Reference](#command-reference)
1. [Configuration Options](#configuration-options)
1. [Dependencies](#dependencies)
1.. [Contribution Guidelines](#contribution-guidelines)
1.. [Future Enhancements](#future-enhancements)
1.. [License](#license)

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

---

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

---

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
│   ├── aichatbot.py              # AI-powered chatbot and moderation
│   ├── channel_access_manager.py # Manage user access to categories and channels
│   ├── channel_archiver.py       # Archive inactive channels
│   ├── listeners.py              # Event listeners for message monitoring
│   ├── manual.py                 # Manual moderation tools
│   ├── pings.py                  # Ping monitoring
│   ├── roles.py                  # Role management commands
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
│   ├── __init__.py               # Marks the directory as a Python module
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
    ├── database_handler.py       # Database operations
    ├── event_handler.py          # Handles Discord events
    └── web_handler.py            # Manages web interface routes and APIs
```

---

## **Detailed Component Overview**

---

### **DatabaseHandler**

The `DatabaseHandler` is a **centralized solution for managing SQL queries** and database schema. It supports **SQLite** (default) and **MySQL**, ensuring scalability for both development and production environments.

#### **Key Features**
1. **Schema Management**:
   - Automatically creates and manages tables on startup, ensuring necessary structures are in place.
   - Handles schema migrations when tables or columns are updated, ensuring smooth transitions.
2. **Centralized Queries**:
   - Encapsulates all SQL logic, keeping other parts of the codebase clean and focused on business logic.
   - Use functions like `execute`, `fetchone`, and `fetchall` for consistent query execution across the bot.
3. **Thread-Safe**:
   - Supports asynchronous connections, allowing for high-performance environments with minimal blocking operations.
4. **Flexible Database Support**:
   - Seamlessly supports both SQLite and MySQL, offering scalability from small to large production environments.
   - Automatically adjusts to the database engine provided in the configuration (SQLite or MySQL).

#### **Example Usage**
Define a schema in `setup()` and access it from other components:

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

Thank you for sharing the code! Based on this context, here's an updated and detailed **Event Handling** section, tailored to reflect the exact functionality in the code you've provided. I'll ensure the description matches the structure and flow of the `EventsHandler` class and its listeners.

---

### **Event Handling**

The `EventHandler` cog serves as the centralized controller for handling a wide variety of Discord events. It listens to key events, such as incoming messages and reactions, and routes them to the appropriate listeners or modules for processing. This architecture enables the bot to react to different types of interactions in an organized and modular way.

The `EventHandler` also runs periodic tasks, such as checking the activity of ticket channels, ensuring the bot can handle long-running processes while still focusing on real-time event handling.

#### **1. Message Events**

- **Message Processing**:
  The `EventHandler` listens for all incoming messages across the bot's active guilds. When a message is received:
  - It is routed through multiple specialized listeners to handle various checks and responses:
    - **AIChatbot**: Processes the message for AI-based responses.
    - **NSFWChecker**: Detects inappropriate or NSFW content and takes action.
    - **FlaggedWordsAlert**: Monitors for flagged keywords or phrases in the message.
    - **RepeatedMessageAlert**: Checks if the message is a repeated message.
    - **ActiveAlertChecker**: Logs the activity of the channel where the message was posted and checks for active alerts.

  Each listener performs its specific task and handles the message accordingly, whether that means sending alerts, muting users, or performing other actions.

#### **2. Reaction Events**

- **Reaction Handling**:
  The `EventHandler` also listens for reaction events, triggered when a user adds a reaction to a message. This is commonly used for alerting or processing actions like approvals or rejections:
    - **NSFWChecker**: Checks if the reaction is related to an NSFW content alert, and handles it accordingly.
    - **FlaggedWordsAlert**: Processes reactions on flagged word alerts, enabling staff to take actions like issuing warnings or muting the user.
    - **RepeatedMessageAlert**: Handles reactions for actions related to repeated message detection, allowing staff to decide on the severity of the action to take.

  These reactions are processed in real-time, allowing staff to take appropriate actions based on the severity of the alert or content.

#### **3. Periodic Tasks**

- **Ticket Channel Activity**:
  The `EventHandler` includes a periodic task that checks ticket channels (channels named `ticket-*`) for recent activity. Every 5 minutes:
  - It checks if there has been activity in any ticket channel. If no messages have been posted within the last 60 minutes, the bot sends a reminder to the user to keep the ticket open.
  - If there is still no activity after 60 minutes, the bot sends commands to close the ticket, send a transcript, and then delete the channel.

This task ensures that the bot maintains an active and well-managed ticket system, closing inactive tickets to keep the server organized.

---

### **How Event Handling Works in ColossusBot**:

1. The `EventHandler` listens for key events across all active guilds, ensuring that the bot responds to interactions promptly.
2. For each event type (e.g., messages or reactions), the event handler delegates processing to the appropriate listener modules:
   - **AIChatbot** for conversational AI responses.
   - **NSFWChecker** for NSFW detection and alerts.
   - **FlaggedWordsAlert** for monitoring flagged keywords.
   - **RepeatedMessageAlert** for detecting and responding to repeated messages.
   - **ActiveAlertChecker** for logging and checking channel activity.
3. The bot performs periodic checks for ticket channels, ensuring they are kept up to date and closed when inactive.
4. The event handler ensures real-time processing of messages and reactions, while managing long-running tasks like ticket monitoring.

This modular, event-driven approach allows ColossusBot to scale efficiently, handling multiple types of events without compromising performance.

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

## **Configuration Options**

ColossusBot is configured using environment variables stored in the `.env` file.

#### **Core Variables**

| Variable         | Description                                    | Default |


|------------------|------------------------------------------------|---------|
| `BOT_TOKEN`      | The token for the Discord bot.                 | None    |
| `BOT_PREFIX`     | The prefix for bot commands.                   | `!`     |
| `DB_ENGINE`      | The type of database to use (`sqlite` or `mysql`). | `sqlite` |
| `DB_NAME`        | The name of the SQLite database file or MySQL database. | `colossusbot.db` |
| `OPENAI_API_KEY` | API key for OpenAI integrations.               | None    |

---

Here’s the updated section for the `listeners/` directory, with **excruciating detail** about each file’s purpose and functionality:

---

## **Cog Reference**

This section provides an overview of the core cogs integrated with ColossusBot. Each cog is responsible for a specific set of functionalities, often leveraging handlers for efficient operation.

### **1. `admin_commands.py`**

**Description**: Provides commands for administrators to manage server operations, such as muting, kicking, banning, and issuing warnings to users.

**Handlers Involved**: `CommandsHandler`, `DatabaseHandler`, `EventHandler`.

---

### **2. `aichatbot.py`**

**Description**: Integrates AI-powered features like natural language processing for chatbot functionalities, including moderation insights, automatic responses, and sentiment analysis.

**Handlers Involved**: `CommandsHandler`, `EventHandler`, `WebHandler`, `DatabaseHandler`.

---

### **3. `channel_access_manager.py`**

**Description**: Manages access control for channels based on roles and permissions, ensuring that only authorized users can interact with sensitive channels.

**Handlers Involved**: `CommandsHandler`, `EventHandler`, `DatabaseHandler`.

---

### **4. `channel_archiver.py`**

**Description**: Handles the archiving and unarchiving of channels, either manually or automatically based on activity. This includes moving inactive channels to an archive category or restoring them when needed.

**Handlers Involved**: `CommandsHandler`, `EventHandler`, `DatabaseHandler`.

---

Got it! Here's the updated README with the inclusion of the various **reaction sets** across the different listeners (excluding `active_alert_checker.py`, which doesn't have reactions). I've also expanded the list of emojis to cover all available reactions mentioned:

---

### **5. `listeners/`**

The `listeners/` directory contains cogs that handle various types of event-driven actions in ColossusBot. These listeners provide core functionality such as monitoring activity, handling flagged content, detecting NSFW material, and tracking repeated messages. Each listener responds to specific events within Discord and takes action based on those events. Here is an overview of the listeners in this directory:

---

#### **1. `active_alert_checker.py`**

**Purpose**: The `active_alert_checker.py` listener is designed to track and log channel activity. It monitors the time difference between the last message sent in a channel and the current message. When a channel becomes active again (after inactivity), it logs the activity in a designated log channel.

- **Key Features**:
  - **Channel Activity Tracking**: This listener keeps track of when a channel becomes active by comparing the time difference between the last message and the current message.
  - **Log Channel**: Once a channel becomes active, it sends an activity log message to a designated log channel.
  - **No Reaction Handling**: Unlike other listeners, the `active_alert_checker.py` does not involve reactions. Instead, it purely logs channel activity.

- **Note**: This listener does **not** use reactions or require staff interaction. It simply logs the channel's activity in a dedicated log channel.

---

#### **2. `flagged_words_alert.py`**

**Purpose**: The `flagged_words_alert.py` listener detects and alerts staff when potentially harmful or inappropriate words are used in messages.

- **Key Features**:
  - **Flagged Words Detection**: Monitors messages for words or phrases from a predefined list of flagged terms.
  - **Real-Time Alerts**: Sends alerts to staff when flagged words are detected in a message.
  - **Reactions Handling**: Staff can use reactions like ✅ (approve action) or ❌ (ignore) to take actions on the flagged content.

- **Take Action**:
  When a flagged word is detected, staff are notified, and they can:
  - **✅**: Approve the alert (issue a penalty).
  - **❌**: Dismiss the alert.

- **Penalty Emojis**:
  - **⚠️**: Issue a warning to the user.
  - **🔇**: Mute the user.
  - **👢**: Kick the user from the server.
  - **🔨**: Ban the user.

---

#### **3. `nsfw_checker.py`**

**Purpose**: The `nsfw_checker.py` listener scans messages for NSFW (Not Safe For Work) content, including explicit images, videos, and text.

- **Key Features**:
  - **NSFW Content Detection**: Uses integrated tools to scan messages for explicit content, both in text and media (e.g., images, videos).
  - **Automatic Actions**: Can automatically take actions such as deleting inappropriate messages or warning the user.
  - **Reactions Handling**: Allows staff to react to alerts to take further action.

- **Take Action**:
  When NSFW content is detected:
  - **✅**: Approve the alert (issue a penalty).
  - **❌**: Dismiss the alert.

- **Penalty Emojis**:
  - **⚠️**: Issue a warning to the user.
  - **🔇**: Mute the user.
  - **👢**: Kick the user from the server.
  - **🔨**: Ban the user.

---

#### **4. `repeated_message_alert.py`**

**Purpose**: The `repeated_message_alert.py` listener detects when the same or similar messages are repeatedly sent across different guilds or channels, helping to flag spammy behavior.

- **Key Features**:
  - **Repeated Message Detection**: Monitors for repeated messages that are identical or nearly identical across different servers or channels.
  - **Cross-Guild Monitoring**: Can detect repeated messages from users in different guilds.
  - **Staff Alerts**: Sends alerts to staff when repeated messages are detected, enabling quick action to be taken.
  - **Reactions Handling**: Staff can react to alerts to approve or dismiss actions on the repeated message.

- **Take Action**:
  When a repeated message is detected, staff can take actions such as:
  - **✅**: Approve the alert (issue a penalty).
  - **❌**: Dismiss the alert.

- **Penalty Emojis**:
  - **⚠️**: Issue a warning to the user.
  - **🔇**: Mute the user.
  - **👢**: Kick the user from the server.
  - **🔨**: Ban the user.

---

#### **How Reactions Work in Listeners**

The following listeners use reactions as a way to quickly take action on alerts:

- **Flagged Words Alert Listener (`flagged_words_alert.py`)**
- **NSFW Checker Listener (`nsfw_checker.py`)**
- **Repeated Message Alert Listener (`repeated_message_alert.py`)**

In these listeners, reactions are used by moderators or staff to confirm, approve, or dismiss alerts generated by the bot. The reactions include:

- **✅**: Confirm the alert (e.g., deleting a message, issuing a penalty).
- **❌**: Dismiss the alert.
- **⚠️**: Issue a warning to the user.
- **🔇**: Mute the user.
- **👢**: Kick the user from the server.
- **🔨**: Ban the user.

Each listener is designed to help staff manage and moderate their servers by making it easier to interact with alerts and take action swiftly.

---

### **In Summary**

The `listeners/` directory contains several event-driven cogs designed to enhance server management in ColossusBot. These listeners monitor different aspects of server activity, such as message content, NSFW material, repeated messages, and overall channel activity. By using reactions, staff can take immediate actions based on the alerts generated by the bot.

The `active_alert_checker.py` listener is unique in that it doesn’t require reactions or direct staff interaction but instead focuses on tracking and logging channel activity to a designated log channel.

## **Command Reference**

This section provides a detailed list of available commands for ColossusBot, including usage examples and descriptions. As commands are polished or newly developed, they will be added here.

---

### **1. `!active`**

**Description**: Displays the current activity status of the bot in the server.

**Usage**:
```plaintext
!active
```

**Example**:
```plaintext
User: !active
Bot: The bot is currently active and processing commands.
```

---

### **2. `!catfish`**

**Description**: Searches for a catfish-related term or phrase and returns a list of relevant search results.

**Usage**:
```plaintext
!catfish [search_term]
```

**Example**:
```plaintext
User: !catfish fishing
Bot: Here are the top search results for "fishing" related to catfish.
```

---

### **3. `!define`**

**Description**: Defines a word or phrase using an online dictionary.

**Usage**:
```plaintext
!define [word]
```

**Example**:
```plaintext
User: !define colloquialism
Bot: "Colloquialism" is defined as a word or phrase used in informal language.
```

---

### **4. `!google`**

**Description**: Performs a Google search and returns the top search results.

**Usage**:
```plaintext
!google [query]
```

**Example**:
```plaintext
User: !google python programming
Bot: Here are the top results for "python programming":
- https://www.python.org/
- https://realpython.com/
```

---

### **5. `!image`**

**Description**: Returns an image based on a search query.

**Usage**:
```plaintext
!image [search_term]
```

**Example**:
```plaintext
User: !image sunset
Bot: [returns image of a sunset]
```

---

### **6. `!keywords`**

**Description**: Detects flagged keywords or phrases within the server chat.

**Usage**:
```plaintext
!keywords
```

**Example**:
```plaintext
User: !keywords
Bot: The following flagged keywords were detected: "example_word_1", "example_word_2".
```

---

### **7. `!purge_user`**

**Description**: Purges a user's messages within the chat for a specified period.

**Usage**:
```plaintext
!purge_user [user_id] [time_frame]
```

**Example**:
```plaintext
User: !purge_user 123456789012345678 24h
Bot: Purged all messages from user 123456789012345678 for the past 24 hours.
```

---

### **8. `!restrict_role`**

**Description**: Restricts a user’s role to prevent them from performing certain actions within the server.

**Usage**:
```plaintext
!restrict_role [user_id] [role]
```

**Example**:
```plaintext
User: !restrict_role 123456789012345678 Moderator
Bot: The user 123456789012345678 is now restricted from performing moderator actions.
```

---

### **9. `!say`**

**Description**: Makes the bot say a specified message.

**Usage**:
```plaintext
!say [message]
```

**Example**:
```plaintext
User: !say Hello, everyone!
Bot: Hello, everyone!
```

---

### **10. `!suggest`**

**Description**: Allows users to make suggestions for improving the server.

**Usage**:
```plaintext
!suggest [suggestion]
```

**Example**:
```plaintext
User: !suggest Add more fun bot games
Bot: Your suggestion "Add more fun bot games" has been noted. Thank you!
```

---

### **11. `!todo`**

**Description**: Adds a task to the bot's to-do list.

**Usage**:
```plaintext
!todo [task]
```

**Example**:
```plaintext
User: !todo Finish the documentation
Bot: Task "Finish the documentation" added to the to-do list.
```

---

### **12. `!vibecheck`**

**Description**: Checks the "vibe" of the chat based on a sentiment analysis.

**Usage**:
```plaintext
!vibecheck
```

**Example**:
```plaintext
User: !vibecheck
Bot: The vibe of the chat is 85% positive!
```

---

### **13. `!vote`**

**Description**: Starts a voting poll in the server.

**Usage**:
```plaintext
!vote [question] [option1] [option2] ...
```

**Example**:
```plaintext
User: !vote Should we add more emotes? Yes No
Bot: Poll started: Should we add more emotes? Yes / No
```

---

### **14. `!wiki`**

**Description**: Fetches a summary of a Wikipedia article.

**Usage**:
```plaintext
!wiki [search_term]
```

**Example**:
```plaintext
User: !wiki Python programming language
Bot: Python is an interpreted, high-level programming language with dynamic semantics...
```

---

## **Command Development**

As ColossusBot is constantly evolving, we also include **command templates** for developers looking to add or modify commands. You can use the following templates:

- **Command Template**: For self-contained, simple commands like `!active` and `!catfish`.
- **Cog Template**: For more complex commands involving databases or event handling.

See the [Command and Cog Templates](#command-and-cog-templates) section for detailed instructions.

---


## **License**

ColossusBot is open-source and released under the MIT License.