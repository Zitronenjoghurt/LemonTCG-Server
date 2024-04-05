import argparse
import asyncio
from src.entities.api_key import ApiKey

parser = argparse.ArgumentParser(description='Create an API-Key')
parser.add_argument('username', type=str, help='The username that is associated with this api key.')

args = parser.parse_args()

async def save_key():
    await api_key.save()

api_key = ApiKey.new(username=args.username)
asyncio.run(save_key())

print(api_key.key)