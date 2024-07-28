import discord
import requests
import os
from discord.ext import tasks
from infos import *

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

def receive_server_old_status():
    os.makedirs('server_status', exist_ok=True)
    try:
        with open(f"server_status/server_old.txt", "r") as f:
            return f.readline().strip()
    except FileNotFoundError:
        return "Offline"

old_status = receive_server_old_status()

def get_server_status(server_address):
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        status = 'Online' if data.get('online') and data.get('max_players', 0) > 0 else 'Offline' #Max players é usado devido a servidores como os do Aternos, que ficam sempre online mas com uma capacidade máxima de 0 jogadores
        return f"O Server {server_address} está {status}!"
    else:
        return f"Falha ao tentar receber o status do servidor {server_address}. HTTP Status code: {response.status_code}"

def verify_status(old_status, new_status):
    if old_status == new_status:
        return 0
    elif old_status != new_status:
        return 1
    else:
        return 2

@client.event
async def on_ready():
    await tree.sync()
    print('Ready? Go!')
    channel = client.get_channel(channelid)
    if channel:
        check_server_status.start(channel)

@tree.command(name="verify", description="Verifique fora da schedule se o servidor está online")
async def verify_command(interaction: discord.Interaction):
    await interaction.response.send_message(get_server_status(server_address))

@tasks.loop(minutes=10)
async def check_server_status(channel):
    global old_status
    new_status = get_server_status(server_address)
    verification = verify_status(old_status, new_status)
    if verification == 1:
        with open(f"server_status/server_old.txt", "w") as f:
            f.write(new_status)
        await channel.send(new_status)
        old_status = new_status
    elif verification == 0:
        pass
    elif verification == 2:
        print("Deu alguma coisa errada no verify")
        await channel.send("Ops, algo parece errado...")
    else:
        print("Deu alguma coisa seriamente errada no verify e na zorra toda")
        await channel.send("Ops, algo parece muito errado...")

client.run(Token)
