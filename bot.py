import os
import logging
import requests
import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters, ConversationHandler
)
from datetime import datetime, timezone

# ── Keep-alive server ─────────────────────────────────────────────────────────
class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"EUROSPACE Bot is running!")
    def log_message(self, format, *args):
        pass

def run_keep_alive():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAlive)
    server.serve_forever()

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN   = os.getenv("BOT_TOKEN", "8566606318:AAF8IRAwUxct4WvO2zHWSkWShoBQtg9NNrY")
WEBSITE     = "https://d41e7edc.eurocoin-website.pages.dev/"
EXPLORER    = "https://monad.socialscan.io"
RPC_URL     = "https://rpc.monad.xyz"
CHAIN_ID    = 143
TWITTER     = "https://x.com/bnbgold277983"
DISCORD     = "https://discord.com/channels/1316093079090106472"
TG_CHANNEL  = "https://t.me/eurocoin_monad_bot"
BOT_USERNAME = "eurocoin_monad_bot"

EURO_CONTRACT = "0x5548D8405F343a6075a46a45CB954bCeB8Ba4E79"

ALL_TOKENS = [
    {"symbol": "EURO",   "name": "Meta EuroCoin",  "cat": "euro",   "emoji": "💶", "contract": "0x5548D8405F343a6075a46a45CB954bCeB8Ba4E79", "pair": "0x9E32FdD909a5BdcCfb874DEE72F24169AfE4eC02"},
    {"symbol": "mBTC",   "name": "Meta Bitcoin",   "cat": "meta",   "emoji": "₿",  "contract": "0x5078A3531Dba3Dea11AB4aaF641DB6f0fE88579e", "pair": "0x47Dc73D3e1C520056AdF52349A6A282e5262D56d"},
    {"symbol": "mETH",   "name": "Meta Ethereum",  "cat": "meta",   "emoji": "🔷", "contract": "0x271028A77301bb705C293Bd1fFA79E239AB1Daec", "pair": "0xDE92BC23146222B86e638B6E88E23917eD378a6E"},
    {"symbol": "mSOL",   "name": "Meta Solana",    "cat": "meta",   "emoji": "◎",  "contract": "0xEd59c5bA2180ce57a723Dbc04FF3A81e1ba84B3C", "pair": "0xf8dbc8Cc478506fb0844C670B35b90A7AD6Ad912"},
    {"symbol": "mBNB",   "name": "Meta BNB",       "cat": "meta",   "emoji": "🟡", "contract": "0xb1326c51F73814f071bb4d3db44c86dD03DC8C76", "pair": "0xd77B55A199EA0DC81EB4c7c36d45fBda4D6477B6"},
    {"symbol": "mXRP",   "name": "Meta XRP",       "cat": "meta",   "emoji": "🔵", "contract": "0x379563529988bD76DeD9bc4a175AD59df6191B75", "pair": "0x69884c6C8Fe6F833aEEDE2A4c0949e667C7F79fB"},
    {"symbol": "mUSDC",  "name": "Meta USDC",      "cat": "stable", "emoji": "💵", "contract": "0xe0Ed08D1bC86b98434861ae0403be968bD95465E", "pair": "0x3BE5B19348d6Ccbc20e0DCF3Cab0aDF9e4643dCa"},
    {"symbol": "mUSDT",  "name": "Meta Tether",    "cat": "stable", "emoji": "💲", "contract": "0x085368cae9d4eCffe676806c3a8105433377164b", "pair": "0xAB4CFB051E73db47f75c4A2c31dFaAFd3A82A8b8"},
    {"symbol": "mMATIC", "name": "Meta Polygon",   "cat": "meta",   "emoji": "🟣", "contract": "0x43C60d3cec23b0E85678602A4F5C1156a7398daC", "pair": "0x5F5908aD27AFf28b0BDbAD8F93470e83310aE365"},
    {"symbol": "mDOGE",  "name": "Meta Dogecoin",  "cat": "meta",   "emoji": "🐕", "contract": "0x111b31d8474Aee70767337FD794a7fb0A08788A8", "pair": "0x8e71b96897c6D5EF3954b06636c24EdB4866b488"},
    {"symbol": "mLTC",   "name": "Meta Litecoin",  "cat": "meta",   "emoji": "🥈", "contract": "0x8abAe4dbf7A2e286d688fa7101bea0fAE4C0Dd75", "pair": "0xd4faf6a3B43105395C1f3db6525eA0fBF5B3aF9a"},
    {"symbol": "mTRX",   "name": "Meta TRON",      "cat": "meta",   "emoji": "🔴", "contract": "0x1A3206c56993d4906ec26Fe85194399E0dBD8EBf", "pair": "0x77A4Ad2ac41775A543353C8255cd88C7bF58e404"},
    {"symbol": "mBASE",  "name": "Meta Base",      "cat": "meta",   "emoji": "🔵", "contract": "0xeA66DaF739823505817d4DAfEdBb43Dc0C2E5372", "pair": "0x9f1b9A6D727DF983a74F11252EDa0Fa96132cc12"},
    {"symbol": "mEURO",  "name": "Meta Euro",      "cat": "euro",   "emoji": "🇪🇺", "contract": "0x4443892C796f7A519C9D099417EC8422f88F5867", "pair": "0x2f3B240444F5b8Dc6f211373ff29CCE0Ba798114"},
    {"symbol": "mMONAD", "name": "Meta Monad",     "cat": "meta",   "emoji": "⚡", "contract": "0xbF5E34B1EBE37F9a98BFcE48645dc67Dd84E5fD6", "pair": "0xc7a8f6A2452D1ec709006E36A3B89f4Df7188a9a"},
    {"symbol": "mEURC",  "name": "Meta EURC",      "cat": "euro",   "emoji": "🏅", "contract": "0x7bD9bbFc0086B033ede5736e4Aa9C16a451D0904", "pair": "0x669d78953a14a147DA6730dA255b4E7A7b15b111"},
    {"symbol": "mCRO",   "name": "Meta Cronos",    "cat": "meta",   "emoji": "🐯", "contract": "0x0127B3c3C864cfC1BB519beB935477299b961d46", "pair": "0x7D9e8050Ba0c0a6c8336A49a5Af6748AA6BD855C"},
]

PRESALE_START = datetime(2026, 4, 18, 0,  0,  0,  tzinfo=timezone.utc)
PRESALE_END   = datetime(2027, 4, 18, 23, 59, 59, tzinfo=timezone.utc)

# ── In-memory state ───────────────────────────────────────────────────────────
# price_alerts[user_id] = [{"symbol": "EURO", "target": 0.001, "direction": "above"}, ...]
price_alerts = {}
# referrals[user_id] = {"referred_by": uid, "referrals": [uid1, uid2...]}
referrals = {}
# watchlist[user_id] = ["EURO", "mBTC", ...]
watchlists = {}
# price cache
price_cache = {}
price_cache_time = {}
CACHE_TTL = 20  # seconds

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ── RPC helpers ───────────────────────────────────────────────────────────────
def rpc_call(method, params):
    try:
        r = requests.post(RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=8)
        return r.json().get("result")
    except Exception as e:
        log.warning(f"RPC error [{method}]: {e}")
        return None

def decode_uint(h):
    return int(h, 16) if h and h not in ("0x", "0x0", None) else 0

def eth_call(contract, data):
    return rpc_call("eth_call", [{"to": contract, "data": data}, "latest"])

def get_euro_supply():
    return decode_uint(eth_call(EURO_CONTRACT, "0x18160ddd")) / 1e18

def get_euro_enabled():
    return decode_uint(eth_call(EURO_CONTRACT, "0xf582d293")) != 0

def get_tokens_per_mon():
    return decode_uint(eth_call(EURO_CONTRACT, "0x19cb3e21"))

def get_pair_price(pair_addr):
    now = time.time()
    if pair_addr in price_cache and now - price_cache_time.get(pair_addr, 0) < CACHE_TTL:
        return price_cache[pair_addr]
    try:
        res = eth_call(pair_addr, "0x0902f1ac")
        if not res or res == "0x" or len(res) < 130:
            return None
        r0 = int(res[2:66], 16)
        r1 = int(res[66:130], 16)
        if r0 == 0 or r1 == 0:
            return None
        price = round(r1 / r0, 8)
        price_cache[pair_addr] = price
        price_cache_time[pair_addr] = now
        return price
    except Exception:
        return None

def get_token_by_symbol(symbol):
    return next((t for t in ALL_TOKENS if t["symbol"].lower() == symbol.lower()), None)

# ── Countdown ─────────────────────────────────────────────────────────────────
def get_countdown():
    diff = PRESALE_END - datetime.now(timezone.utc)
    if diff.total_seconds() <= 0:
        return "⏰ Presale ended"
    d, h, m, s = diff.days, diff.seconds//3600, (diff.seconds%3600)//60, diff.seconds%60
    return f"{d}d {h:02d}h {m:02d}m {s:02d}s"

def get_progress_bar():
    now = datetime.now(timezone.utc)
    total = (PRESALE_END - PRESALE_START).total_seconds()
    elapsed = (now - PRESALE_START).total_seconds()
    pct = min(100, max(0, int((elapsed / total) * 100)))
    bar = "█" * int(pct/5) + "░" * (20 - int(pct/5))
    return bar, pct

# ── Keyboards ─────────────────────────────────────────────────────────────────
def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💶 Open EUROSPACE App", web_app=WebAppInfo(url=WEBSITE))],
        [InlineKeyboardButton("⚡ Quick Trade",  callback_data="quicktrade"),
         InlineKeyboardButton("📊 Live Stats",   callback_data="stats")],
        [InlineKeyboardButton("📈 Market Prices", callback_data="market"),
         InlineKeyboardButton("⏳ Countdown",     callback_data="countdown")],
        [InlineKeyboardButton("🪙 17 Tokens",     callback_data="tokens"),
         InlineKeyboardButton("📉 DEX Pairs",     callback_data="dex")],
        [InlineKeyboardButton("🔔 Price Alerts",  callback_data="alerts"),
         InlineKeyboardButton("👁 Watchlist",     callback_data="watchlist")],
        [InlineKeyboardButton("👥 Refer & Earn",  callback_data="referral"),
         InlineKeyboardButton("🏆 Leaderboard",   callback_data="leaderboard")],
        [InlineKeyboardButton("💰 Price & Rate",  callback_data="price"),
         InlineKeyboardButton("📜 Contract",      callback_data="contract")],
        [InlineKeyboardButton("🚀 How To Buy",    callback_data="howtobuy"),
         InlineKeyboardButton("❓ Help",           callback_data="help")],
        [InlineKeyboardButton("🔍 Explorer", url=f"{EXPLORER}/address/{EURO_CONTRACT}"),
         InlineKeyboardButton("🌐 Website",   url=WEBSITE)],
        [InlineKeyboardButton("𝕏 Twitter", url=TWITTER),
         InlineKeyboardButton("💬 Discord",  url=DISCORD),
         InlineKeyboardButton("✈️ Telegram", url=TG_CHANNEL)],
    ])

def back_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💶 Buy Now", url=WEBSITE),
        InlineKeyboardButton("⬅️ Main Menu", callback_data="back"),
    ]])

def contract_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔍 Explorer", url=f"{EXPLORER}/address/{EURO_CONTRACT}"),
        InlineKeyboardButton("⬅️ Back", callback_data="back"),
    ]])

def tokens_trade_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⚡ Trade on App", web_app=WebAppInfo(url=WEBSITE)),
        InlineKeyboardButton("⬅️ Back", callback_data="back"),
    ]])

def dex_kb_full():
    rows, row = [], []
    for t in ALL_TOKENS:
        row.append(InlineKeyboardButton(
            f"{t['emoji']} {t['symbol']}",
            url=f"https://dexscreener.com/monad/{t['pair']}"
        ))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([
        InlineKeyboardButton("⚡ Trade on App", web_app=WebAppInfo(url=WEBSITE)),
        InlineKeyboardButton("⬅️ Back", callback_data="back"),
    ])
    return InlineKeyboardMarkup(rows)

def trade_tokens_kb(action="buy"):
    """Keyboard showing all 17 tokens for buy or sell selection."""
    rows, row = [], []
    for t in ALL_TOKENS:
        row.append(InlineKeyboardButton(
            f"{t['emoji']} {t['symbol']}",
            callback_data=f"{action}_{t['symbol']}"
        ))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
    return InlineKeyboardMarkup(rows)

def watchlist_add_kb():
    rows, row = [], []
    for t in ALL_TOKENS:
        row.append(InlineKeyboardButton(
            f"{t['emoji']} {t['symbol']}",
            callback_data=f"wl_add_{t['symbol']}"
        ))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="watchlist")])
    return InlineKeyboardMarkup(rows)

# ── Message builders ──────────────────────────────────────────────────────────
WELCOME = (
    "💶 *EUROSPACE — Monad Ecosystem*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🌍 The *Euro\\-pegged* DeFi ecosystem on Monad\\!\n\n"
    "🪙 *17 Tokens* — EURO \\+ 16 Meta Tokens\n"
    "📈 *17 DEX Pairs* — Live liquidity on Monad\n"
    "⚡ *Instant* buy & sell any token in the app\n"
    "🔔 *Price Alerts* — get notified on targets\n"
    "👥 *Refer & Earn* — invite friends to join\n\n"
    f"⛓ Monad Mainnet · Chain ID {CHAIN_ID}\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👇 *Choose an action below:*"
)

HOW_TO_BUY = (
    "🚀 *HOW TO BUY ON EUROSPACE*\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "*Step 1 — Connect Wallet*\n"
    "MetaMask, WalletConnect, Trust Wallet or Rabby\n\n"
    "*Step 2 — Switch to Monad*\n"
    "Chain ID: 143 — added automatically\\!\n\n"
    "*Step 3 — Choose Your Token*\n"
    "EURO or any of the 16 Meta Tokens\n"
    "\\(mBTC, mETH, mSOL, mBNB, mXRP and more\\)\n\n"
    "*Step 4 — Enter MON Amount & Buy*\n"
    "Tokens sent instantly to your wallet\\!\n\n"
    "*Step 5 — Sell Anytime*\n"
    "Tap any token → Sell → MON back to you\\!\n\n"
    "💡 *Pro Tips:*\n"
    "▸ Use /alert to set price targets\n"
    "▸ Use /watchlist to track your tokens\n"
    "▸ Use /refer to earn by inviting friends\n"
    "━━━━━━━━━━━━━━━━━━━━"
)

def stats_text():
    supply = get_euro_supply()
    enabled = get_euro_enabled()
    rate = get_tokens_per_mon()
    status = "OPEN ✅" if enabled else "CLOSED ❌"
    cd = get_countdown()
    bar, pct = get_progress_bar()
    return (
        "📊 *LIVE PRESALE STATS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🪙 EURO Supply: `{supply:,.2f}` EURO\n"
        f"💰 Rate: `{rate:,}` EURO per MON\n"
        f"🟢 Presale: {status}\n"
        f"⏳ Ends In: `{cd}`\n"
        f"📊 Progress: `{bar}` {pct}%\n"
        f"🪙 Total Tokens: 17\n"
        f"⛓ Monad \\#{CHAIN_ID}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 [Open App]({WEBSITE})"
    )

def price_text():
    rate = get_tokens_per_mon() or 1000
    return (
        "💰 *EURO COIN PRICE*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ Rate: `{rate:,}` EURO per MON\n\n"
        f"▸ 1 MON → `{rate:,}` EURO\n"
        f"▸ 10 MON → `{rate*10:,}` EURO\n"
        f"▸ 100 MON → `{rate*100:,}` EURO\n"
        f"▸ 1,000 MON → `{rate*1000:,}` EURO\n"
        f"▸ 10,000 MON → `{rate*10000:,}` EURO\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Meta Tokens have individual rates\\!\n"
        "Open the app to see live buy\\/sell prices\\."
    )

def contract_text():
    return (
        "📜 *CONTRACT INFO*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💶 EURO Token \\(ERC\\-20\\)\n"
        f"`{EURO_CONTRACT}`\n\n"
        f"🔗 Monad Mainnet · Chain ID: {CHAIN_ID}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "See /tokens for all 17 contract addresses"
    )

def market_text():
    lines = [
        "📈 *LIVE MARKET PRICES*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Token · Price \\(WMON\\)\n"
    ]
    for t in ALL_TOKENS:
        price = get_pair_price(t["pair"])
        if price:
            price_str = f"`{price:.8f}`"
        else:
            price_str = "`—`"
        lines.append(f"{t['emoji']} *{t['symbol']}* {price_str}")
    lines.append("\n━━━━━━━━━━━━━━━━━━━━")
    lines.append("🔄 Prices update every 20s · Tap DEX for charts")
    return "\n".join(lines)

def tokens_list_text():
    sections = [("euro", "🟡 EURO TOKENS"), ("stable", "🟢 STABLE TOKENS"), ("meta", "🔵 META TOKENS")]
    lines = ["🪙 *ALL 17 TOKENS*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for cat, label in sections:
        group = [t for t in ALL_TOKENS if t["cat"] == cat]
        if not group:
            continue
        lines.append(f"*{label}*")
        for t in group:
            short = f"{t['contract'][:10]}…{t['contract'][-6:]}"
            price = get_pair_price(t["pair"])
            price_str = f" · `{price:.8f}` WMON" if price else ""
            lines.append(f"{t['emoji']} `{t['symbol']}` — {t['name']}{price_str}\n  `{short}`")
        lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━\nTap ⚡ Trade in App to buy or sell\\!")
    return "\n".join(lines)

def dex_text():
    lines = ["📉 *DEX LIVE PAIRS — 17 Pairs*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for t in ALL_TOKENS:
        price = get_pair_price(t["pair"])
        price_str = f"`{price:.8f}` WMON" if price else "`— loading`"
        lines.append(f"{t['emoji']} `{t['symbol']}` {price_str}")
    lines += ["\n━━━━━━━━━━━━━━━━━━━━", "Tap any token below for DexScreener chart 👇"]
    return "\n".join(lines)

def countdown_text():
    bar, pct = get_progress_bar()
    diff = PRESALE_END - datetime.now(timezone.utc)
    if diff.total_seconds() <= 0:
        return "⏰ Presale has ended\\!"
    d, h, m, s = diff.days, diff.seconds//3600, (diff.seconds%3600)//60, diff.seconds%60
    return (
        "⏳ *PRESALE COUNTDOWN*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🗓 `{d}d {h:02d}h {m:02d}m {s:02d}s` remaining\n\n"
        f"`{bar}` {pct}%\n\n"
        "📅 Start: April 18, 2026\n"
        "📅 End:   April 18, 2027\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 [Buy EURO Now]({WEBSITE})"
    )

def quicktrade_text():
    rate = get_tokens_per_mon() or 1000
    return (
        "⚡ *QUICK TRADE*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose an action:\n\n"
        f"💰 Current Rate: `{rate:,}` EURO/MON\n\n"
        "🟢 *BUY* — Spend MON, receive tokens\n"
        "🔴 *SELL* — Return tokens, receive MON\n"
        "📊 *PRICE* — Check live token prices\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "All trades execute on\\-chain via app 👇"
    )

def token_detail_text(token):
    price = get_pair_price(token["pair"])
    rate = get_tokens_per_mon() if token["symbol"] == "EURO" else None
    lines = [
        f"{token['emoji']} *{token['name']} \\({token['symbol']}\\)*\n"
        "━━━━━━━━━━━━━━━━━━━━\n",
        f"📋 Contract:\n`{token['contract']}`\n",
    ]
    if price:
        lines.append(f"💱 DEX Price: `{price:.8f}` WMON\n")
        lines.append(f"📊 Pair: `{token['pair'][:10]}…{token['pair'][-6:]}`\n")
    if rate:
        lines.append(f"🏷️ Presale Rate: `{rate:,}` per MON\n")
    lines.append(f"\n🔗 [DexScreener Chart](https://dexscreener.com/monad/{token['pair']})")
    lines.append(f"\n🔍 [Explorer](https://monad.socialscan.io/address/{token['contract']})")
    return "\n".join(lines)

def token_detail_kb(token):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🟢 Buy {token['symbol']}", callback_data=f"buy_{token['symbol']}"),
         InlineKeyboardButton(f"🔴 Sell {token['symbol']}", callback_data=f"sell_{token['symbol']}")],
        [InlineKeyboardButton("📊 DexScreener", url=f"https://dexscreener.com/monad/{token['pair']}"),
         InlineKeyboardButton("🔔 Set Alert", callback_data=f"alert_{token['symbol']}")],
        [InlineKeyboardButton("👁 Add to Watchlist", callback_data=f"wl_add_{token['symbol']}"),
         InlineKeyboardButton("⬅️ Back", callback_data="tokens")],
    ])

def alerts_text(user_id):
    user_alerts = price_alerts.get(user_id, [])
    if not user_alerts:
        return (
            "🔔 *PRICE ALERTS*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "You have no active alerts\\.\n\n"
            "Set an alert to be notified when a token\n"
            "hits your target price\\!\n\n"
            "Use: /alert SYMBOL PRICE\n"
            "Example: `/alert EURO 0\\.001`\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
    lines = ["🔔 *YOUR PRICE ALERTS*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for i, a in enumerate(user_alerts):
        direction = "⬆️ above" if a["direction"] == "above" else "⬇️ below"
        lines.append(f"{i+1}\\. `{a['symbol']}` — {direction} `{a['target']:.8f}` WMON")
    lines.append("\n━━━━━━━━━━━━━━━━━━━━")
    lines.append("Use /alert to add · /delalert N to remove")
    return "\n".join(lines)

def watchlist_text(user_id):
    wl = watchlists.get(user_id, [])
    if not wl:
        return (
            "👁 *YOUR WATCHLIST*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your watchlist is empty\\!\n\n"
            "Add tokens to track their prices quickly\\.\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
    lines = ["👁 *YOUR WATCHLIST*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for sym in wl:
        token = get_token_by_symbol(sym)
        if token:
            price = get_pair_price(token["pair"])
            price_str = f"`{price:.8f}` WMON" if price else "`loading…`"
            lines.append(f"{token['emoji']} *{sym}* — {price_str}")
    lines.append("\n━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

def watchlist_kb(user_id):
    wl = watchlists.get(user_id, [])
    rows = []
    if wl:
        remove_row = []
        for sym in wl:
            remove_row.append(InlineKeyboardButton(f"❌ {sym}", callback_data=f"wl_rm_{sym}"))
            if len(remove_row) == 3:
                rows.append(remove_row)
                remove_row = []
        if remove_row:
            rows.append(remove_row)
    rows.append([InlineKeyboardButton("➕ Add Token", callback_data="wl_add")])
    rows.append([InlineKeyboardButton("🔄 Refresh", callback_data="watchlist"),
                 InlineKeyboardButton("⬅️ Back", callback_data="back")])
    return InlineKeyboardMarkup(rows)

def referral_text(user_id):
    ref_data = referrals.get(user_id, {"referred_by": None, "referrals": []})
    count = len(ref_data["referrals"])
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref{user_id}"
    return (
        "👥 *REFER & EARN*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📣 Invite friends to EUROSPACE\\!\n\n"
        f"🔗 *Your referral link:*\n`{ref_link}`\n\n"
        f"👤 Friends referred: *{count}*\n\n"
        "🎁 *How it works:*\n"
        "▸ Share your link with friends\n"
        "▸ They join and buy EURO tokens\n"
        "▸ You both grow the community\\!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 The more you refer, the bigger EUROSPACE grows\\!"
    )

def leaderboard_text():
    sorted_refs = sorted(referrals.items(), key=lambda x: len(x[1].get("referrals", [])), reverse=True)
    lines = ["🏆 *REFERRAL LEADERBOARD*\n━━━━━━━━━━━━━━━━━━━━\n"]
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    if not sorted_refs:
        lines.append("No referrals yet\\. Be the first\\!")
    else:
        for i, (uid, data) in enumerate(sorted_refs[:5]):
            count = len(data.get("referrals", []))
            medal = medals[i] if i < len(medals) else f"{i+1}\\."
            lines.append(f"{medal} User `{str(uid)[-4:]}…` — *{count}* referrals")
    lines.append("\n━━━━━━━━━━━━━━━━━━━━")
    lines.append("Use /refer to get your link\\!")
    return "\n".join(lines)

# ── Alert checker background task ─────────────────────────────────────────────
async def check_alerts(context):
    for user_id, alerts in list(price_alerts.items()):
        triggered = []
        remaining = []
        for alert in alerts:
            token = get_token_by_symbol(alert["symbol"])
            if not token:
                continue
            price = get_pair_price(token["pair"])
            if price is None:
                remaining.append(alert)
                continue
            hit = (alert["direction"] == "above" and price >= alert["target"]) or \
                  (alert["direction"] == "below" and price <= alert["target"])
            if hit:
                triggered.append((alert, price))
            else:
                remaining.append(alert)
        price_alerts[user_id] = remaining
        for alert, price in triggered:
            direction_str = "risen above" if alert["direction"] == "above" else "dropped below"
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"🔔 *PRICE ALERT TRIGGERED\\!*\n\n"
                        f"{get_token_by_symbol(alert['symbol'])['emoji']} *{alert['symbol']}* has {direction_str} "
                        f"`{alert['target']:.8f}` WMON\\!\n\n"
                        f"📊 Current price: `{price:.8f}` WMON\n\n"
                        f"[Trade Now]({WEBSITE})"
                    ),
                    parse_mode="MarkdownV2"
                )
            except Exception as e:
                log.warning(f"Alert notify error: {e}")

# ── Command handlers ──────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = ctx.args
    # Handle referral
    if args and args[0].startswith("ref"):
        try:
            referrer_id = int(args[0][3:])
            if referrer_id != user_id:
                if referrer_id not in referrals:
                    referrals[referrer_id] = {"referred_by": None, "referrals": []}
                if user_id not in referrals[referrer_id]["referrals"]:
                    referrals[referrer_id]["referrals"].append(user_id)
                if user_id not in referrals:
                    referrals[user_id] = {"referred_by": referrer_id, "referrals": []}
                try:
                    await ctx.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 *New Referral\\!* Someone joined EUROSPACE using your link\\! You now have *{len(referrals[referrer_id]['referrals'])}* referrals\\!",
                        parse_mode="MarkdownV2"
                    )
                except:
                    pass
        except:
            pass
    await update.message.reply_text(WELCOME, parse_mode="MarkdownV2", reply_markup=main_kb())

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *EUROSPACE Help*\n\n"
        f"🌐 {WEBSITE}\n\n"
        "*Commands:*\n"
        "/start — Main menu\n"
        "/buy — Buy tokens\n"
        "/sell — Sell tokens\n"
        "/market — Live prices all 17 tokens\n"
        "/price SYMBOL — Token price \\(e\\.g\\. /price mBTC\\)\n"
        "/alert SYMBOL TARGET — Set price alert\n"
        "/delalert N — Delete alert number N\n"
        "/watchlist — View your watchlist\n"
        "/refer — Your referral link\n"
        "/stats — Live presale stats\n"
        "/countdown — Presale timer\n"
        "/tokens — All 17 tokens\n"
        "/dex — DEX pairs\n"
        "/contract — Contract addresses\n"
        "/help — This menu",
        parse_mode="MarkdownV2",
        reply_markup=main_kb(),
        disable_web_page_preview=True,
    )

async def buy_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "🟢 *BUY TOKENS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select which token you want to buy\\.\n"
        "You will pay with *MON* \\(Monad native token\\)\\.\n\n"
        "👇 Choose a token:"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="MarkdownV2", reply_markup=trade_tokens_kb("buy"))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="MarkdownV2", reply_markup=trade_tokens_kb("buy"))

async def sell_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔴 *SELL TOKENS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select which token you want to sell\\.\n"
        "You will receive *MON* back\\.\n\n"
        "👇 Choose a token:"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="MarkdownV2", reply_markup=trade_tokens_kb("sell"))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="MarkdownV2", reply_markup=trade_tokens_kb("sell"))

async def market_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("📈 Loading live prices…")
    await msg.edit_text(market_text(), parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="market"),
         InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ]))

async def price_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    if not args:
        await update.message.reply_text(price_text(), parse_mode="MarkdownV2", reply_markup=back_kb())
        return
    symbol = args[0].upper()
    token = get_token_by_symbol(symbol)
    if not token:
        await update.message.reply_text(
            f"❌ Token `{symbol}` not found\\. Use /tokens to see all 17 tokens\\.",
            parse_mode="MarkdownV2"
        )
        return
    await update.message.reply_text(
        token_detail_text(token), parse_mode="MarkdownV2",
        reply_markup=token_detail_kb(token),
        disable_web_page_preview=True
    )

async def alert_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    user_id = update.effective_user.id
    if len(args) < 2:
        await update.message.reply_text(
            "🔔 *Set Price Alert*\n\n"
            "Usage: `/alert SYMBOL PRICE`\n"
            "Example: `/alert mBTC 0\\.005`\n\n"
            "You'll be notified when the token crosses your target\\!",
            parse_mode="MarkdownV2"
        )
        return
    symbol = args[0].upper()
    token = get_token_by_symbol(symbol)
    if not token:
        await update.message.reply_text(f"❌ Token `{symbol}` not found\\.", parse_mode="MarkdownV2")
        return
    try:
        target = float(args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid price\\. Use a number like `0\\.001`", parse_mode="MarkdownV2")
        return
    current = get_pair_price(token["pair"])
    direction = "above" if (current is None or target > current) else "below"
    if user_id not in price_alerts:
        price_alerts[user_id] = []
    price_alerts[user_id].append({"symbol": symbol, "target": target, "direction": direction})
    dir_str = "rises above" if direction == "above" else "drops below"
    await update.message.reply_text(
        f"✅ *Alert Set\\!*\n\n"
        f"{token['emoji']} `{symbol}` — notify me when price {dir_str} `{target:.8f}` WMON\n\n"
        f"Current price: `{current:.8f}` WMON" if current else
        f"✅ *Alert Set\\!*\n\n"
        f"{token['emoji']} `{symbol}` — notify when price {dir_str} `{target:.8f}` WMON",
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📋 My Alerts", callback_data="alerts"),
            InlineKeyboardButton("⬅️ Back", callback_data="back")
        ]])
    )

async def delalert_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = ctx.args
    if not args:
        await update.message.reply_text("Usage: `/delalert N` \\(where N is the alert number\\)", parse_mode="MarkdownV2")
        return
    try:
        idx = int(args[0]) - 1
        alerts = price_alerts.get(user_id, [])
        if 0 <= idx < len(alerts):
            removed = alerts.pop(idx)
            price_alerts[user_id] = alerts
            await update.message.reply_text(f"✅ Alert for `{removed['symbol']}` removed\\.", parse_mode="MarkdownV2")
        else:
            await update.message.reply_text("❌ Invalid alert number\\.", parse_mode="MarkdownV2")
    except ValueError:
        await update.message.reply_text("❌ Use a number\\. Example: `/delalert 1`", parse_mode="MarkdownV2")

async def watchlist_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message:
        await update.message.reply_text(
            watchlist_text(user_id), parse_mode="MarkdownV2",
            reply_markup=watchlist_kb(user_id)
        )

async def refer_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in referrals:
        referrals[user_id] = {"referred_by": None, "referrals": []}
    await update.message.reply_text(
        referral_text(user_id), parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
            InlineKeyboardButton("⬅️ Back", callback_data="back")
        ]])
    )

async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Fetching live stats…")
    await msg.edit_text(stats_text(), parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="stats"),
         InlineKeyboardButton("💶 Buy Now", url=WEBSITE)],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ]))

async def contract_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(contract_text(), parse_mode="MarkdownV2", reply_markup=contract_kb())

async def tokens_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(tokens_list_text(), parse_mode="MarkdownV2", reply_markup=tokens_trade_kb())

async def dex_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Loading DEX prices from chain…")
    await msg.edit_text(dex_text(), parse_mode="MarkdownV2", reply_markup=dex_kb_full())

async def countdown_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(countdown_text(), parse_mode="MarkdownV2", reply_markup=back_kb())

# ── Inline button handler ─────────────────────────────────────────────────────
async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user_id = q.from_user.id
    await q.answer()

    # ── Navigation ────────────────────────────────────────────────────────────
    if data == "back":
        await q.edit_message_text(WELCOME, parse_mode="MarkdownV2", reply_markup=main_kb())

    elif data == "stats":
        await q.edit_message_text("⏳ Fetching live stats…")
        await q.edit_message_text(stats_text(), parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="stats"),
             InlineKeyboardButton("💶 Buy Now", url=WEBSITE)],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]))

    elif data == "market":
        await q.edit_message_text("📈 Loading live prices…")
        await q.edit_message_text(market_text(), parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="market"),
             InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]))

    elif data == "countdown":
        await q.edit_message_text(countdown_text(), parse_mode="MarkdownV2", reply_markup=back_kb())

    elif data == "price":
        await q.edit_message_text(price_text(), parse_mode="MarkdownV2", reply_markup=back_kb())

    elif data == "contract":
        await q.edit_message_text(contract_text(), parse_mode="MarkdownV2", reply_markup=contract_kb())

    elif data == "tokens":
        await q.edit_message_text("⏳ Loading tokens…")
        await q.edit_message_text(tokens_list_text(), parse_mode="MarkdownV2", reply_markup=tokens_trade_kb())

    elif data == "dex":
        await q.edit_message_text("⏳ Loading DEX prices…")
        await q.edit_message_text(dex_text(), parse_mode="MarkdownV2", reply_markup=dex_kb_full())

    elif data == "howtobuy":
        await q.edit_message_text(HOW_TO_BUY, parse_mode="MarkdownV2", reply_markup=back_kb())

    elif data == "help":
        await q.edit_message_text(
            "❓ *Help*\n\n"
            f"🌐 {WEBSITE}\n\n"
            "/start /buy /sell /market /price SYMBOL\n"
            "/alert /watchlist /refer /stats /tokens\n"
            "/dex /countdown /contract /help",
            parse_mode="Markdown", reply_markup=main_kb(),
        )

    # ── Quick Trade ───────────────────────────────────────────────────────────
    elif data == "quicktrade":
        await q.edit_message_text(quicktrade_text(), parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 BUY Token",  callback_data="buymenu"),
             InlineKeyboardButton("🔴 SELL Token", callback_data="sellmenu")],
            [InlineKeyboardButton("📊 Market Prices", callback_data="market")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")],
        ]))

    elif data == "buymenu":
        await q.edit_message_text(
            "🟢 *SELECT TOKEN TO BUY*\n━━━━━━━━━━━━━━━━━━━━\nChoose a token — you pay with MON:",
            parse_mode="MarkdownV2", reply_markup=trade_tokens_kb("buy")
        )

    elif data == "sellmenu":
        await q.edit_message_text(
            "🔴 *SELECT TOKEN TO SELL*\n━━━━━━━━━━━━━━━━━━━━\nChoose a token — you receive MON:",
            parse_mode="MarkdownV2", reply_markup=trade_tokens_kb("sell")
        )

    # ── Buy / Sell token detail ───────────────────────────────────────────────
    elif data.startswith("buy_") or data.startswith("sell_"):
        action, symbol = data.split("_", 1)
        token = get_token_by_symbol(symbol)
        if not token:
            await q.answer("Token not found", show_alert=True)
            return
        price = get_pair_price(token["pair"])
        price_str = f"\n💱 Current price: `{price:.8f}` WMON" if price else ""
        action_emoji = "🟢" if action == "buy" else "🔴"
        action_text = "BUY" if action == "buy" else "SELL"
        text = (
            f"{action_emoji} *{action_text} {token['name']} \\({token['symbol']}\\)*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{price_str}\n\n"
            "To complete this trade:\n"
            "1\\. Open the EUROSPACE App below\n"
            "2\\. Connect your wallet\n"
            f"3\\. Find `{token['symbol']}` and tap {action_text}\n"
            "4\\. Enter amount and confirm tx\n\n"
            "✅ Trade executes on\\-chain instantly\\!"
        )
        await q.edit_message_text(text, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{action_emoji} Open App to {action_text}", web_app=WebAppInfo(url=WEBSITE))],
            [InlineKeyboardButton("📊 Chart", url=f"https://dexscreener.com/monad/{token['pair']}"),
             InlineKeyboardButton("🔔 Set Alert", callback_data=f"alert_{token['symbol']}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buymenu" if action == "buy" else "sellmenu")],
        ]))

    # ── Token detail from alert button ────────────────────────────────────────
    elif data.startswith("alert_"):
        symbol = data.split("_", 1)[1]
        token = get_token_by_symbol(symbol)
        if token:
            price = get_pair_price(token["pair"])
            price_str = f"`{price:.8f}` WMON" if price else "unknown"
            await q.edit_message_text(
                f"🔔 *Set Alert for {token['emoji']} {token['symbol']}*\n\n"
                f"Current price: {price_str}\n\n"
                f"Use this command:\n"
                f"`/alert {token['symbol']} <target_price>`\n\n"
                f"Example: `/alert {token['symbol']} {price*1.1:.8f}`",
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Back", callback_data=f"buy_{symbol}")
                ]])
            )

    # ── Alerts ────────────────────────────────────────────────────────────────
    elif data == "alerts":
        await q.edit_message_text(alerts_text(user_id), parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]))

    # ── Watchlist ─────────────────────────────────────────────────────────────
    elif data == "watchlist":
        await q.edit_message_text(
            watchlist_text(user_id), parse_mode="MarkdownV2",
            reply_markup=watchlist_kb(user_id)
        )

    elif data == "wl_add":
        await q.edit_message_text(
            "👁 *ADD TO WATCHLIST*\n\nChoose a token to track:",
            parse_mode="MarkdownV2", reply_markup=watchlist_add_kb()
        )

    elif data.startswith("wl_add_"):
        symbol = data.split("_", 2)[2]
        if user_id not in watchlists:
            watchlists[user_id] = []
        if symbol not in watchlists[user_id]:
            watchlists[user_id].append(symbol)
            await q.answer(f"✅ {symbol} added to watchlist!")
        else:
            await q.answer(f"{symbol} is already in your watchlist!")
        await q.edit_message_text(
            watchlist_text(user_id), parse_mode="MarkdownV2",
            reply_markup=watchlist_kb(user_id)
        )

    elif data.startswith("wl_rm_"):
        symbol = data.split("_", 2)[2]
        if user_id in watchlists and symbol in watchlists[user_id]:
            watchlists[user_id].remove(symbol)
            await q.answer(f"❌ {symbol} removed from watchlist!")
        await q.edit_message_text(
            watchlist_text(user_id), parse_mode="MarkdownV2",
            reply_markup=watchlist_kb(user_id)
        )

    # ── Referral ──────────────────────────────────────────────────────────────
    elif data == "referral":
        if user_id not in referrals:
            referrals[user_id] = {"referred_by": None, "referrals": []}
        await q.edit_message_text(
            referral_text(user_id), parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
                 InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ])
        )

    elif data == "leaderboard":
        await q.edit_message_text(
            leaderboard_text(), parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👥 My Referrals", callback_data="referral"),
                 InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ])
        )

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    t = threading.Thread(target=run_keep_alive, daemon=True)
    t.start()
    log.info("Keep-alive server started on port %s", os.environ.get("PORT", 8080))

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("help",       help_cmd))
    app.add_handler(CommandHandler("buy",        buy_cmd))
    app.add_handler(CommandHandler("sell",       sell_cmd))
    app.add_handler(CommandHandler("market",     market_cmd))
    app.add_handler(CommandHandler("price",      price_cmd))
    app.add_handler(CommandHandler("alert",      alert_cmd))
    app.add_handler(CommandHandler("delalert",   delalert_cmd))
    app.add_handler(CommandHandler("watchlist",  watchlist_cmd))
    app.add_handler(CommandHandler("refer",      refer_cmd))
    app.add_handler(CommandHandler("stats",      stats_cmd))
    app.add_handler(CommandHandler("contract",   contract_cmd))
    app.add_handler(CommandHandler("tokens",     tokens_cmd))
    app.add_handler(CommandHandler("dex",        dex_cmd))
    app.add_handler(CommandHandler("countdown",  countdown_cmd))
    app.add_handler(CallbackQueryHandler(button))

    # Price alert checker every 30 seconds
    app.job_queue.run_repeating(check_alerts, interval=30, first=30)

    log.info("EUROSPACE Bot started — %s", WEBSITE)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
