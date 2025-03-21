---

<h1 align="center">Fishing Frenzy Bot</h1>

<p align="center">Automate tasks in Fishing Frenzy to enhance your fishing skills, upgrade your abilities, and maximize your daily rewards!</p>

---

## 🚀 About the Bot

Fishing Frenzy Bot is designed to automate various tasks in **Fishing Frenzy**, including:

- **Proxy Support**: Use dynamic proxies for each account (**mandatory for multi-account setups**).
- **Quest Automation**: Complete quests and events automatically.
- **Upgrade Skill**: Automatically upgrade your character's skills.
- **Sell All Fish**: Sell all your fish without manual intervention.
- **Fishing Automation**: Enjoy automatic fishing with configurable types and the latest API adjustments for Fishing Frenzy Session 2.
- **Daily Tasks**: Automatically handle daily activities for extra rewards.
- **Event System**: Automatically switch to the event area (without purchasing event items).
- **Web Login Support**: Log in via web by searching for the login API.
- **Bait Usage**: The bot now automatically uses all available bait variations from your inventory.
- **Thread System**: Run tasks concurrently with the new threading system for improved performance.

This bot is built to save you time and streamline your gameplay, allowing you to focus on strategy and enjoying the game.

---

## 🌟 Version Updates

**Current Version: v1.0.4**

### Version v1.0.4 Updates:

- **API Adjustments for Fishing Frenzy Session 2:**  
  Enhanced support for the updated fishing session API.
- **Proxy System:**  
  Dynamic proxy support is now integrated for each account.
- **Thread System:**  
  New threading support to run tasks concurrently.
- **Login System:**
  - **Web Login (Guest Only):** The bot currently supports guest login only.
  - **Upcoming:** Additional login methods via email and wallet are planned.
- **Bait Usage:**  
  The bot now uses all available bait items across every variation from your inventory.

> **Upcoming Updates:**
>
> - Feature optimization across the board.
> - Additional features in line with Fishing Frenzy Session 2 updates (e.g., cooking).

---

## ⚙️ Configuration (`config.json`)

The configuration file now follows this structure:

```json
{
  "quest": true,
  "upgrade_skill": true,
  "event": false,
  "fishing": true,
  "fishing_type": 1,
  "daily": true,
  "sell_all_fish": false,
  "proxy": true,
  "thread": 1,
  "delay_loop": 3000,
  "delay_account_switch": 10
}
```

> **Note:** If you are using more than one account, you **must** use proxies.

| **Setting**            | **Description**                                                | **Default Value** |
| ---------------------- | -------------------------------------------------------------- | ----------------- |
| `quest`                | Automatically complete quests.                                 | `true`            |
| `upgrade_skill`        | Automatically upgrade your skills.                             | `true`            |
| `event`                | Automatically switch to the event area.                        | `false`           |
| `fishing`              | Enable automatic fishing.                                      | `true`            |
| `fishing_type`         | Set the fishing type (1 for short, 2 for mid, and 3 for long). | `1`               |
| `daily`                | Automatically complete daily tasks.                            | `true`            |
| `sell_all_fish`        | Automatically sell all caught fish.                            | `false`           |
| `proxy`                | Enable proxy usage for multi-account setups.                   | `true`            |
| `thread`               | Number of threads to run concurrently.                         | `1`               |
| `delay_loop`           | Delay (in milliseconds) before the next loop.                  | `3000`            |
| `delay_account_switch` | Delay (in seconds) between switching accounts.                 | `10`              |

---

## 📥 Installation Steps

1. **Clone the Repository**  
   Clone the project to your local machine using:

   ```bash
   git clone https://github.com/livexords-nw/fishingfrenzy-bot.git
   ```

2. **Navigate to the Project Folder**  
   Move into the project directory:

   ```bash
   cd fishingfrenzy-bot
   ```

3. **Install Dependencies**  
   Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Your Query**  
   Create a file named `query.txt` and paste your query data in the following format:

   1. **Inspect Fishing Frenzy Web:**  
      Open your browser, navigate to the Fishing Frenzy login page, and inspect the web page.
   2. **Locate the Device ID:**  
      Look in the **Application** tab or check the API calls for your device ID.
   3. **Guest Login Support:**  
      The bot currently supports guest login only.
   4. **Format Your Query:**  
      Copy your device ID and format it as follows:

      ```text
      deviceid|guest
      ```

5. **Set Up Proxies (Mandatory for Multi-Account Usage)**  
   If you are running the bot with multiple accounts, you **must** use proxies. Create a file named `proxy.txt` and add your proxies in the following format:

   ```text
   http://username:password@ip:port
   ```

   > **Note:** Only `HTTP` and `HTTPS` proxies are supported.

6. **Run the Bot**  
   Start the bot by running:

   ```bash
   python main.py
   ```

---

### 🔹 Need Free Proxies?

You can obtain free proxies from [Webshare.io](https://www.webshare.io/).

---

## 🛠️ Contributing

This project is developed by **Livexords**. If you have any suggestions, questions, or would like to contribute, please feel free to reach out:

<div align="center">
  <a href="https://t.me/livexordsscript" target="_blank">
    <img src="https://img.shields.io/static/v1?message=Livexords&logo=telegram&label=&color=2CA5E0&logoColor=white&labelColor=&style=for-the-badge" height="25" alt="telegram logo" />
  </a>
</div>

---
