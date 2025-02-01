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
- **Fishing Automation**: Enjoy automatic fishing with configurable types.
- **Daily Tasks**: Automatically handle daily activities for extra rewards.

This bot is built to save you time and streamline your gameplay, allowing you to focus on strategy and enjoying the game.

---

## 🌟 Version v1.0.0

### Updates

- **New Feature:** Added dynamic proxy support for each account (**mandatory when using multiple accounts**).
- **New Feature:** Automatically complete quests and daily tasks.
- **New Feature:** Auto upgrade skills to boost your performance.
- **New Feature:** Auto sell all caught fish to keep your inventory clear.
- **New Feature:** Configurable fishing types to suit your gameplay style.

🔹 **Upcoming Update:**  
The next version will focus on optimizing the **fishing system** to improve efficiency and maximize your catch rate. Stay tuned for better performance and more features!

---

## ℹ️ Getting Started with UserInfo Bot

To avoid any confusion when setting up your account data, please use the [UserInfo Bot](https://github.com/nadam/userinfobot). This bot displays your user information when you forward a message to it. **Remember:** the query format should be:

```
id|telegram_username
```

Make sure you obtain your correct information from the UserInfo Bot before proceeding with the setup.

---

## 📥 **How to Register**

Start using Fishing Frenzy by registering through the following link:

<div align="center">
  <a href="https://t.me/fishingfrenzy_bot/fishingfrenzyapp?startapp=HE8W8F" target="_blank">
    <img src="https://img.shields.io/static/v1?message=Fishinhg Frenzy&logo=telegram&label=&color=2CA5E0&logoColor=white&labelColor=&style=for-the-badge" height="25" alt="telegram logo" />
  </a>
</div>

---
## ⚙️ Configuration (`config.json`)

Below is the configuration table for the Fishing Frenzy Bot. Adjust these settings in your `config.json` file as needed:

| **Setting**            | **Description**                                                              | **Default Value** |
| ---------------------- | ---------------------------------------------------------------------------- | ----------------- |
| `proxy`                | **Mandatory** for multi-account setups. Enable proxy usage for each account. | `true`            |
| `quest`                | Automatically complete quests                                                | `true`            |
| `upgrade_skill`        | Automatically upgrade your skills                                            | `true`            |
| `sell_all_fish`        | Automatically sell all caught fish                                           | `true`            |
| `fishing`              | Enable automatic fishing                                                     | `true`            |
| `fishing_type`         | Set the fishing type (1 for short, 2 for mid, and 3 for long)                | `1`               |
| `daily`                | Automatically complete daily tasks                                           | `true`            |
| `delay_loop`           | Delay (in seconds) before the next loop                                      | `3000`            |
| `delay_account_switch` | Delay (in seconds) between switching accounts                                | `10`              |

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
   Create a file named `query.txt` and paste your query data in the format obtained from the UserInfo Bot:

   ```
   id|telegram_username
   ```

5. **Set Up Proxies (Mandatory for Multi-Account Usage)**  
   If you are running the bot with multiple accounts, you **must** use proxies. Create a file named `proxy.txt` and add your proxies in the following format:

   ```
   http://username:password@ip:port
   ```

   _Note: Only HTTP and HTTPS proxies are supported._

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
