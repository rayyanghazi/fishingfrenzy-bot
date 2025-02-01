from datetime import datetime
import json
import time
from colorama import Fore
import requests
import uuid
import random
import websocket
import asyncio
from urllib.parse import urlparse

class fishingfrenzy:
    BASE_URL = "https://fishing-frenzy-api-0c12a800fbfe.herokuapp.com/v1/"
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "fishing-frenzy-api-0c12a800fbfe.herokuapp.com",
        "Origin": "https://fishingfrenzy.co",
        "Referer": "https://fishingfrenzy.co/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "sec-ch-ua": '"Chromium";v="132", "Microsoft Edge";v="132", "Not A(Brand";v="8", "Microsoft Edge WebView2";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"' 
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.access_token = None
        self.refresh_token = None
        self.energy = 0
        self.config = self.load_config()
        self.reconnect_attempts = 3
        self.reconnect_delay = 5

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Fishing Frenzy Free Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
            print(Fore.LIGHTBLACK_EX + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |") + " " + color + message + Fore.RESET)

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log("❌ Failed to parse config.json. Please check the file format.", Fore.RED)
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file, expecting each line to contain
        'telegram_id|username_telegram' format.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of tuples (telegram_id, username_telegram, device_id) or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = []
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split("|")
                        if len(parts) == 2:
                            device_id = str(uuid.uuid4())  # Generate a unique device ID
                            queries.append((parts[0].strip(), parts[1].strip(), device_id))
                        else:
                            self.log(f"⚠️ Invalid format in line: {line}", Fore.YELLOW)
            
            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty or has invalid entries.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} valid queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        self.log("🔒 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        teleUserId, teleName, deviceId = self.query_list[index]
        req_url = f"{self.BASE_URL}auth/guest-login"
        
        payload = {
            "deviceId": str(uuid.uuid4()),  # Generate new device ID for each login
            "teleUserId": int(teleUserId),
            "teleName": teleName
        }
        
        self.log(f"📋 Logging in as {teleName} (ID: {teleUserId})", Fore.CYAN)

        headers = {**self.HEADERS}
        
        try:
            self.log("📡 Sending request to fetch user information...", Fore.CYAN)
            response = requests.post(req_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            access_token = data["tokens"].get("access", {}).get("token")
            refresh_token = data["tokens"].get("refresh", {}).get("token")
            if access_token and refresh_token:
                self.access_token = access_token
                self.refresh_token = refresh_token
                self.log("🔑 Access token and refresh token successfully retrieved.", Fore.GREEN)
            else:
                self.log("⚠️ Access token and refresh token not found in response.", Fore.YELLOW)
                return

            # Verify token request
            verify_url = f"{self.BASE_URL}auth/verify-tokens"
            verify_payload = {"accessToken": self.access_token}
            verify_headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

            self.log("🔍 Verifying access token...", Fore.CYAN)
            verify_response = requests.post(verify_url, headers=verify_headers, json=verify_payload)

            if verify_response.status_code == 200:
                self.log("✅ Access token successfully verified.", Fore.GREEN)
                self.access_token = verify_response.json()['access'].get('token', None)
            else:
                self.log(f"❌ Token verification failed. Status: {verify_response.status_code}", Fore.RED)
                self.log(f"📄 Response: {verify_response.text}", Fore.RED)

            user_info = data.get("user", {})
            self.energy = user_info.get('energy')
            if user_info:
                self.log("✅ Login successful!", Fore.GREEN)
                self.log(f"🆔 User ID: {user_info.get('userPrivyId')}", Fore.LIGHTCYAN_EX)
                self.log(f"👤 Role: {user_info.get('role')}", Fore.LIGHTCYAN_EX)
                self.log(f"💰 Gold: {user_info.get('gold')}", Fore.YELLOW)
                self.log(f"⚡ Energy: {user_info.get('energy')}", Fore.YELLOW)
                self.log(f"🐟 Fish Points: {user_info.get('fishPoint')}", Fore.YELLOW)
                self.log(f"⭐ EXP: {user_info.get('exp')}", Fore.YELLOW)
                self.log(f"🎁 Today's Reward: {user_info.get('todayReward')}", Fore.YELLOW)
                self.log(f"📅 Last Login: {user_info.get('lastLoginTime')}", Fore.LIGHTCYAN_EX)
            else:
                self.log("⚠️ Unexpected response structure.", Fore.YELLOW)
        
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to send login request: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)

    def daily(self) -> int:
        """Claims the daily rewards from the server."""
        req_url_daily = f"{self.BASE_URL}daily-rewards/claim"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        try:
            self.log("📡 Claiming daily rewards...", Fore.CYAN)
            response = requests.get(req_url_daily, headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                self.log("✅ Daily reward successfully claimed.", Fore.GREEN)
            else:
                self.log(f"❌ Failed to claim daily reward. Status: {response.status_code}", Fore.RED)
                self.log(f"📄 Response: {response.text}", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to claim daily rewards: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0  # Return 0 if claiming the reward fails
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0 
    
    def fishing(self) -> int:
        """
        Connects to the fishing server via WebSocket and runs fishing sessions in a loop.
        Each session costs energy based on the fishing type:
        - short_range (fishing_type == 1): costs 1 energy
        - mid_range (fishing_type == 2): costs 2 energy
        - long_range (any other fishing_type): costs 3 energy

        If there is not enough energy for a session, this method will call self.buy_and_use_sushi()
        repeatedly until enough energy is restored. If sushi cannot be bought due to lack of gold,
        the fishing loop stops.

        Returns:
            1 if the fishing sessions complete successfully, or 0 on failure.
        """

        # Determine fishing type and corresponding energy cost.
        fishing_type = self.config.get("fishing_type")
        if fishing_type == 1:
            range_type = "short_range"
            energy_cost = 1
        elif fishing_type == 2:
            range_type = "mid_range"
            energy_cost = 2
        else:
            range_type = "long_range"
            energy_cost = 3

        self.log(f"🎣 Starting fishing sessions with type: {range_type} (energy cost: {energy_cost})", Fore.CYAN)

        # Main loop: continue fishing until an unrecoverable error occurs (e.g., out of gold).
        while True:
            # Check if current energy is enough for a session.
            if self.energy < energy_cost:
                self.log("⚠️ Not enough energy for fishing. Attempting to buy and use sushi...", Fore.YELLOW)
                # Attempt to replenish energy.
                result = self.buy_and_use_sushi()
                if result == 0:
                    self.log("❌ Not enough gold to buy sushi. Stopping fishing sessions.", Fore.RED)
                    break
                # After replenishing, wait a moment and re-check energy.
                time.sleep(1)
                continue

            ws_url = f"wss://fishing-frenzy-api-0c12a800fbfe.herokuapp.com/?token={self.access_token}"
            try:
                self.log("📡 Connecting to WebSocket server...", Fore.CYAN)
                ws = websocket.create_connection(ws_url)
                self.log("✅ Connected to WebSocket server.", Fore.GREEN)

                # Initialize game state variables for the session.
                is_game_initialized = False
                frames = []
                frame_count = 0
                session_start_time = time.time()
                max_frames = 15
                fps_default = 20
                fish = None

                # Helper function to start a new game.
                def start_new_game():
                    nonlocal is_game_initialized
                    if not is_game_initialized:
                        prepare_msg = json.dumps({"cmd": "prepare", "range": range_type})
                        ws.send(prepare_msg)
                        self.log("📡 Sent 'prepare' command. Getting ready for fishing...", Fore.CYAN)
                    else:
                        time.sleep(1)
                        start_msg = json.dumps({"cmd": "start"})
                        ws.send(start_msg)
                        self.log("📡 Sent 'start' command. Fishing started...", Fore.CYAN)

                # Helper function to end the game.
                def end_game():
                    nonlocal frame_count, frames
                    end_time = time.time()
                    duration = end_time - session_start_time
                    fps_calculated = frame_count / duration if duration > 0 else fps_default
                    end_payload = {
                        "cmd": "end",
                        "rep": {
                            "fs": frame_count,
                            "ns": len(frames),
                            "fps": fps_calculated,
                            "frs": frames
                        },
                        "en": 1
                    }
                    ws.send(json.dumps(end_payload))
                    self.log("📡 Sent 'end' command.", Fore.CYAN)

                def calculate_position_x(frame: int, direction: int) -> int:
                    return 450 + frame * 2 + direction * 5

                def calculate_position_y(frame: int, direction: int) -> int:
                    return 426 + frame * 2 - direction * 3

                # Begin the session by sending the initial command.
                start_new_game()

                # Process incoming messages from the WebSocket.
                while True:
                    try:
                        message = ws.recv()
                    except websocket.WebSocketTimeoutException:
                        continue  # If no message is received, continue waiting.
                    if not message:
                        continue

                    try:
                        parsed = json.loads(message)
                    except json.JSONDecodeError:
                        self.log("❌ Failed to parse message from server.", Fore.RED)
                        continue

                    msg_type = parsed.get("type")
                    if msg_type == "initGame":
                        # Game initialization response received.
                        fish = parsed.get("data", {}).get("randomFish", {}).get("fishName")
                        self.log(f"🎣 Targeting fish: {fish}", Fore.CYAN)
                        is_game_initialized = True
                        start_new_game()  # Start fishing after initialization.

                    elif msg_type == "gameState":
                        # Process game state messages to record frames.
                        frame = parsed.get("frame", 0)
                        direction = parsed.get("dir", 0)
                        frame_count += 1
                        x = calculate_position_x(frame, direction)
                        y = calculate_position_y(frame, direction)
                        frames.append([x, y])
                        self.log(f"🎯 Frame {frame_count}: x={x}, y={y}", Fore.MAGENTA)
                        if frame_count >= max_frames:
                            end_game()

                    elif msg_type == "gameOver":
                        # Final game result message.
                        energy = parsed.get("catchedFish", {}).get("energy")
                        if parsed.get("success"):
                            self.log(f"✅ Session succeeded! Caught fish: {fish} | Energy Left: {energy}", Fore.GREEN)
                        else:
                            self.log("❌ Session failed.", Fore.RED)
                        break

                ws.close()

                # After the session completes, subtract the energy cost.
                self.energy -= energy_cost
                self.log(f"⏱️ Session finished. Remaining energy: {self.energy}", Fore.YELLOW)
                time.sleep(1)  # Optional delay between sessions

            except Exception as e:
                self.log(f"❌ Error during fishing session: {e}", Fore.RED)
                return 0

        # End of fishing sessions.
        return 1

    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.
        
        Args:
            filename (str): The path to the proxy file.
        
        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.
        
        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").
        
        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN)
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)
        
        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session
    
    def override_requests(self):
        """Override requests and WebSocket functions globally when proxy is enabled."""

        if self.config.get("proxy", False):
            self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
            proxies = self.load_proxies()
            self.set_proxy_session(proxies)

            # Override HTTP request methods
            requests.get = self.proxy_session.get
            requests.post = self.proxy_session.post
            requests.put = self.proxy_session.put
            requests.delete = self.proxy_session.delete

            # Save the original WebSocket create_connection if not already saved
            if not hasattr(self, "_original_websocket_create_connection"):
                self._original_websocket_create_connection = websocket.create_connection

            # Define a proxy-enabled create_connection wrapper
            def proxy_create_connection(*args, **kwargs):
                proxy_url = self.config.get("proxy_url")
                if proxy_url:
                    parsed = urlparse(proxy_url)
                    kwargs["http_proxy_host"] = parsed.hostname
                    kwargs["http_proxy_port"] = parsed.port
                    # Optionally support proxy authentication if provided in the proxy URL
                    if parsed.username and parsed.password:
                        kwargs["http_proxy_auth"] = f"{parsed.username}:{parsed.password}"
                return self._original_websocket_create_connection(*args, **kwargs)

            websocket.create_connection = proxy_create_connection

        else:
            self.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)
            # Restore original HTTP request methods if proxy is disabled
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]

            # Restore the original WebSocket create_connection if it was overridden
            if hasattr(self, "_original_websocket_create_connection"):
                websocket.create_connection = self._original_websocket_create_connection
        
    def sell_all_fish(self) -> int:
        """Sells all fish in the inventory."""
        req_url_sell = f"{self.BASE_URL}fish/sellAll"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        try:
            self.log("🟡 Selling all fish...", Fore.CYAN)
            response = requests.get(req_url_sell, headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                if not data.get("list_fish_info", {}).get("inGame", []):
                    self.log("✅ All fish successfully sold.", Fore.GREEN)
                    return 1
                else:
                    self.log("❌ Some fish were not sold.", Fore.RED)
                    return 0
            else:
                self.log(f"❌ Failed to sell fish. Status: {response.status_code}", Fore.RED)
                self.log(f"📄 Response: {response.text}", Fore.RED)
                return 0

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to sell fish: {e}", Fore.RED)
            return 0
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return 0

    def buy_and_use_sushi(self) -> int:
        """
        Buys and uses sushi to replenish energy.
        
        Steps:
        1. Checks the user's inventory.
        2. Uses available Sushi to restore energy (each Sushi restores a certain amount).
        3. If the Sushi count is low (less than 5), attempts to purchase more,
            provided the user has enough gold.
            
        Note:
        - The Sushi item is identified by the fixed ID "668d070357fb368ad9e91c8a".
        - Assumes a maximum energy of 30.
        """
        req_url_inventory = f"{self.BASE_URL}inventory"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        try:
            self.log("📡 Checking your inventory...", Fore.CYAN)
            response = requests.get(req_url_inventory, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Retrieve basic user info from inventory data
            user_id = data.get("userId")
            gold = data.get("gold", 0)
            energy = data.get("energy", 0)
            self.energy = energy
            max_energy = 30  # assumed maximum energy

            # Locate the Sushi item by its fixed ID
            sushi_id = "668d070357fb368ad9e91c8a"
            sushi_item = next(
                (item for item in data.get("list_item_info", []) if item.get("id") == sushi_id),
                None
            )

            if sushi_item:
                sushi_quantity = sushi_item.get("quantity", 0)
                sushi_effect = sushi_item.get("effect", 0)  # energy restored per sushi
                # Extract the price; assume it's stored as a list of price dictionaries
                sushi_price = sushi_item.get("price", [{}])[0].get("amount", 0)
            else:
                self.log("ℹ️ Sushi item not found in your inventory. Assuming 0 available.", Fore.YELLOW)
                sushi_quantity = 0
                # Set default values if Sushi is not found (you can adjust these as needed)
                sushi_effect = 5     # Default energy restored per sushi
                sushi_price = 500    # Default price in gold

            # Calculate how much energy is needed
            energy_needed = max_energy - energy
            if energy_needed > 0:
                # Determine the number of Sushi needed based on its effect
                needed_sushi = energy_needed // sushi_effect
                # Use only as many as available in the inventory
                used_sushi = min(sushi_quantity, needed_sushi)
                if used_sushi > 0:
                    for _ in range(used_sushi):
                        req_url_use_sushi = f"{self.BASE_URL}items/{sushi_id}/use?userId={user_id}&quantity=1"
                        use_response = requests.get(req_url_use_sushi, headers=headers)
                        use_response.raise_for_status()
                    self.log(f"✅ Used {used_sushi} Sushi to restore energy.", Fore.GREEN)
                else:
                    self.log("ℹ️ Not enough Sushi in inventory to restore energy.", Fore.YELLOW)
            else:
                self.log("ℹ️ Your energy is already full.", Fore.YELLOW)

            # If there is no Sushi or the quantity is low, attempt to buy more (up to 5)
            if sushi_quantity < 5:
                # Calculate how many Sushi the user can buy with their available gold
                max_buyable = gold // sushi_price if sushi_price > 0 else 0
                if max_buyable > 0:
                    buy_quantity = min(max_buyable, 5)
                    req_url_buy_sushi = f"{self.BASE_URL}items/{sushi_id}/buy?userId={user_id}&quantity={buy_quantity}"
                    buy_response = requests.get(req_url_buy_sushi, headers=headers)
                    buy_response.raise_for_status()
                    self.log(f"✅ Purchased {buy_quantity} Sushi.", Fore.GREEN)
                else:
                    self.log("❌ Not enough gold to buy Sushi.", Fore.RED)

            return 1

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to process sushi transactions: {e}", Fore.RED)
            return 0
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return 0
    
    def upgrade_skill(self) -> int:
        """
        Retrieves the accessories data from the server, displays each skill's name,
        current level, and effect. Then, it searches for the "Lucky Charm" accessory and
        attempts to upgrade it if the user has enough upgrade points.
        """
        req_url_accessories = f"{self.BASE_URL}accessories"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        try:
            self.log("📡 Retrieving accessories data...", Fore.CYAN)
            response = requests.get(req_url_accessories, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Get available upgrade points and accessories list
            available_upgrade_points = data.get("availableUpgradePoint", 0)
            accessories = data.get("accessories", [])

            # Display the list of skills with their current level and effect
            self.log("📄 Available Skills:", Fore.YELLOW)
            for accessory in accessories:
                name = accessory.get("name", "Unknown")
                current_level = accessory.get("currentLevel", 0)
                effect = next(
                    (item.get("effect") for item in accessory.get("effects", [])
                    if item.get("level") == current_level),
                    None
                )
                self.log(f"   - {name}: Level {current_level} with Effect {effect}", Fore.YELLOW)

            # Find the accessory with ID "6766e9052546c7705aaf55da" (Lucky Charm)
            lucky_charm = next(
                (acc for acc in accessories if acc.get("accessoryId") == "6766e9052546c7705aaf55da"),
                None
            )
            if not lucky_charm:
                self.log("❌ 'Lucky Charm' accessory not found.", Fore.RED)
                return 0

            # Check if the user has enough upgrade points
            if available_upgrade_points <= 0:
                self.log("❌ You don't have enough upgrade points to upgrade 'Lucky Charm'.", Fore.RED)
                return 0

            # Attempt to upgrade Lucky Charm
            req_url_upgrade = f"{self.BASE_URL}accessories/6766e9052546c7705aaf55da/upgrade"
            self.log("📡 Upgrading 'Lucky Charm'...", Fore.CYAN)
            upgrade_response = requests.post(req_url_upgrade, headers=headers)
            upgrade_response.raise_for_status()

            if upgrade_response.status_code == 200:
                self.log("✅ 'Lucky Charm' has been successfully upgraded.", Fore.GREEN)
            else:
                self.log(f"❌ Failed to upgrade 'Lucky Charm'. Status Code: {upgrade_response.status_code}", Fore.RED)
                self.log(f"📄 Response: {upgrade_response.text}", Fore.RED)
                return 0

            return 1

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request error: {e}", Fore.RED)
            if 'response' in locals():
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0
        except ValueError as e:
            self.log(f"❌ Data processing error: {e}", Fore.RED)
            if 'response' in locals():
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            if 'response' in locals():
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0

    def quest(self) -> dict:
        """
        Fetches the list of social quests from the server and then attempts to verify each quest.
        
        The function uses self.HEADERS and self.access_token for authentication. It first sends a GET
        request to retrieve the quests, then iterates over the returned quests and performs a POST request 
        to verify each quest using additional headers (including an "origin" header).

        Returns:
        A dictionary with two keys:
            - "quests": the list of social quests fetched from the server.
            - "verification_results": a list of results from verifying each quest.
        """
        import requests
        import json

        base_url = "https://fishing-frenzy-api-0c12a800fbfe.herokuapp.com/v1/social-quests/"
        # Use self.HEADERS with the access token for GET requests
        get_headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}
        verification_results = []

        try:
            self.log("📡 Fetching social quests...", Fore.CYAN)
            response = requests.get(base_url, headers=get_headers)
            response.raise_for_status()
            quests = response.json()
            self.log("✅ Social quests fetched successfully.", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error fetching social quests: {e}", Fore.RED)
            return {"quests": [], "verification_results": []}

        # Iterate over the fetched quests and verify each one
        for quest in quests:
            quest_id = quest.get("id")
            if not quest_id:
                self.log("❌ Quest without an ID found, skipping...", Fore.RED)
                continue

            verify_url = f"{base_url}{quest_id}/verify"
            # Construct verification headers using self.HEADERS and include an origin header
            verify_headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}", "origin": "https://fishingfrenzy.co"}
            try:
                self.log(f"📡 Verifying quest with ID {quest_id}...", Fore.CYAN)
                verify_response = requests.post(verify_url, headers=verify_headers, data=json.dumps({}))
                verify_response.raise_for_status()
                result = verify_response.json()
                self.log(f"✅ Quest {quest_id} verified successfully.", Fore.GREEN)
                verification_results.append({"id": quest_id, "result": result})
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Error verifying quest {quest_id}: {e}", Fore.RED)
                verification_results.append({"id": quest_id, "result": None})

        return {"quests": quests, "verification_results": verification_results}

if __name__ == "__main__":
    fishing = fishingfrenzy()
    index = 0
    max_index = len(fishing.query_list)
    config = fishing.load_config()
    proxies = fishing.load_proxies()

    fishing.log("🎉 [LIVEXORDS] === Welcome to Fishing Frenzy Automation === [LIVEXORDS]", Fore.YELLOW)
    fishing.log(f"📂 Loaded {max_index} accounts from query list.", Fore.YELLOW)

    while True:
        current_account = fishing.query_list[index]
        display_account = current_account[:10] + "..." if len(current_account) > 10 else current_account

        fishing.log(f"👤 [ACCOUNT] Processing account {index + 1}/{max_index}: {display_account}", Fore.YELLOW)

        fishing.override_requests()

        fishing.login(index)

        fishing.log("🛠️ Starting task execution...")
        tasks = {
            "daily": "🌞 Daily Check-In - Log in daily to receive rewards and bonuses.",
            "sell_all_fish": "🐟 Sell All Fish - Convert your caught fish into extra gold.",
            "upgrade_skill": "🚀 Upgrade Skill - Enhance your fishing abilities for better results.",
            "quest": "📜 Quest - Complete exciting quests to earn rewards and unlock achievements.",
            "fishing": "🎣 Fishing Tester - Try out the fishing simulation and test your strategy."
        }

        for task_key, task_name in tasks.items():
            task_status = config.get(task_key, False)
            fishing.log(f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}", Fore.YELLOW if task_status else Fore.RED)

            if task_status:
                fishing.log(f"🔄 Executing {task_name}...")
                getattr(fishing, task_key)()

        if index == max_index - 1:
            fishing.log("🔁 All accounts processed. Restarting loop.")
            fishing.log(f"⏳ Sleeping for {config.get('delay_loop', 30)} seconds before restarting.")
            time.sleep(config.get("delay_loop", 30))
            index = 0
        else:
            fishing.log(f"➡️ Switching to the next account in {config.get('delay_account_switch', 10)} seconds.")
            time.sleep(config.get("delay_account_switch", 10))
            index += 1