import argparse
import asyncio
from src.entities.user import User

parser = argparse.ArgumentParser(description='Create a user and return the Api-Key.')
parser.add_argument('name', type=str, help='The username of the created user.')

args = parser.parse_args()

async def save_user():
    await user.save()

user = User.new(name=args.name)
asyncio.run(save_user())

print(user.key)