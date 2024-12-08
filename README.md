## Features
- Create a new sChain wallet
- Check wallet balance
- Transfer tokens to another address
- Request airdrops (public airdrop)

## Requirements
- Python 3.8 or higher
- `pip` (Python package manager)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/schainfun/schain.git
    cd schain
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up the environment variables:
    Create a `.env` file in the project directory and add your RPC URL:
    ```env
    RPC_URL=https://mainnet-beta.schain.fun
    ```

## Usage

Run the main script to start the application:
```bash
python main.py
