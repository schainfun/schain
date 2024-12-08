import json
import os
import requests
from eth_account import Account
from colorama import Fore, Style, init
from eth_account.messages import encode_defunct
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
init(autoreset=True)

PUBLIC_RPC = os.getenv("RPC_URL", "https://mainnet-beta.schain.fun")

def save_wallet_to_file(wallet_address, private_key, file_name="wallet.json"):
    wallet_data = {
        "address": wallet_address,
        "private_key": private_key
    }
    with open(file_name, "w") as file:
        json.dump(wallet_data, file, indent=4)
    print(f"{Fore.GREEN}Wallet information saved to {file_name}")

def check_existing_wallet(file_name="wallet.json"):
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            wallet_data = json.load(file)
        print(f"{Fore.YELLOW}Existing wallet found:")
        print(f"{Fore.CYAN}Wallet Address: {wallet_data['address']}")
        print(f"{Fore.CYAN}Private Key: {wallet_data['private_key']}")
        return wallet_data
    return None

def create_ethereum_wallet():
    wallet = check_existing_wallet()
    if wallet:
        print(f"{Fore.RED}A wallet already exists. No new wallet created.")
        return

    account = Account.create()
    wallet_address = account.address
    private_key = account.key.hex()

    print(f"{Fore.GREEN}Wallet Address: {Fore.CYAN}{wallet_address}")
    print(f"{Fore.GREEN}Private Key: {Fore.CYAN}{private_key}")

    save_wallet_to_file(wallet_address, private_key)

def show_balance(file_name="wallet.json"):
    if not os.path.exists(file_name):
        print(f"{Fore.RED}No wallet found. Please create a wallet first.")
        return

    with open(file_name, "r") as file:
        wallet_data = json.load(file)

    wallet_address = wallet_data['address']
    print(f"{Fore.CYAN}Fetching balance for: {wallet_address}")

    try:
        payload = {
            "method": "getBalance",
            "params": [wallet_address, "latest"],
            "id": 666
        }
        response = requests.post(PUBLIC_RPC + "/wallet", json=payload)

        if response.status_code == 200:
            balance_wei = int(response.json()["result"], 16)
            balance_eth = balance_wei / (10 ** 6)
            print(f"{Fore.GREEN}Balance: {balance_eth} S")
        else:
            print(f"{Fore.RED}Failed to fetch balance. Response: {response.text}")
    except Exception as e:
        print(f"{Fore.RED}Error fetching balance: {str(e)}")

def transfer_tokens():
    wallet = check_existing_wallet()
    if not wallet:
        print(f"{Fore.RED}No wallet found. Please create a wallet first.")
        return

    sender_address = wallet["address"]
    private_key = wallet["private_key"]

    receiver_address = input(f"{Fore.CYAN}Enter recipient address: ").strip()
    if not Web3.is_address(receiver_address):
        print(f"{Fore.RED}Invalid recipient address.")
        return

    try:
        amount = float(input(f"{Fore.CYAN}Enter amount to transfer: ").strip())
    except ValueError:
        print(f"{Fore.RED}Amount must be a valid number.")
        return

    if amount <= 0:
        print(f"{Fore.RED}Amount must be greater than zero.")
        return

    if len(str(amount).split(".")[-1]) > 6:
        print(f"{Fore.RED}Amount cannot have more than 6 decimal places.")
        return

    amount_in_wei = int(amount * 10 ** 6)

    tx_data = {
        "sender": sender_address,
        "receiver": receiver_address,
        "amount": str(amount_in_wei)
    }

    message = encode_defunct(text=json.dumps(tx_data))
    signature = Account.sign_message(message, private_key).signature.hex()

    payload = {
        "method": "transfer",
        "params": {
            "tx_data": tx_data,
            "signature": signature
        },
        "id": 777
    }

    try:
        response = requests.post(PUBLIC_RPC + "/wallet", json=payload)

        if response.status_code == 200:
            tx_hash = response.json().get("result")
            print(f"{Fore.GREEN}Transaction successful! Tx Hash: {tx_hash}")
        else:
            error_message = response.json().get("error", "Unknown error")
            print(f"{Fore.RED}Failed to process transaction. Error: {error_message}")
    except Exception as e:
        print(f"{Fore.RED}Error processing transaction: {str(e)}")

def request_airdrop():
    wallet = check_existing_wallet()
    if not wallet:
        print(f"{Fore.RED}No wallet found. Please create a wallet first.")
        return

    wallet_address = wallet["address"]

    try:
        payload = {
            "method": "requestAirdrop",
            "params": [wallet_address],
            "id": 888
        }
        print(f"{Fore.YELLOW}Requesting airdrop for wallet: {wallet_address}...")

        response = requests.post(PUBLIC_RPC + "/wallet", json=payload)
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"{Fore.GREEN}Airdrop successful! {result['result']}")
            elif "error" in result:
                print(f"{Fore.RED}Airdrop failed: {result['error']}")
        else:
            print(f"{Fore.RED}Failed to claim airdrop. HTTP Status: {response.status_code}")
            print(f"{Fore.RED}Response: {response.text}")
    except Exception as e:
        print(f"{Fore.RED}Error claiming airdrop: {str(e)}")

def main():
    while True:
        print(f"\n{Style.BRIGHT}{Fore.MAGENTA}==== S Chain ====")
        print(f"{Fore.YELLOW}1. Create Wallet")
        print(f"{Fore.YELLOW}2. Show Balance")
        print(f"{Fore.YELLOW}3. Transfer Tokens")
        print(f"{Fore.YELLOW}4. Request Airdrop")
        print(f"{Fore.YELLOW}5. Exit")

        choice = input(f"{Fore.CYAN}Select an option: ")

        if choice == "1":
            create_ethereum_wallet()
        elif choice == "2":
            show_balance()
        elif choice == "3":
            transfer_tokens()
        elif choice == "4":
            request_airdrop()
        elif choice == "5":
            print(f"{Fore.GREEN}Exiting...")
            break
        else:
            print(f"{Fore.RED}Invalid choice, try again.")

if __name__ == "__main__":
    main()
