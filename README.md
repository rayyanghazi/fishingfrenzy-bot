
---

<h1 align="center">Fishing Frenzy Bot</h1>

<p align="center">
<strong>Boost your productivity with Fishing Frenzy Bot – your friendly automation tool that handles key tasks with ease!</strong>
</p>

<p align="center">
<a href="https://github.com/livexords-nw/fishingfrenzy-bot/actions">
<img src="https://img.shields.io/github/actions/workflow/status/livexords-nw/fishingfrenzy-bot/ci.yml?branch=main" alt="Build Status" />
</a>
<a href="https://github.com/livexords-nw/fishingfrenzy-bot/releases">
<img src="https://img.shields.io/github/v/release/livexords-nw/fishingfrenzy-bot" alt="Latest Release" />
</a>
<a href="https://github.com/livexords-nw/fishingfrenzy-bot/blob/main/LICENSE">
<img src="https://img.shields.io/github/license/livexords-nw/fishingfrenzy-bot" alt="License" />
</a>
<a href="https://t.me/livexordsscript">
<img src="https://img.shields.io/badge/Telegram-Join%20Group-2CA5E0?logo=telegram&style=flat" alt="Telegram Group" />
</a>
</p>

---

## 🚀 About the Bot

Fishing Frenzy Bot is your automation buddy designed to simplify daily operations. This bot takes over repetitive tasks so you can focus on what really matters. With Fishing Frenzy Bot, you get:

- **Auto Buy Sushi 🍣**  
  Automatically purchase sushi when needed to maintain performance and boost gameplay.
- **Quest Automation 🏟️**  
  Automatically complete quests and in-game events without manual input.
- **Skill Upgrade 💪**  
  Automatically upgrade your character’s skills for better performance.
- **Auto Sell Fish 💰**  
  Instantly sell all caught fish without any manual effort.
- **Auto Fishing 🎣**  
  Fully automate fishing with configurable types and updated API support for Fishing Frenzy Season 2.
- **Daily Tasks 📅**  
  Automatically handle daily missions to secure extra rewards.
- **Event System 🎉**  
  Seamlessly switch to the event area without needing to buy event items.
- **Auto Bait Usage 📦**  
  Automatically use all available bait items from your inventory.
- **Auto Cooking 🍳**  
  Cook recipes automatically when ingredients are available.
- **Auto Referral 🔖**  
  Generate new accounts using referral codes automatically.
- **Auto Claim Referral 🧵**  
  Automatically claim rewards from used referral codes.
- **Auto Chest Opening 📦**  
  Open all available chests in your backpack automatically (in-game only).
- **Auto Equip Rod 🔱**  
  Automatically equip the best available fishing rod from your inventory (in-game only). Compares current rod with available ones and equips a better option if found.
- **Multi Account Support 👥:**  
  Manage multiple accounts effortlessly with built-in multi account support.
- **Thread System 🧵:**  
  Run tasks concurrently with configurable threading options to improve overall performance and speed.
- **Configurable Delays ⏱️:**  
  Fine-tune delays between account switches and loop iterations to match your specific workflow needs.
- **Support Proxy 🔌:**  
  Use HTTP/HTTPS proxies to enhance your multi-account setups.

Fishing Frenzy Bot is built with flexibility and efficiency in mind – it's here to help you automate your operations and boost your productivity!

---

## 🌟 Version Updates

**Current Version: v1.0.8**

### v1.0.8 - Latest Update

- Optimization across all features
- Improvements to the latest features: auto open chest and auto rod. Currently, auto rod can only equip the best rod. Auto repair functionality will be added in the next update.
- Added new setting `buy_sushi` in `config.json` to enable or disable the auto-buy sushi feature (default: `false`)

---

## 📝 Register

Before you start using Fishing Frenzy Bot, make sure to register your account.  
Click the link below to get started:

[🔗 Register for Fishing Frenzy Bot](https://fishingfrenzy.co?code=EU6HOU)

---

## ⚙️ Configuration

### Main Bot Configuration (`config.json`)

```json
{
  "buy_sushi": false,
  "chest": true,
  "rod": true,
  "reff": true,
  "cooking": true,
  "battle_pass": true,
  "quest": true,
  "upgrade_skill": true,
  "event": true,
  "fishing": true,
  "daily": true,
  "sell_all_fish": false,
  "proxy": false,
  "run_with_reff": false,
  "thread": 1,
  "delay_loop": 3000,
  "delay_account_switch": 10
}
```

| **Setting**            | **Description**                                  | **Default Value** |
| ---------------------- | ------------------------------------------------ | ----------------- |
| `buy_sushi`            | Enable or disable the auto-buy sushi feature.    | `false`           |
| `chest`                | Enable auto open chest (in-game).                | `true`            |
| `rod`                  | Enable auto equip rod (in-game).                 | `true`            |
| `cooking`              | Enable the auto cooking feature.                 | `true`            |
| `battle_pass`          | Automatically claim battle pass rewards.         | `true`            |
| `quest`                | Automatically complete quests.                   | `true`            |
| `upgrade_skill`        | Automatically upgrade your skills.               | `true`            |
| `event`                | Automatically switch to the event area.          | `true`            |
| `fishing`              | Enable automatic fishing.                        | `true`            |
| `daily`                | Automatically complete daily tasks.              | `true`            |
| `sell_all_fish`        | Automatically sell all caught fish.              | `false`           |
| `proxy`                | Enable proxy usage for multi-account setups.     | `false`           |
| `run_with_reff`        | Enable running accounts generated via auto reff. | `false`           |
| `thread`               | Number of threads to run concurrently.           | `1`               |
| `delay_loop`           | Delay (in seconds) before the next loop.         | `3000`            |
| `delay_account_switch` | Delay (in seconds) between switching accounts.   | `10`              |

##

### Reff Bot Configuration (`config_reff.json`)

```json
{
  "proxy": true,
  "thread": 1,
  "delay_loop": 3000,
  "delay_account_switch": 10
}
```

| **Setting**            | **Description**                                | **Default Value** |
| ---------------------- | ---------------------------------------------- | ----------------- |
| `proxy`                | Enable proxy usage for the auto reff system.   | `true`            |
| `thread`               | Number of threads to run concurrently.         | `1`               |
| `delay_loop`           | Delay (in seconds) before the next loop.       | `3000`            |
| `delay_account_switch` | Delay (in seconds) between switching accounts. | `10`              |

---

## 📅 Requirements

- **Minimum Python Version:** `Python 3.9+`
- **Required Libraries:**
  - colorama
  - requests
  - websocket-client
  - fake-useragent
  - brotli
  - chardet
  - urllib3

These are installed automatically when running:

```bash
pip install -r requirements.txt
```

---

## 📅 Installation Steps

### Main Bot Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/livexords-nw/fishingfrenzy-bot.git
   ```

2. **Navigate to the Project Folder**

   ```bash
   cd fishingfrenzy-bot
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Your Query**

   Create a file named `query.txt` and add your query data.

5. **Set Up Proxy (Optional)**  
   To use a proxy, create a `proxy.txt` file and add proxies in the format:

   ```
   http://username:password@ip:port
   ```

   _Only HTTP and HTTPS proxies are supported._

6. **Run Bot**

   ```bash
   python main.py
   ```

---

## 📅 Auto Reff Installation

1. **Prepare Auto Reff Files**  
   Create a file named `query_reff.txt` with the following content:

   ```text
   EU6HOU|20
   ```

   Here, `EU6HOU` is your referral code and `20` is the number of accounts you want to generate.

2. **Run the Auto Reff Module**

   ```bash
   python reff.py
   ```

3. **Integrate Reff Accounts**  
   To run the generated reff accounts in the main bot, enable `"run_with_reff": true` in your `config.json`.

---

## 💻 **Tutorial: Install the Extension**

1. **Download the Extension:**  
   Download the zip file `fishing_frenzy_query.zip` from this repository.  
   ![Download Image](download_extension.png)

2. **Install Violent Monkey Extension:**  
   Install the Violent Monkey extension in your browser using [this link](https://chromewebstore.google.com/detail/jinjaccalgkegednnccohejagnlnfdag?utm_source=item-share-cb).

3. **Import the Zip File:**  
   Open Violent Monkey, go to **Settings** → **Import from Zip**, and select the downloaded zip file.  
   ![Import Zip Image](import_placeholder.png)

4. **Activate the Extension on Fishing Frenzy Website:**  
   Open the Fishing Frenzy website. If you are still logged in, please log out and log in again to ensure the extension is active.  
   Make sure the extension is working correctly as shown below:  
   ![Extension Active Image](extension_active_placeholder.jpg)

5. **Capture and Copy the Query:**  
   Once logged in, click **Format & Format Token** or **Format & Format Divace ID** on the extension.  
   Then, paste the copied result into your `query.txt` file.

---

### 🔹 Want Free Proxies?

You can obtain free proxies from [Webshare.io](https://www.webshare.io/).

---

## 📂 Project Structure

```
FishingFrenzy-bot/
├── .github/
│   └── workflows/
│       └── ci.yml                        # GitHub Actions CI workflow
├── config_reff.json                      # Configuration for referral settings
├── config.json                           # Main configuration file
├── download_extension.png                # Image asset for extension
├── extension_active_placeholder.jpg      # Placeholder image for extension state
├── fishing_frenzy_query.zip              # ⚙️ Violentmonkey extension to auto-extract query data
├── import_placeholder.png                # Placeholder image for import section
├── LICENSE                               # Project license file
├── main.py                               # Main Python entry point
├── README.md                             # Project description and usage
├── reff.py                               # Script handling referral system
├── requirements.txt                      # Python dependencies
├── tutorial.png                          # Tutorial image for guidance
```

---

## 🛠️ Contributing

This project is developed by **Livexords**.  
If you have ideas, questions, or want to contribute, please join our Telegram group for discussions and updates.  
For contribution guidelines, please consider:

- **Code Style:** Follow standard Python coding conventions.
- **Pull Requests:** Test your changes before submitting a PR.
- **Feature Requests & Bugs:** Report and discuss via our Telegram group.

<div align="center">
  <a href="https://t.me/livexordsscript" target="_blank">
    <img src="https://img.shields.io/badge/Join-Telegram%20Group-2CA5E0?logo=telegram&style=for-the-badge" height="25" alt="Telegram Group" />
  </a>
</div>

---

## 📖 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for more details.

---

## 🔍 Usage Example

After installation and configuration, simply run:

```bash
python main.py
```

You should see output indicating the bot has started its operations. For further instructions or troubleshooting, please check our Telegram group or open an issue in the repository.

---

## 📣 Community & Support

For support, updates, and feature requests, join our Telegram group.  
This is the central hub for all discussions related to Fishing Frenzy Bot, including roadmap ideas and bug fixes.

---
