import os
from ic.client import Client
from ic.agent import Agent
from ic.candid import Types, encode
import dotenv
from ic.identity import Identity

# Load .env
dotenv.load_dotenv()

pem_str = os.environ.get("BACKEND_IDENTITY_PEM")

# Create IC identity
identity = Identity(privkey=pem_str, type="secp256k1")
CANISTER_ID = os.environ.get("CANISTER_ID")
ICP_CLIENT_URL = os.environ.get("ICP_CLIENT_URL")

client = Client(url=ICP_CLIENT_URL)
agent = Agent(identity, client)


def increase_score(user_id: str, amount: int):
    params = [
        {'type': Types.Text, 'value': user_id},
        {'type': Types.Nat64, 'value': amount}
    ]
    response = agent.update_raw(
        CANISTER_ID,
        "increaseScore",
        encode(params)
    )
    print(response)


def who_is_caller():

    response = agent.update_raw(
        CANISTER_ID,
        "whoIsCaller",
        encode([])
    )
    print(response)

if __name__ == "__main__":
    who_is_caller()
    increase_score("nikita", 100)
