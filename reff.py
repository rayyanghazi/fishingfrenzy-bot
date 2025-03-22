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
import os

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
        self.query_list = self.load_query("query_reff.txt")
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
            with open("config_reff.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config_reff.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log("❌ Failed to parse config_reff.json. Please check the file format.", Fore.RED)
            return {}

    def load_query(self, path_file: str = "query_reff.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def reff(self, index: int) -> None:
        self.log("🔒 Attempting to log in (reff)...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        # Ambil data dari query_list, diharapkan dengan format "referralCode|<generate_count>"
        raw = self.query_list[index]
        parts = raw.split('|')
        if len(parts) < 2:
            self.log("❌ Invalid format. Expected format: <referralCode>|<generate_count>", Fore.RED)
            return

        referral_code = parts[0].strip()
        try:
            generate_count = int(parts[1].strip())
        except ValueError:
            self.log("❌ Generate count is not a valid integer.", Fore.RED)
            return

        req_url = f"{self.BASE_URL}auth/guest-login"
        headers = {**self.HEADERS}

        for i in range(generate_count):
            self.log(f"🔄 Generation {i+1}/{generate_count} - Attempting guest login...", Fore.CYAN)
            
            # Generate device id secara otomatis (menggunakan uuid4)
            generated_device_id = str(uuid.uuid4())
            payload = {"deviceId": generated_device_id}
            
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
                    continue

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
                    continue

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
                    continue

                # Setelah login berhasil, verifikasi referral code
                ref_verify_url = f"{self.BASE_URL}reference-code/verify?code={referral_code}"
                self.log(f"📡 Verifying referral code: {referral_code}", Fore.CYAN)
                ref_response = requests.post(ref_verify_url, headers=verify_headers)
                ref_response.raise_for_status()
                ref_data = ref_response.json()
                self.log("✅ Referral code verified successfully.", Fore.GREEN)
                self.log(f"ℹ️ Referral response: {ref_data}", Fore.LIGHTCYAN_EX)
                
                # Simpan device id yang berhasil ke file result_query.txt dengan format "deviceid|guest"
                result_file = "result_query.txt"
                with open(result_file, "a") as f:
                    f.write(f"{generated_device_id}|guest\n")
                self.log(f"💾 Saved device id {generated_device_id}|guest to {result_file}", Fore.GREEN)

            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to send request on iteration {i+1}: {e}", Fore.RED)
                self.log(f"📄 Response content: {response.text if 'response' in locals() else 'No response'}", Fore.RED)
            except ValueError as e:
                self.log(f"❌ Data error (possible JSON issue) on iteration {i+1}: {e}", Fore.RED)
                self.log(f"📄 Response content: {response.text if 'response' in locals() else 'No response'}", Fore.RED)
            except KeyError as e:
                self.log(f"❌ Key error on iteration {i+1}: {e}", Fore.RED)
                self.log(f"📄 Response content: {response.text if 'response' in locals() else 'No response'}", Fore.RED)
            except Exception as e:
                self.log(f"❌ Unexpected error on iteration {i+1}: {e}", Fore.RED)
                self.log(f"📄 Response content: {response.text if 'response' in locals() else 'No response'}", Fore.RED)

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

    await asyncio.to_thread(fishing.reff, original_index)

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
