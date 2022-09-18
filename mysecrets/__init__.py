import json
import os

SECRETS_PATH = os.path.dirname(__file__)

BINANCE_SECRETS_PATH = os.path.join(SECRETS_PATH, 'binance_secrets.json')

if not os.path.exists(BINANCE_SECRETS_PATH):
    with open(BINANCE_SECRETS_PATH, "w") as outfile:
        outfile.write(
            json.dumps(
                {
                    'api_key': 'ENTER API KEY HERE!',
                    'api_secret': 'ENTER API SECRET HERE!'
                },
                indent=4
            )
        )
