from flask import Flask, make_response, jsonify, request
import json
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")

proxies = { 'http': None, 'https': f"https://{PROXY_USERNAME}:{PROXY_PASSWORD}@zproxy.lum-superproxy.io:22225"}

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["ENV"] = "development"

@app.route('/api/v1/health', methods=['GET'])
def health():
    response = make_response('Hello World!', 200)
    return response


@app.route('/api/v1/refreshtoken', methods=['POST'])
def refreshToken(clientId = None, clientSecret = None, refreshToken = None):
    clientId = request.args.get('clientId')
    clientSecret = request.args.get('clientSecret')
    refreshToken = request.args.get('refreshToken')
    url = "https://discord.com/api/oauth2/token"
    params = {
        "client_id": clientId,
        "client_secret": clientSecret,
        "grant_type": "refresh_token",
        "refresh_token": refreshToken,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "DiscordBot (https://discord.js.org, 0.0.0)",
    }

    response = requests.post(url, data=params, headers=headers, proxies=proxies)
    response = make_response(response.text, response.status_code)
    return response
    

@app.route('/api/v1/addmember', methods=['POST'])
def addMember(guildId = None, userId = None, botToken = None, accessToken = None, roles = None, nick = None):
    guildId = request.args.get('guildId')
    userId = request.args.get('userId')
    botToken = request.args.get('botToken')
    accessToken = request.args.get('accessToken')
    roles = request.args.get('roles')
    nick = request.args.get('nick')
    print(f"Adding {userId} to {guildId}")

    if roles is not None and nick is not None:
        payload = dict(accessToken=accessToken, roles=roles, nick=nick)
    elif roles is not None:
        payload = dict(accessToken=accessToken, roles=roles)
    elif nick is not None:
        payload = dict(accessToken=accessToken, nick=nick)
    else:
        payload = dict(accessToken=accessToken)

    url = f"https://discordapp.com/api/guilds/{guildId}/members/{userId}"
    headers = {
        "Authorization": f"Bot {botToken}",
        "Content-Type": "application/json",
        "X-RateLimit-Precision": "millisecond",
        "User-Agent": "DiscordBot (https://discord.js.org, 0.0.0)",
    }
    
    response = requests.put(url, headers=headers, data=payload, proxies=proxies)
    response = make_response(response.text, response.status_code)
    return response


@app.route('/api/v1/migrate', methods=['POST'])
def migrate(guildId = None, roles = None, botToken = None, delay = None):
    print("Migrating")
    guildId = int(request.args.get('guildId'))
    botToken = request.args.get('botToken')
    delay = int(request.args.get('delay'))
    roles = request.args.get('roles')

    data = request.get_json()
    print(data)

    for user in data:
        print(user)
        userId = user['id']
        accessToken=user['accessToken']
        if user['nick']: nick = user['nick']
        if user['roles']: roles = user['roles']
        addMember(guildId, userId, botToken, accessToken, roles, nick)
        time.sleep(delay)

    return jsonify(data)
