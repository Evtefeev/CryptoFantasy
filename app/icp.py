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
    return response


def get_scores():
    response = agent.update_raw(
        CANISTER_ID,
        "getLeaderboard",
        encode([])
    )

    # Extract the list of records
    raw_list = response[0]['value']
    
    # Map raw keys to readable names
    result = [
        {"name": item["_1106197254"], "score": item["_2027516754"]}
        for item in raw_list
    ]
    
    return result


def who_is_caller():
    response = agent.update_raw(
        CANISTER_ID,
        "whoIsCaller",
        encode([])
    )
    return response


if __name__ == "__main__":
    res = [
        who_is_caller(),
        increase_score("nikita", 100),
        get_scores()
    ]
    for r in res:
        print(r)
