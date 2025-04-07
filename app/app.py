import sys
import os
import ssl
import random
from flask import Flask, jsonify
from flask_cors import CORS
from secretvaults import SecretVaultWrapper, OperationType

# Avoid SSL/HTTPS issues.
ssl._create_default_https_context = ssl._create_unverified_context

org_config = {
    "org_credentials": {
        "secret_key": "0ac97ffdd83769c6c5032cb202d0957800e0ef151f015b0aaec52e2d864d4fc6",
        "org_did": "did:nil:testnet:nillion1v596szek38l22jm9et4r4j7txu3v7eff3uffue"
    },
    "nodes": [
        {
            "url": "https://nildb-nx8v.nillion.network",
            "did": "did:nil:testnet:nillion1qfrl8nje3nvwh6cryj63mz2y6gsdptvn07nx8v",
        },
        {
            "url": "https://nildb-p3mx.nillion.network",
            "did": "did:nil:testnet:nillion1uak7fgsp69kzfhdd6lfqv69fnzh3lprg2mp3mx",
        },
        {
            "url": "https://nildb-rugk.nillion.network",
            "did": "did:nil:testnet:nillion1kfremrp2mryxrynx66etjl8s7wazxc3rssrugk",
        },
    ],
}

app = Flask(__name__)
CORS(app)

ints = list(range(52))

int_to_card = [
    "2c", "2d", "2h", "2s",
    "3c", "3d", "3h", "3s",
    "4c", "4d", "4h", "4s",
    "5c", "5d", "5h", "5s",
    "6c", "6d", "6h", "6s",
    "7c", "7d", "7h", "7s",
    "8c", "8d", "8h", "8s",
    "9c", "9d", "9h", "9s",
    "Tc", "Td", "Th", "Ts",
    "Jc", "Jd", "Jh", "Js",
    "Qc", "Qd", "Qh", "Qs",
    "Kc", "Kd", "Kh", "Ks",
    "Ac", "Ad", "Ah", "As"
]

async def get_deck_from_nildb():
    try:
        collection = SecretVaultWrapper(
            org_config["nodes"],
            org_config["org_credentials"],
            "51dba4eb-b5e7-4c54-9059-867ff592d1ae", # Schema ID.
            operation=OperationType.STORE,
        )
        await collection.init()

        # Put a deck into the database.
        deck = [
            {
                "years_in_web3": {"%allot": 0},
                "responses": [
                    {
                        "rating": 1,
                        "question_number": 1 + i,
                    }
                ],
            }
            for i in range(52)
        ]
        random.shuffle(deck)
        data_written = await collection.write_to_nodes(deck)
        new_ids = list(
            {
                created_id
                for item in data_written
                if item.get("result")
                for created_id in item["result"]["data"]["created"]
            }
        )

        # Retreive the deck from the database.
        data_read = await collection.read_from_nodes()
        return [
            card["responses"][0]["question_number"] - 1 
            for card in data_read[:52]
        ]

    except RuntimeError as error:
        print(f"Failed to use SecretVaultWrapper: {str(error)}")
        sys.exit(1)

@app.route("/")
def health():
    return "OK"

@app.route("/cards")
async def cards():
    deck = await get_deck_from_nildb()
    return jsonify({"cards": [int_to_card[i] for i in deck]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("FLASK_RUN_PORT", 5001))
