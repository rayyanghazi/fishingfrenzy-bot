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
from fake_useragent import UserAgent

class fishingfrenzy:
    BASE_URL = "https://api.fishingfrenzy.co/v1/"
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Origin": "https://fishingfrenzy.co",
        "Referer": "https://fishingfrenzy.co/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "sec-ch-ua": '"Chromium";v="132", "Microsoft Edge";v="132", "Not A(Brand";v="8", "Microsoft Edge WebView2";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    def __init__(self):
        self.config = self.load_config()
        self.query_list = self.load_query("query.txt")
        self.access_token = None
        self.refresh_token = None
        self.energy = 0
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
        Loads a list of queries from the specified file. If self.config["run_with_reff"]
        is True, it also loads queries from "result_reff.txt" and appends them to the list.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries combined from the provided file and, optionally, from result_reff.txt.
        """
        self.banner()

        queries = []
        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]
            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)
            else:
                self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries from {path_file}: {e}", Fore.RED)

        # Jika konfigurasi run_with_reff true, juga muat file result_query.txt
        if self.config.get("run_with_reff", False):
            reff_file = "result_query.txt"
            try:
                with open(reff_file, "r") as file:
                    reff_queries = [line.strip() for line in file if line.strip()]
                if reff_queries:
                    self.log(f"✅ Loaded {len(reff_queries)} queries from {reff_file}.", Fore.GREEN)
                    queries.extend(reff_queries)
                else:
                    self.log(f"⚠️ Warning: {reff_file} is empty.", Fore.YELLOW)
            except FileNotFoundError:
                self.log(f"❌ File not found: {reff_file}", Fore.RED)
            except Exception as e:
                self.log(f"❌ Unexpected error loading queries from {reff_file}: {e}", Fore.RED)

        return queries

    def login(self, index: int) -> None:
        self.log("🔒 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        # Ambil data dari query_list, diharapkan dengan format "value|type" 
        # dimana type bisa "guest" atau "token"
        raw = self.query_list[index]
        parts = raw.split('|')
        if len(parts) < 2:
            self.log("❌ Invalid format. Expected format: <value>|<guest/token>", Fore.RED)
            return

        login_type = parts[1].strip().lower()
        
        if login_type == "guest":
            device_id = parts[0].strip()
            self.log("🌐 Logging in via Web", Fore.CYAN)
            req_url = f"{self.BASE_URL}auth/guest-login"

            # Payload hanya memuat deviceId
            payload = {
                "deviceId": device_id
            }
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

                # Verifikasi token yang baru didapat
                verify_url = f"{self.BASE_URL}auth/verify-tokens"
                verify_payload = {"accessToken": self.access_token}
                verify_headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

                self.log("🔍 Verifying access token...", Fore.CYAN)
                verify_response = requests.post(verify_url, headers=verify_headers, json=verify_payload)
                if verify_response.status_code == 200:
                    self.log("✅ Access token successfully verified.", Fore.GREEN)
                    self.access_token = verify_response.json()['access'].get('token', self.access_token)
                else:
                    self.log(f"❌ Token verification failed. Status: {verify_response.status_code}", Fore.RED)
                    self.log(f"📄 Response: {verify_response.text}", Fore.RED)
                    return

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

        elif login_type == "token":
            # Langsung menggunakan token yang diberikan untuk verifikasi
            self.access_token = parts[0].strip()
            verify_url = f"{self.BASE_URL}auth/verify-tokens"
            verify_payload = {"accessToken": self.access_token}
            verify_headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

            try:
                self.log("🔍 Verifying provided access token...", Fore.CYAN)
                verify_response = requests.post(verify_url, headers=verify_headers, json=verify_payload)
                if verify_response.status_code == 200:
                    self.log("✅ Access token successfully verified.", Fore.GREEN)
                    self.access_token = verify_response.json()['access'].get('token', self.access_token)
                else:
                    self.log(f"❌ Token verification failed. Status: {verify_response.status_code}", Fore.RED)
                    self.log(f"📄 Response: {verify_response.text}", Fore.RED)
                    return

                # Mengambil informasi user dari response verifikasi (jika tersedia)
                user_info = verify_response.json().get("user", {})
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
                self.log(f"❌ Failed to send verify request: {e}", Fore.RED)
                self.log(f"📄 Response content: {verify_response.text}", Fore.RED)
            except ValueError as e:
                self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
                self.log(f"📄 Response content: {verify_response.text}", Fore.RED)
            except KeyError as e:
                self.log(f"❌ Key error: {e}", Fore.RED)
                self.log(f"📄 Response content: {verify_response.text}", Fore.RED)
            except Exception as e:
                self.log(f"❌ Unexpected error: {e}", Fore.RED)
                self.log(f"📄 Response content: {verify_response.text}", Fore.RED)

        else:
            self.log("❌ Unknown login type. Use 'guest' or 'token' after the '|' delimiter.", Fore.RED)

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
        Connects to the WebSocket server and runs fishing sessions automatically until energy is exhausted.
        Each fishing session will prioritize the option with energy cost 3 (long_range). If there isn't enough energy,
        it will try the option with energy cost 2 (mid_range) or 1 (short_range) in order.
        """
        # Parameters for collecting key frames and interpolation.
        required_frames = 10        # Send "end" after receiving 10 key frames.
        interpolation_steps = 30    # Number of interpolation steps between key frames.

        # Linear interpolation between two points (only for coordinates [x, y]).
        def interpolate_points(p0, p1, steps):
            pts = []
            # Skip repeating the starting point; iterate from 1 to steps-1.
            for i in range(1, steps):
                t = i / float(steps)
                x = round(p0[0] + (p1[0] - p0[0]) * t)
                y = round(p0[1] + (p1[1] - p0[1]) * t)
                pts.append([x, y])
            return pts

        inventory_url = f"{self.BASE_URL}inventory"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        while True:
            # --- Refresh energy from the server ---
            try:
                self.log("📡 Refreshing inventory to update energy...", Fore.CYAN)
                inv_response = requests.get(inventory_url, headers=headers)
                inv_response.raise_for_status()
                inv_data = inv_response.json()
                self.energy = inv_data.get("energy", 0)
                self.log(f"✅ Current energy: {self.energy}", Fore.GREEN)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to refresh energy: {e}", Fore.RED)
                return 0

            if self.energy <= 0:
                self.log("ℹ️ No energy left. Exiting fishing loop.", Fore.YELLOW)
                break

            # --- Select the fishing option based on current energy ---
            if self.energy >= 3:
                range_type = "long_range"
                energy_cost = 3
            elif self.energy >= 2:
                range_type = "mid_range"
                energy_cost = 2
            else:
                range_type = "short_range"
                energy_cost = 1

            # Check if energy is sufficient for the selected option.
            if self.energy < energy_cost:
                self.log("⚠️ Not enough energy for the current option. Attempting to buy and use sushi...", Fore.YELLOW)
                result = self.buy_and_use_sushi()
                if result == 0:
                    self.log("❌ Not enough gold to buy sushi. Continuing loop to refresh energy...", Fore.YELLOW)
                time.sleep(1)
                continue

            self.bait()
            self.log(f"🎣 Starting fishing session with type: {range_type} (energy cost: {energy_cost}) (current energy: {self.energy})", Fore.CYAN)

            ws_url = f"wss://api.fishingfrenzy.co/?token={self.access_token}"
            try:
                self.log("📡 Connecting to WebSocket server...", Fore.CYAN)
                ws = websocket.create_connection(ws_url)
                ws.settimeout(3)  # Set timeout so that recv() does not block indefinitely.
                self.log("✅ Connected to WebSocket server.", Fore.GREEN)

                # List to store key frames from "gameState" messages.
                key_frames = []
                end_sent = False  # Flag to ensure "end" is sent only once.

                last_message_time = time.time()  # Timestamp of the last received message.
                max_idle_time = 10  # Maximum time (in seconds) to wait for a new message.

                # Functions to calculate positions based on frame and direction.
                def calculate_position_x(frame: int, direction: int) -> int:
                    return 450 + frame * 2 + direction * 5

                def calculate_position_y(frame: int, direction: int) -> int:
                    return 426 + frame * 2 - direction * 3

                # Function to send the "prepare" command.
                def start_new_game():
                    prepare_msg = json.dumps({"cmd": "prepare", "range": range_type})
                    ws.send(prepare_msg)
                    self.log("📡 Sent 'prepare' command. Getting ready for fishing...", Fore.CYAN)

                # Function to send the "end" command after interpolating key frames.
                def end_game():
                    nonlocal end_sent
                    if end_sent:
                        return
                    end_sent = True

                    # If only one key frame exists, no interpolation is needed.
                    if len(key_frames) < 2:
                        final_frames = key_frames.copy()
                    else:
                        final_frames = []
                        # Add the first key frame.
                        final_frames.append(key_frames[0])
                        # Interpolate between key frames.
                        for i in range(1, len(key_frames)):
                            prev = key_frames[i - 1]
                            curr = key_frames[i]
                            # Use only the coordinates for interpolation.
                            p0 = prev[0:2]
                            p1 = curr[0:2]
                            interpolated_pts = interpolate_points(p0, p1, interpolation_steps)
                            final_frames.extend(interpolated_pts)
                            # Add the current key frame.
                            final_frames.append(curr)

                    fps_value = 20  # Example payload value.
                    self.log(f"📡 Final frame data contains {len(final_frames)} points from {len(key_frames)} key frames.", Fore.CYAN)
                    end_payload = {
                        "cmd": "end",
                        "rep": {
                            "fs": 100,
                            "ns": 200,
                            "fps": fps_value,
                            "frs": final_frames
                        },
                        "en": 1
                    }
                    self.log("📡 Sending 'end' command...", Fore.CYAN)
                    ws.send(json.dumps(end_payload))
                    time.sleep(1)

                # Start the session with a "prepare" command.
                start_new_game()

                # Loop to receive messages from the server.
                while True:
                    try:
                        message = ws.recv()
                        last_message_time = time.time()  # Update last message timestamp.
                    except websocket.WebSocketTimeoutException:
                        if time.time() - last_message_time > max_idle_time:
                            self.log("⚠️ No response received within idle time. Breaking out of loop.", Fore.YELLOW)
                            break
                        continue

                    if not message:
                        if time.time() - last_message_time > max_idle_time:
                            self.log("⚠️ No message content received for a while. Breaking out of loop.", Fore.YELLOW)
                            break
                        continue

                    try:
                        parsed = json.loads(message)
                    except json.JSONDecodeError:
                        self.log("❌ Failed to parse message from server.", Fore.RED)
                        continue

                    msg_type = parsed.get("type")
                    if msg_type == "initGame":
                        # Initialization message.
                        start_msg = json.dumps({"cmd": "start"})
                        ws.send(start_msg)
                        self.log("📡 Sent 'start' command. Fishing started...", Fore.CYAN)

                    elif msg_type == "gameState":
                        if end_sent:
                            continue

                        # Process the gameState message as a key frame.
                        frame = parsed.get("frame", 0)
                        direction = parsed.get("dir", 0)
                        x = calculate_position_x(frame, direction)
                        y = calculate_position_y(frame, direction)

                        if direction != 0:
                            entry = [x, y, frame, direction]
                            self.log(f"🎯 Received key frame (full info): {entry}", Fore.MAGENTA)
                        else:
                            entry = [x, y]
                            self.log(f"🎯 Received key frame (coordinates only): {entry}", Fore.MAGENTA)
                        key_frames.append(entry)

                        # Once the required number of key frames is reached, send the "end" command.
                        if len(key_frames) == required_frames:
                            self.log("⚠️ Reached 10 key frames. Sending 'end' message...", Fore.YELLOW)
                            end_game()

                    elif msg_type == "gameOver":
                        if parsed.get("success"):
                            self.log("✅ Session succeeded!", Fore.GREEN)
                            catched = parsed.get("catchedFish", {})
                            if catched:
                                fish_info = catched.get("fishInfo", {})
                                self.log("🐟 Fishing Result:", Fore.LIGHTCYAN_EX)
                                self.log(f"   - Fish Name      : {fish_info.get('fishName', 'N/A')}", Fore.LIGHTCYAN_EX)
                                self.log(f"   - EXP Gain       : {fish_info.get('expGain', 'N/A')}", Fore.LIGHTCYAN_EX)
                                self.log(f"   - Sell Price     : {fish_info.get('sellPrice', 'N/A')}", Fore.LIGHTCYAN_EX)
                                self.log(f"   - Current EXP    : {catched.get('currentExp', 'N/A')}", Fore.LIGHTCYAN_EX)
                                self.log(f"   - Level          : {catched.get('level', 'N/A')}", Fore.LIGHTCYAN_EX)
                                self.log(f"   - EXP to Next    : {catched.get('expToNextLevel', 'N/A')}", Fore.LIGHTCYAN_EX)
                            else:
                                self.log("⚠️ No fish data received.", Fore.YELLOW)
                        else:
                            self.log("❌ Session failed.", Fore.RED)
                        # If "end" has not been sent but enough key frames have been collected, send "end".
                        if not end_sent and len(key_frames) >= required_frames:
                            end_game()
                        break

                ws.close()

                # Do not decrease self.energy manually; it will be refreshed from the server at the start of the next iteration.
                time.sleep(1)
                # If energy is still low, try buying sushi before next session.
                if self.energy < energy_cost:
                    self.log("⚠️ Not enough energy for fishing. Attempting to buy and use sushi...", Fore.YELLOW)
                    result = self.buy_and_use_sushi()
                    if result == 0:
                        self.log("❌ Not enough gold to buy sushi. Continuing loop...", Fore.YELLOW)
                    time.sleep(1)
                # Continue the loop to refresh energy and start a new session.
                continue

            except Exception as e:
                self.log(f"❌ Error during fishing session: {e}", Fore.RED)
                return 0

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
        """
        Sells all fish in the inventory by:
        1. Mengambil data inventory dengan GET request ke {self.BASE_URL}inventory.
        2. Mengambil list ikan dari field "list_fish_info" -> "inGame".
        3. Untuk setiap ikan, melakukan POST request ke {self.BASE_URL}fish/sell dengan payload:
            {"fishInfoId": <id_ikan>, "quantity": <quantity_ikan>}
        
        Menggunakan header yang sama dengan tambahan "authorization". 
        Jika semua ikan berhasil dijual, fungsi akan mengembalikan 1, sebaliknya akan mengembalikan 0.
        """
        # URL inventory
        req_url_inventory = f"{self.BASE_URL}inventory"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}
        
        # --- FETCH INVENTORY ---
        try:
            self.log("📡 Fetching inventory...", Fore.CYAN)
            inv_response = requests.get(req_url_inventory, headers=headers)
            inv_response.raise_for_status()
            inventory_data = inv_response.json()
            self.log("✅ Inventory fetched successfully.", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error fetching inventory: {e}", Fore.RED)
            return 0
        
        # Ambil list ikan dari inventory (bagian "inGame")
        fish_list = inventory_data.get("list_fish_info", {}).get("inGame", [])
        if not fish_list:
            self.log("ℹ️ No fish found in inventory.", Fore.MAGENTA)
            return 1  # Tidak ada ikan yang harus dijual
        
        sell_all_success = True
        sell_url = f"{self.BASE_URL}fish/sell"
        
        # --- ITERASI DAN JUAL IKAN ---
        for fish in fish_list:
            fish_id = fish.get("id")
            quantity = fish.get("quantity")
            fish_name = fish.get("fishName", "Unknown")
            if not fish_id or not quantity:
                self.log("❌ Fish with missing ID or quantity found, skipping...", Fore.RED)
                continue
            
            payload = {
                "fishInfoId": fish_id,
                "quantity": quantity
            }
            
            try:
                self.log(f"📡 Selling fish {fish_name} (ID: {fish_id}) with quantity {quantity}...", Fore.CYAN)
                sell_response = requests.post(sell_url, headers=headers, json=payload)
                sell_response.raise_for_status()
                if sell_response.status_code == 200:
                    self.log(f"✅ Fish {fish_name} sold successfully.", Fore.GREEN)
                else:
                    self.log(f"❌ Failed to sell fish {fish_name}. Status: {sell_response.status_code}", Fore.RED)
                    sell_all_success = False
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Error selling fish {fish_name}: {e}", Fore.RED)
                sell_all_success = False
        
        return 1 if sell_all_success else 0
    
    def battle_pass(self) -> int:
        """
        Checks the user's Battle Pass status and automatically claims available FREE rewards.
        
        Steps:
        1. Retrieve battle pass data via GET {self.BASE_URL}battle-pass.
        2. Loop through the 'milestones' list and check if any milestone's free reward is claimable 
        (i.e. status is "Unclaimed" and claimedFree is False).
        3. For each eligible milestone, send a POST request to {self.BASE_URL}battle-pass/claim-reward
        with payload: {"battlePassId": <battlePassId>, "level": <level>, "rewardType": "FREE"}.
        4. Logs the result for each claim and returns 1 if the process is completed.
        
        Returns:
            int: 1 if the claim process has been executed (even if no claimable rewards), 0 if error occurs.
        """
        battle_pass_url = f"{self.BASE_URL}battle-pass"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        try:
            self.log("📡 Checking battle pass status...", Fore.CYAN)
            response = requests.get(battle_pass_url, headers=headers)
            response.raise_for_status()
            bp_data = response.json()

            # Ambil battlePassId dan milestones dari response
            bp_id = bp_data.get("battlePassId")
            milestones = bp_data.get("milestones", [])
            claimed_count = 0

            if not bp_id:
                self.log("❌ Battle pass ID not found.", Fore.RED)
                return 0

            # Loop melalui tiap milestone untuk claim reward FREE jika belum diklaim
            for milestone in milestones:
                # Pastikan reward free belum diklaim dan statusnya "Unclaimed"
                if milestone.get("status") == "Unclaimed" and not milestone.get("claimedFree", True):
                    level = milestone.get("level")
                    payload = {
                        "battlePassId": bp_id,
                        "level": level,
                        "rewardType": "FREE"
                    }
                    claim_url = f"{self.BASE_URL}battle-pass/claim-reward"
                    claim_response = requests.post(claim_url, headers=headers, json=payload)
                    claim_response.raise_for_status()
                    self.log(f"✅ Claimed FREE reward for level {level}.", Fore.GREEN)
                    claimed_count += 1

            if claimed_count == 0:
                self.log("ℹ️ No FREE rewards available to claim.", Fore.YELLOW)
            return 1

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to process battle pass claim: {e}", Fore.RED)
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
        3. If the Sushi count is low (less than 5) and energy belum penuh, attempts to purchase more,
        kemudian langsung menggunakan sushi yang baru dibeli.
        
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
                # Set default values if Sushi is not found
                sushi_effect = 5     # Default energy restored per sushi
                sushi_price = 500    # Default price in gold

            # Fungsi untuk langsung pakai sushi (gunakan satu per satu)
            def use_sushi(times: int) -> None:
                nonlocal energy
                for _ in range(times):
                    req_url_use_sushi = f"{self.BASE_URL}items/{sushi_id}/use?userId={user_id}&quantity=1"
                    use_response = requests.get(req_url_use_sushi, headers=headers)
                    use_response.raise_for_status()
                    data_use = use_response.json()
                    energy = data_use.get('energy', energy)
                    self.energy = energy
                if times > 0:
                    self.log(f"✅ Used {times} Sushi to restore energy. Current energy: {energy}", Fore.GREEN)

            # Calculate how much energy is needed
            energy_needed = max_energy - energy
            if energy_needed > 0:
                # Tentukan berapa sushi yang diperlukan (gunakan pembagian integer)
                needed_sushi = energy_needed // sushi_effect
                if energy_needed % sushi_effect != 0:
                    needed_sushi += 1
                # Gunakan sushi yang tersedia di inventory
                used_sushi = min(sushi_quantity, needed_sushi)
                if used_sushi > 0:
                    use_sushi(used_sushi)
                    sushi_quantity -= used_sushi
                else:
                    self.log("ℹ️ Not enough Sushi in inventory to restore energy.", Fore.YELLOW)
            else:
                self.log("ℹ️ Your energy is already full.", Fore.YELLOW)

            # Jika energi belum penuh dan jumlah sushi kurang dari 5, coba beli dan langsung pakai
            if self.energy < max_energy and sushi_quantity < 5:
                max_buyable = gold // sushi_price if sushi_price > 0 else 0
                if max_buyable > 0:
                    # Beli sushi hingga maksimal 5 buah (atau sesuai kebutuhan untuk full energy)
                    needed_after = max_energy - self.energy
                    needed_sushi_after = needed_after // sushi_effect
                    if needed_after % sushi_effect != 0:
                        needed_sushi_after += 1
                    buy_quantity = min(max_buyable, 5, needed_sushi_after)
                    req_url_buy_sushi = f"{self.BASE_URL}items/{sushi_id}/buy?userId={user_id}&quantity={buy_quantity}"
                    buy_response = requests.get(req_url_buy_sushi, headers=headers)
                    buy_response.raise_for_status()
                    self.log(f"✅ Purchased {buy_quantity} Sushi.", Fore.GREEN)
                    # Setelah beli, langsung gunakan sushi tersebut
                    use_sushi(buy_quantity)
                else:
                    self.log("❌ Not enough gold to buy Sushi.", Fore.RED)
                    return 0

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
        Retrieves the inventory data from the server and checks the user's level.
        If the level is below 5, the upgrade process is halted.
        Otherwise, it retrieves the accessories data, displays the current status of each skill,
        and then attempts to upgrade the first eligible skill based on the priority order.

        Priority order for upgrades:
            1. Rod Handle (Reduces Energy Consumption) 🔋
            2. Icebox (Increases Gold Income) 💰
            3. Fishing Manual (Increases EXP per Catch) 📖
            4. Lucky Charm (Increases Chance for Item Drop) 🍀
            5. Cutting Board (Reduces Bait Consumption) 🎣
        """
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}
        
        # --- Step 1: Retrieve Inventory Data ---
        req_url_inventory = f"{self.BASE_URL}inventory"
        try:
            self.log("📡 Retrieving inventory data...", Fore.CYAN)
            inv_response = requests.get(req_url_inventory, headers=headers)
            inv_response.raise_for_status()
            inv_data = inv_response.json()
            user_level = inv_data.get("level", 0)
            self.log(f"✅ Inventory retrieved. User level: {user_level}", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error retrieving inventory data: {e}", Fore.RED)
            return 0

        # Check if user's level is at least 5.
        if user_level < 5:
            self.log("ℹ️ User level is below 5. Skill upgrades are available only from level 5.", Fore.YELLOW)
            return 0

        # --- Step 2: Retrieve Accessories Data and Attempt Upgrade ---
        req_url_accessories = f"{self.BASE_URL}accessories"
        try:
            self.log("📡 Retrieving accessories data...", Fore.CYAN)
            response = requests.get(req_url_accessories, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Retrieve available upgrade points and accessories list.
            available_upgrade_points = data.get("availableUpgradePoint", 0)
            accessories = data.get("accessories", [])

            # Display the list of skills with their current level and effect.
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

            # Check if the user has any upgrade points available.
            if available_upgrade_points <= 0:
                self.log("❌ You don't have enough upgrade points to upgrade any skill.", Fore.RED)
                return 0

            # Define the upgrade priority order by skill name.
            priority_order = [
                "Rod Handle",      # 1. Reduces Energy Consumption
                "Icebox",          # 2. Increases Gold Income
                "Fishing Manual",  # 3. Increases EXP per Catch
                "Lucky Charm",     # 4. Increases Chance for Item Drop
                "Cutting Board",   # 5. Reduces Bait Consumption
            ]

            # Iterate over the priority order to find a skill that can be upgraded.
            for skill_name in priority_order:
                # Find the accessory with the matching name.
                accessory = next((acc for acc in accessories if acc.get("name") == skill_name), None)
                if accessory:
                    current_level = accessory.get("currentLevel", 0)
                    max_level = accessory.get("maxLevel", 0)
                    # Ensure the skill hasn't reached its maximum level.
                    if current_level < max_level:
                        accessory_id = accessory.get("accessoryId")
                        req_url_upgrade = f"{self.BASE_URL}accessories/{accessory_id}/upgrade"
                        self.log(f"📡 Upgrading '{skill_name}'...", Fore.CYAN)
                        upgrade_response = requests.post(req_url_upgrade, headers=headers)
                        upgrade_response.raise_for_status()

                        if upgrade_response.status_code == 200:
                            self.log(f"✅ '{skill_name}' has been successfully upgraded.", Fore.GREEN)
                            return 1  # Upgrade succeeded; exit the function.
                        else:
                            self.log(f"❌ Failed to upgrade '{skill_name}'. Status Code: {upgrade_response.status_code}", Fore.RED)
                            self.log(f"📄 Response: {upgrade_response.text}", Fore.RED)
                            return 0
                    else:
                        self.log(f"ℹ️ '{skill_name}' is already at max level ({max_level}). Skipping...", Fore.MAGENTA)
                else:
                    self.log(f"ℹ️ Skill '{skill_name}' not found in your accessories list. Skipping...", Fore.MAGENTA)

            # If no eligible skill was found for upgrade.
            self.log("ℹ️ No eligible skill found for upgrade.", Fore.YELLOW)
            return 0

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
        Additionally, it fetches the list of daily quests and claims those that are completed but not yet claimed.
        
        Setelah proses verifikasi social quest, fungsi akan melakukan request ulang untuk mendapatkan
        data social quest yang terbaru dan melakukan claim pada quest yang sudah terverifikasi namun belum di-claim.
        
        Returns:
            A dictionary with four keys:
                - "quests": the original list of social quests fetched from the server.
                - "verification_results": a list of results from verifying each social quest.
                - "social_claim_results": a list of results from claiming each verified social quest.
                - "daily_claim_results": a list of results from claiming each daily quest.
        """

        # Social quests URL is hard-coded, while daily quests use the BASE_URL of the instance.
        social_quests_url = f"{self.BASE_URL}social-quests"
        daily_quests_url = f"{self.BASE_URL}user-quests"
        
        # Prepare headers for authentication.
        get_headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}
        
        verification_results = []
        social_claim_results = []
        daily_claim_results = []
        
        # --- SOCIAL QUESTS FETCH AND VERIFICATION ---
        try:
            self.log("📡 Fetching social quests...", Fore.CYAN)
            response = requests.get(social_quests_url, headers=get_headers)
            response.raise_for_status()
            quests = response.json()
            self.log("✅ Social quests fetched successfully.", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error fetching social quests: {e}", Fore.RED)
            quests = []

        # Iterate over the fetched social quests and verify only those that are necessary.
        for quest in quests:
            quest_id = quest.get("id")
            if not quest_id:
                self.log("❌ Quest without an ID found, skipping...", Fore.RED)
                continue

            # Only verify quests that are unclaimed (status must be "UnClaimed").
            if quest.get("status") != "UnClaimed":
                self.log(f"ℹ️ Skipping quest {quest_id} as it is already claimed.", Fore.MAGENTA)
                continue

            verify_url = f"{social_quests_url}/{quest_id}/verify"
            try:
                self.log(f"📡 Verifying quest with ID {quest_id}...", Fore.CYAN)
                verify_response = requests.post(verify_url, headers=get_headers, data=json.dumps({}), timeout=10)
                verify_response.raise_for_status()
                result = verify_response.json()
                self.log(f"✅ Quest {quest_id} verified successfully.", Fore.GREEN)
                verification_results.append({"id": quest_id, "result": result})
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Error verifying quest {quest_id}: {e}", Fore.RED)
                verification_results.append({"id": quest_id, "result": None})
        
        # --- SOCIAL QUESTS RE-FETCH AND CLAIMING ---
        try:
            self.log("📡 Re-fetching social quests after verification...", Fore.CYAN)
            refetch_response = requests.get(social_quests_url, headers=get_headers)
            refetch_response.raise_for_status()
            updated_quests = refetch_response.json()
            self.log("✅ Social quests re-fetched successfully.", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error re-fetching social quests: {e}", Fore.RED)
            updated_quests = []

        # Iterate over the updated social quests and claim the ones that are verified but not yet claimed.
        for quest in updated_quests:
            quest_id = quest.get("id")
            if quest.get("status") == "UnClaimed":
                claim_url = f"{social_quests_url}/{quest_id}/claim"
                try:
                    self.log(f"📡 Claiming verified social quest with ID {quest_id}...", Fore.CYAN)
                    claim_response = requests.post(claim_url, headers=get_headers)
                    claim_response.raise_for_status()
                    if claim_response.status_code == 200:
                        self.log(f"✅ Social quest {quest_id} claimed successfully.", Fore.GREEN)
                        social_claim_results.append({"id": quest_id, "claimed": True})
                    else:
                        self.log(f"❌ Failed to claim social quest {quest_id}. Status Code: {claim_response.status_code}", Fore.RED)
                        social_claim_results.append({"id": quest_id, "claimed": False})
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Error claiming social quest {quest_id}: {e}", Fore.RED)
                    social_claim_results.append({"id": quest_id, "claimed": False})
        
        # --- DAILY QUESTS FETCH AND CLAIMING ---
        try:
            self.log("📡 Fetching daily quests...", Fore.CYAN)
            daily_response = requests.get(daily_quests_url, headers=get_headers)
            daily_response.raise_for_status()
            daily_quests = daily_response.json()
            self.log("✅ Daily quests fetched successfully.", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error fetching daily quests: {e}", Fore.RED)
            daily_quests = []

        # Iterate over the daily quests and claim the ones that are completed but not yet claimed.
        for dq in daily_quests:
            # Check if the quest is a daily quest, is completed, and not yet claimed.
            if dq.get("isCompleted") and not dq.get("isClaimed"):
                quest_id = dq.get("id")
                claim_url = f"{daily_quests_url}/{quest_id}/claim"
                try:
                    self.log(f"📡 Claiming daily quest with ID {quest_id}...", Fore.CYAN)
                    claim_response = requests.post(claim_url, headers=get_headers)
                    claim_response.raise_for_status()
                    if claim_response.status_code == 200:
                        self.log(f"✅ Daily quest {quest_id} claimed successfully.", Fore.GREEN)
                        daily_claim_results.append({"id": quest_id, "claimed": True})
                    else:
                        self.log(f"❌ Failed to claim daily quest {quest_id}. Status Code: {claim_response.status_code}", Fore.RED)
                        daily_claim_results.append({"id": quest_id, "claimed": False})
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Error claiming daily quest {quest_id}: {e}", Fore.RED)
                    daily_claim_results.append({"id": quest_id, "claimed": False})
        
        return {
            "quests": quests,
            "verification_results": verification_results,
            "social_claim_results": social_claim_results,
            "daily_claim_results": daily_claim_results
        }

    def event(self) -> int:
        """Switches to the event theme."""
        req_url_event = f"{self.BASE_URL}events/6780f4c7a48b6c2b29d82bf6/themes/6752b7a7ef93f2489cfef709/switch"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        try:
            self.log("🟡 Switching to event theme...", Fore.CYAN)
            response = requests.get(req_url_event, headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                self.log("✅ Successfully switched to the event theme.", Fore.GREEN)
                return 1
            else:
                self.log(f"❌ Failed to switch event. Status: {response.status_code}", Fore.RED)
                self.log(f"📄 Response: {response.text}", Fore.RED)
                return 0

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to switch event: {e}", Fore.RED)
            return 0
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            return 0

    def bait(self) -> int:
        """
        Uses all available bait items (all variations) from the inventory.
        
        Process:
        1. Fetch the inventory from {self.BASE_URL}inventory.
        2. Extract the userId and list_item_info.
        3. For each bait item in list_item_info that has a quantity > 0,
        use the bait by making a GET request to:
            {self.BASE_URL}items/{bait_id}/use?userId={userId}&quantity={bait_quantity}
        4. If all bait items are used successfully (or if no bait items have quantity > 0),
        return 1. Otherwise, return 0 in case of any failure.
        
        Returns:
            int: 1 if all bait items were used successfully or none were available,
                0 if any request fails.
        """
        # Step 1: Fetch inventory data
        req_url_inventory = f"{self.BASE_URL}inventory"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}

        try:
            self.log("📡 Fetching inventory...", Fore.CYAN)
            response = requests.get(req_url_inventory, headers=headers)
            response.raise_for_status()
            inventory = response.json()
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch inventory: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0
        except ValueError as e:
            self.log(f"❌ Data error while fetching inventory: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred while fetching inventory: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0

        # Step 2: Extract userId and bait items
        user_id = inventory.get("userId")
        list_item_info = inventory.get("list_item_info", [])
        if not user_id:
            self.log("❌ User ID not found in inventory.", Fore.RED)
            return 0

        # Flag to indicate if at least one bait was processed
        bait_used = False

        # Step 3: Iterate through each bait variation
        for bait_item in list_item_info:
            bait_quantity = bait_item.get("quantity", 0)
            if bait_quantity > 0:
                bait_id = bait_item.get("id")
                bait_name = bait_item.get("name")
                self.log(f"📋 Using bait: {bait_name} (ID: {bait_id}) with quantity: {bait_quantity}", Fore.CYAN)
                req_url_use = f"{self.BASE_URL}items/{bait_id}/use?userId={user_id}&quantity={bait_quantity}"
                try:
                    self.log("📡 Sending request to use bait...", Fore.CYAN)
                    response_use = requests.get(req_url_use, headers=headers)
                    response_use.raise_for_status()

                    if response_use.status_code == 200:
                        self.log(f"✅ Successfully used {bait_quantity} of {bait_name}.", Fore.GREEN)
                        bait_used = True
                    else:
                        self.log(f"❌ Failed to use {bait_name}. Status: {response_use.status_code}", Fore.RED)
                        self.log(f"📄 Response: {response_use.text}", Fore.RED)
                        return 0
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Failed to use {bait_name}: {e}", Fore.RED)
                    self.log(f"📄 Response content: {response_use.text if response_use is not None else 'No response'}", Fore.RED)
                    return 0
                except Exception as e:
                    self.log(f"❌ An unexpected error occurred while using {bait_name}: {e}", Fore.RED)
                    self.log(f"📄 Response content: {response_use.text if response_use is not None else 'No response'}", Fore.RED)
                    return 0

        # Step 4: If no bait items were available or used, log a message and return normally
        if not bait_used:
            self.log("ℹ️ No bait items available to use.", Fore.CYAN)
        return 1
    
    def cooking(self) -> int:
        """
        Cooks an active recipe if the user has sufficient fish ingredients and meets the required cooking level.
        
        Steps:
        1. Retrieve the user's inventory via GET {self.BASE_URL}inventory to get the user's level.
        2. If the user's level is below 15, log that cooking is not available and exit.
        3. If the level is sufficient, retrieve the active cooking recipes via GET {self.BASE_URL}cooking-recipes/active.
        4. From the active recipes, select one where the unlockLevel is less than or equal to the user's cooking level,
        and ensure all required fish components are available in sufficient quantity.
        5. If a valid recipe is found, send a POST to {self.BASE_URL}cooking-recipes/claim with the payload:
        {
            "cookingRecipeId": <recipe_id>,
            "quantity": 1,
            "fishs": [list of userItemIds used for each component],
            "shinyFishs": [],
            "transactionHash": None
        }
        6. Log the result and return 1 if the cooking action is executed successfully; otherwise, log the error and return 0.
        """
        recipes_url = f"{self.BASE_URL}cooking-recipes/active"
        inventory_url = f"{self.BASE_URL}inventory"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}
        
        # --- Step 1: Retrieve User Inventory ---
        try:
            self.log("📡 Retrieving user inventory...", Fore.CYAN)
            inv_response = requests.get(inventory_url, headers=headers)
            inv_response.raise_for_status()
            inv_data = inv_response.json()
            user_level = inv_data.get("level", 0)
            self.log(f"✅ Inventory retrieved. User level: {user_level}", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error retrieving inventory data: {e}", Fore.RED)
            return 0

        # Check if the user level is sufficient (minimum 15)
        if user_level < 15:
            self.log("ℹ️ User level is below 15. Cooking is available only from level 15.", Fore.YELLOW)
            return 0
        
        try:
            # --- Step 2: Retrieve Active Cooking Recipes ---
            self.log("📡 Retrieving active cooking recipes...", Fore.CYAN)
            recipes_response = requests.get(recipes_url, headers=headers)
            recipes_response.raise_for_status()
            recipes_data = recipes_response.json()  # Expecting a list of recipes

            self.log("📡 Retrieving inventory for component validation...", Fore.CYAN)
            inv_response = requests.get(inventory_url, headers=headers)
            inv_response.raise_for_status()
            inv_data = inv_response.json()
            user_cooking_level = inv_data.get("level", 0)
            self.log(f"ℹ️ User cooking level: {user_cooking_level}", Fore.LIGHTCYAN_EX)
            
            # Create a mapping of available fish items by id for easy lookup
            inventory_fish = {}
            for fish in inv_data.get("list_fish_info", {}).get("inGame", []):
                fish_id = fish.get("id")
                if fish_id:
                    inventory_fish[fish_id] = {
                        "quantity": fish.get("quantity", 0),
                        "userItemIds": list(fish.get("userItemIds", []))
                    }
            
            # Function to check if all required components for a recipe are available
            def can_cook_recipe(recipe):
                required_fish_ids = []
                for comp in recipe.get("components", []):
                    comp_id = comp.get("id")
                    comp_qty = comp.get("quantity", 1)
                    inv_item = inventory_fish.get(comp_id)
                    if not inv_item or inv_item["quantity"] < comp_qty or not inv_item["userItemIds"]:
                        return None  # Required component is missing or insufficient
                    # Take one userItemId per required component (assuming quantity is always 1 for simplicity)
                    required_fish_ids.append(inv_item["userItemIds"][0])
                return required_fish_ids
            
            recipe_to_cook = None
            fish_ids_to_use = None
            
            # Iterate through active recipes to find a valid one based on level and available ingredients
            for recipe in recipes_data:
                if not recipe.get("active", False):
                    continue
                if recipe.get("unlockLevel", 0) > user_cooking_level:
                    continue
                fish_ids = can_cook_recipe(recipe)
                if fish_ids:
                    recipe_to_cook = recipe
                    fish_ids_to_use = fish_ids
                    break
            
            if not recipe_to_cook:
                self.log("ℹ️ No available cooking recipe meets your level and ingredient requirements.", Fore.YELLOW)
                return 1
            
            # --- Step 3: Claim the Cooking Recipe ---
            payload = {
                "cookingRecipeId": recipe_to_cook.get("id"),
                "quantity": 1,
                "fishs": fish_ids_to_use,
                "shinyFishs": [],
                "transactionHash": None
            }
            claim_url = f"{self.BASE_URL}cooking-recipes/claim"
            self.log(f"📡 Attempting to cook recipe: {recipe_to_cook.get('name')}", Fore.CYAN)
            claim_response = requests.post(claim_url, headers=headers, json=payload)
            claim_response.raise_for_status()
            claim_result = claim_response.json()
            
            # Log claim result and any rewards received
            rewards = claim_result.get("formattedRewards", [])
            if rewards:
                self.log("✅ Cooking successful! Rewards received:", Fore.GREEN)
                for reward in rewards:
                    self.log(f"   - {reward.get('name')} x {reward.get('quantity')}", Fore.LIGHTCYAN_EX)
            else:
                self.log("ℹ️ Cooking executed, but no rewards were received.", Fore.YELLOW)
            return 1
        
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to process cooking: {e}", Fore.RED)
            return 0
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred during cooking: {e}", Fore.RED)
            return 0
        
    def reff(self) -> int:
        claim_url = f"{self.BASE_URL}reference-code/rewards/claim-all"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.access_token}"}
        
        try:
            self.log("📡 Claiming rewards...", Fore.CYAN)
            response = requests.get(claim_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            remain_seconds = data.get("remainSeconds")
            status = data.get("status")
            message = data.get("message")
            
            self.log(f"✅ Rewards claimed: {message} (Status: {status}, Remain Seconds: {remain_seconds})", Fore.GREEN)
            return 1
        except requests.exceptions.RequestException as err:
            self.log(f"❌ Failed to claim rewards: {err}", Fore.RED)
            return 0
        except Exception as err:
            self.log(f"❌ Error occurred: {err}", Fore.RED)
            return 0

async def process_account(account, original_index, account_label, fishing, config):
    # Set a random fake User-Agent for this account
    ua = UserAgent()
    fishing.HEADERS["User-Agent"] = ua.random

    display_account = account[:10] + "..." if len(account) > 10 else account
    fishing.log(f"👤 Processing {account_label}: {display_account}", Fore.YELLOW)

    # Override proxy if enabled
    if config.get("proxy", False):
        fishing.override_requests()
    else:
        fishing.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)

    # Login (blocking call executed in a thread) using the account's index
    await asyncio.to_thread(fishing.login, original_index)

    fishing.log("🛠️ Starting task execution...", Fore.CYAN)
    tasks_config = {
        "event": "🎉 Event - Switch to event mode.",
        "daily": "🌞 Daily Check-In - Log in for rewards.",
        "sell_all_fish": "🐟 Sell All Fish - Sell your fish for gold.",
        "upgrade_skill": "🚀 Upgrade Skill - Boost your fishing skills.",
        "quest": "📜 Quest - Complete quests for rewards.",
        "battle_pass": "🔥 Battle Pass - Activate for extra challenges.",
        "cooking": "🍳 Cooking - Cook recipes for bonuses.",
        "reff": "🤝 Referral - Claim referral rewards.",
        "fishing": "🎣 Fishing - Try your hand at fishing."
    }

    for task_key, task_name in tasks_config.items():
        task_status = config.get(task_key, False)
        color = Fore.YELLOW if task_status else Fore.RED
        fishing.log(
            f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
            color,
        )
        if task_status:
            fishing.log(f"🔄 Executing {task_name}...", Fore.CYAN)
            await asyncio.to_thread(getattr(fishing, task_key))

    delay_switch = config.get("delay_account_switch", 10)
    fishing.log(
        f"➡️ Finished processing {account_label}. Waiting {Fore.WHITE}{delay_switch}{Fore.CYAN} seconds before next account.",
        Fore.CYAN,
    )
    await asyncio.sleep(delay_switch)


async def worker(worker_id, fishing, config, queue):
    """
    Each worker takes one account from the queue and processes it sequentially.
    A worker will not take a new account until the current one is finished.
    """
    while True:
        try:
            original_index, account = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        account_label = f"Worker-{worker_id} Account-{original_index+1}"
        await process_account(account, original_index, account_label, fishing, config)
        queue.task_done()
    fishing.log(
        f"Worker-{worker_id} finished processing all assigned accounts.", Fore.CYAN
    )


async def main():
    fishing = fishingfrenzy()  
    config = fishing.load_config()
    all_accounts = fishing.query_list
    num_workers = config.get("thread", 1)  # Number of concurrent workers (threads)

    fishing.log(
        "🎉 [LIVEXORDS] === Welcome to fishing Frenzy Automation === [LIVEXORDS]",
        Fore.YELLOW,
    )
    fishing.log(f"📂 Loaded {len(all_accounts)} accounts from query list.", Fore.YELLOW)

    if config.get("proxy", False):
        proxies = fishing.load_proxies()

    while True:
        # Create a new asyncio Queue and add all accounts (with their original index)
        queue = asyncio.Queue()
        for idx, account in enumerate(all_accounts):
            queue.put_nowait((idx, account))

        # Create worker tasks according to the number of threads specified
        workers = [
            asyncio.create_task(worker(i + 1, fishing, config, queue))
            for i in range(num_workers)
        ]

        # Wait until all accounts in the queue are processed
        await queue.join()

        # Cancel workers to avoid overlapping in the next loop
        for w in workers:
            w.cancel()

        fishing.log("🔁 All accounts processed. Restarting loop.", Fore.CYAN)
        delay_loop = config.get("delay_loop", 30)
        fishing.log(
            f"⏳ Sleeping for {Fore.WHITE}{delay_loop}{Fore.CYAN} seconds before restarting.",
            Fore.CYAN,
        )
        await asyncio.sleep(delay_loop)


if __name__ == "__main__":
    asyncio.run(main())
