import sys
import os
import ssl
from flask import Flask, jsonify
from flask_cors import CORS
from bitlist import bitlist
from secretvaults import SecretVaultWrapper, OperationType, KeyType

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
"""
This application relies on the nilDB cluster consisting of three nilDB nodes.
"""

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
"""
Table for converting integers to cards as they are represented internally in
FiftyTwo.
"""

async def get_deck_from_nildb():
    """
    Query the nilDB network to obtain a random sequence of bits and use rejection
    sampling to convert that sequence into a deck of cards.
    """
    try:
        collection = SecretVaultWrapper(
            org_config["nodes"],
            org_config["org_credentials"],
            "145e0ed3-5d6b-4fc9-93b2-7855a9bb6e7c", # Schema ID.
            operation=OperationType.SUM,
            encryption_key_type=KeyType.CLUSTER,
            encryption_secret_key=None
        )
        await collection.init()

        # Add the query used to create the random sequence of bits.
        # This `try-except` block will fail if the query already exists
        # (which should occur in all executions other than the first one).
        try:
            query = {
                "variables": {},
                "pipeline": [
                    {
                        "$project": {
                            "_id": 0,
                            "sequence": [
                                {
                                    "%share": {
                                        "$floor": {
                                            "$multiply": [{"$rand": {}}, 4294967311]
                                        }
                                    }
                                }
                                for i in range(100)
                            ]
                        }
                    },
                    {"$limit": 1}
                ]
            }

            result = await collection.create_query(
                query,
                "51dba4eb-b5e7-4c54-9059-867ff592d1ae",
                "test-query-0000",
                "ef596d21-c1b9-4997-acff-ea621d2a0007" # Query ID
            )
            print(result)
        except:
            pass

        # Perform the query to obtain the sequence of random 32-bit integers.
        result = await collection.query_execute_on_nodes({
            "id": "ef596d21-c1b9-4997-acff-ea621d2a0007",
            "variables": {},
        })

        # Convert the sequence of 32-bit integers into a bit vector.
        bs = bytes()
        for i in result[0]['sequence']:
            bs = bs + int(i + 2**31).to_bytes(4, 'little')
        bs = bitlist(bs)

        # Select cards via rejection sampling from portions of the bit vector.
        cards = list(int_to_card) # Copy of deck from which cards are drawn.
        deck = []
        while len(cards) > 0:
            i = None
            while i is None or i >= len(cards):
                l = len(cards).bit_length()
                (b, bs) = (bs[:l], bs[l:])
                i = int.from_bytes(b.to_bytes(), 'little')
            deck.append(cards[i])
            del cards[i]

        return deck

    except RuntimeError as error:
        print(f"Failed to use SecretVaultWrapper: {str(error)}")
        sys.exit(1)

@app.route("/")
def home():
    return "OK"

@app.route("/api/cards")
async def cards():
    deck = await get_deck_from_nildb()
    return jsonify({"cards": deck})

# kubernetes health check routes
@app.route("/api/health", methods=["GET"])
def health():
    return "", 200

@app.route("/api/ready", methods=["GET"])
def ready():
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("FLASK_RUN_PORT", 5001))
