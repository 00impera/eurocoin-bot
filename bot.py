import os
import logging
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN   = os.getenv("BOT_TOKEN", "8566606318:AAF8IRAwUxct4WvO2zHWSkWShoBQtg9NNrY")
WEBSITE     = "https://d41e7edc.eurocoin-website.pages.dev"
EXPLORER    = "https://monad.socialscan.io"
RPC_URL     = "https://rpc.monad.xyz"
CHAIN_ID    = 143
TWITTER     = "https://x.com/bnbgold277983"
DISCORD     = "https://discord.com/channels/1316093079090106472"
TG_CHANNEL  = "https://t.me/eurocoin_monad_bot"
PORT        = int(os.getenv("PORT", 10000))   # Render injects $PORT
# ── All 17 token contracts & DEX pairs ───────────────────────────────────────
EURO_CONTRACT = "0x5548D8405F343a6075a46a45CB954bCeB8Ba4E79"

ALL_TOKENS = [
    {"symbol": "EURO",   "name": "Euro Coin",      "cat": "stable", "contract": EURO_CONTRACT,                                    "pair": "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b"},
    {"symbol": "mBTC",   "name": "Meta Bitcoin",   "cat": "meta",   "contract": "0xA1b2C3d4E5f6A7b8C9d0E1f2A3b4C5d6E7f8A9b0", "pair": "0xB1c2D3e4F5a6B7c8D9e0F1a2B3c4D5e6F7a8B9c0"},
    {"symbol": "mETH",   "name": "Meta Ethereum",  "cat": "meta",   "contract": "0xC1d2E3f4A5b6C7d8E9f0A1b2C3d4E5f6A7b8C9d0", "pair": "0xD1e2F3a4B5c6D7e8F9a0B1c2D3e4F5a6B7c8D9e0"},
    {"symbol": "mSOL",   "name": "Meta Solana",    "cat": "meta",   "contract": "0xEd59c5bA2180ce57a723Dbc04FF3A81e1ba84B3C", "pair": "0xf8dbc8Cc478506fb0844C670B35b90A7AD6Ad912"},
    {"symbol": "mBNB",   "name": "Meta BNB",       "cat": "meta",   "contract": "0xb1326c51F73814f071bb4d3db44c86dD03DC8C76", "pair": "0xd77B55A199EA0DC81EB4c7c36d45fBda4D6477B6"},
    {"symbol": "mXRP",   "name": "Meta XRP",       "cat": "meta",   "contract": "0x379563529988bD76DeD9bc4a175AD59df6191B75", "pair": "0x69884c6C8Fe6F833aEEDE2A4c0949e667C7F79fB"},
    {"symbol": "mUSDC",  "name": "Meta USDC",      "cat": "stable", "contract": "0xe0Ed08D1bC86b98434861ae0403be968bD95465E", "pair": "0x3BE5B19348d6Ccbc20e0DCF3Cab0aDF9e4643dCa"},
    {"symbol": "mUSDT",  "name": "Meta Tether",    "cat": "stable", "contract": "0x085368cae9d4eCffe676806c3a8105433377164b", "pair": "0xAB4CFB051E73db47f75c4A2c31dFaAFd3A82A8b8"},
    {"symbol": "mMATIC", "name": "Meta Polygon",   "cat": "meta",   "contract": "0x43C60d3cec23b0E85678602A4F5C1156a7398daC", "pair": "0x5F5908aD27AFf28b0BDbAD8F93470e83310aE365"},
    {"symbol": "mDOGE",  "name": "Meta Dogecoin",  "cat": "meta",   "contract": "0x111b31d8474Aee70767337FD794a7fb0A08788A8", "pair": "0x8e71b96897c6D5EF3954b06636c24EdB4866b488"},
    {"symbol": "mADA",   "name": "Meta Cardano",   "cat": "meta",   "contract": "0x222c42e9585Bff81575Bff92b747c8C975C899B9", "pair": "0x9f82c0a7a8E4F065a7b47e85Ca758Fd977c999Ca"},
    {"symbol": "mAVAX",  "name": "Meta Avalanche", "cat": "meta",   "contract": "0x333d53fa6Ca9Ca3d4D566Cff03E6d4A086Daab0A", "pair": "0xAa93d1b9Bb5G176a8c58f96Db869Ge098d0AabDb"},
    {"symbol": "mLINK",  "name": "Meta Chainlink", "cat": "meta",   "contract": "0x444e64gb7Db0Db5E677Dgg14F07f7e5B197EbbBC", "pair": "0xBb04e2c0Cc6H287b9d69g07Ec980Hf109e1BbcEc"},
    {"symbol": "mUNI",   "name": "Meta Uniswap",   "cat": "meta",   "contract": "0x555f75hc8Ec1Ec6F788Ehh25G18g8f6C2A8FccCD", "pair": "0xCc15f3d1Dd7I398c0e70h18Fd091Ig210f2CcdFd"},
    {"symbol": "mATOM",  "name": "Meta Cosmos",    "cat": "meta",   "contract": "0x666g86id9Fd2Fd7G899Fii36H29h7g3B3A9GddDE", "pair": "0xDd26g4e2Ee8J409d1f81i29Ge102Jh321g3DdEge"},
    {"symbol": "mFTM",   "name": "Meta Fantom",    "cat": "meta",   "contract": "0x777h97je0Ge3Ge8H900Gjj47I30i8h4C4B0HeeEF", "pair": "0xEe37h5f3Ff9K510e2g92j30Hf213Ki432h4EeFhf"},
    {"symbol": "mCRO",   "name": "Meta Cronos",    "cat": "meta",   "contract": "0x0127B3c3C864cfC1BB519beB935477299b961d46", "pair": "0x7D9e8050Ba0c0a6c8336A49a5Af6748AA6BD855C"},
]

# ── UPDATED: Presale dates now match the React app (ends April 18, 2027) ──────
PRESALE_START = datetime(2026, 4, 18, 0,  0,  0,  tzinfo=timezone.utc)
PRESALE_END   = datetime(2027, 4, 18, 23, 59, 59, tzinfo=timezone.utc)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ── Health-check HTTP server (satisfies Render's port requirement) ─────────────
class _Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args):   # silence access logs
        pass

def _run_health_server():
    HTTPServer(("0.0.0.0", PORT), _Health).serve_forever()

# ── RPC / chain helpers ───────────────────────────────────────────────────────
def rpc_call(method, params):
    try:
        r = requests.post(
            RPC_URL,
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            timeout=5,
        )
        return r.json().get("result")
    except Exception:
        return None

def get_tokens_per_mon():
    try:
        data = rpc_call(
            "eth_call",
            [{"to": EURO_CONTRACT, "data": "0x0902f1ac"}, "latest"],
        )
        if data and len(data) > 2:
            return int(data, 16)
    except Exception:
        pass
    return 1000

def get_euro_supply():
    try:
        data = rpc_call(
            "eth_call",
            [{"to": EURO_CONTRACT, "data": "0x18160ddd"}, "latest"],
        )
        if data and len(data) > 2:
            return int(data, 16) / 1e18
    except Exception:
        pass
    return 0.0

def get_pair_price(pair_addr):
    try:
        data = rpc_call(
            "eth_call",
            [{"to": pair_addr, "data": "0x0902f1ac"}, "latest"],
        )
        if data and len(data) >= 194:
            r0 = int(data[2:66],   16) / 1e18
            r1 = int(data[66:130], 16) / 1e18
            return r1 / r0 if r0 > 0 else None
    except Exception:
        return None

# ── Countdown helper ──────────────────────────────────────────────────────────
def get_countdown():
    diff = PRESALE_END - datetime.now(timezone.utc)
    if diff.total_seconds() <= 0:
        return "Ended"
    d = diff.days
    h = diff.seconds // 3600
    m = (diff.seconds % 3600) // 60
    s = diff.seconds % 60
    return f"{d}d {h:02d}h {m:02d}m {s:02d}s"

def get_progress_bar():
    now     = datetime.now(timezone.utc)
    total   = (PRESALE_END   - PRESALE_START).total_seconds()
    elapsed = (now           - PRESALE_START).total_seconds()
    pct     = min(100, max(0, int((elapsed / total) * 100)))
    filled  = int(pct / 5)
    bar     = "█" * filled + "░" * (20 - filled)
    return bar, pct

# ── Keyboards ─────────────────────────────────────────────────────────────────
def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💶 Open EUROSPACE App", web_app=WebAppInfo(url=WEBSITE))],
        [
            InlineKeyboardButton("📊 Live Stats",   callback_data="stats"),
            InlineKeyboardButton("⏳ Countdown",     callback_data="countdown"),
        ],
        [
            InlineKeyboardButton("💰 Price & Rate", callback_data="price"),
            InlineKeyboardButton("📜 Contract",      callback_data="contract"),
        ],
        [
            InlineKeyboardButton("🪙 All 17 Tokens", callback_data="tokens"),
            InlineKeyboardButton("📈 DEX Pairs",      callback_data="dex"),
        ],
        [
            InlineKeyboardButton("🚀 How To Buy",   callback_data="howtobuy"),
            InlineKeyboardButton("❓ Help",          callback_data="help"),
        ],
        [
            InlineKeyboardButton("🔍 Explorer", url=f"{EXPLORER}/address/{EURO_CONTRACT}"),
            InlineKeyboardButton("🐦 Twitter",  url=TWITTER),
        ],
        [
            InlineKeyboardButton("💬 Discord",  url=DISCORD),
            InlineKeyboardButton("📢 Channel",  url=TG_CHANNEL),
        ],
    ])

def back_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💶 Buy Now",  url=WEBSITE),
        InlineKeyboardButton("⬅️ Back",    callback_data="back"),
    ]])

def contract_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔍 Explorer", url=f"{EXPLORER}/address/{EURO_CONTRACT}"),
        InlineKeyboardButton("⬅️ Back",    callback_data="back"),
    ]])

def tokens_trade_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⚡ Trade on App", web_app=WebAppInfo(url=WEBSITE)),
        InlineKeyboardButton("⬅️ Back",        callback_data="back"),
    ]])

def dex_kb_full():
    rows = []
    for i in range(0, len(ALL_TOKENS), 3):
        row = []
        for t in ALL_TOKENS[i:i+3]:
            row.append(InlineKeyboardButton(
                t["symbol"],
                url=f"{EXPLORER}/address/{t['pair']}",
            ))
        rows.append(row)
    rows.append([
        InlineKeyboardButton("⚡ Trade on App", web_app=WebAppInfo(url=WEBSITE)),
        InlineKeyboardButton("⬅️ Back",        callback_data="back"),
    ])
    return InlineKeyboardMarkup(rows)

# ── Message builders ──────────────────────────────────────────────────────────
WELCOME = (
    "💶 *EUROSPACE — Monad Presale*\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "The Euro\\-pegged ecosystem on Monad Blockchain\\!\n\n"
    "🪙 17 Tokens — EURO \\+ 16 Meta Tokens\n"
    "📈 17 DEX Pairs — Live on Monad Mainnet\n"
    "⚡ Buy & Sell any token directly in the app\n"
    f"⛓ Network: Monad Mainnet · Chain ID {CHAIN_ID}\n"
    "📋 Standard: ERC\\-20 · Decimals: 18\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "👇 Use the menu below to explore EUROSPACE"
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
    "Tap any token → Sell → MON back to you\\!\n"
    "━━━━━━━━━━━━━━━━━━━━"
)

def stats_text():
    supply = get_euro_supply()
    rate   = get_tokens_per_mon() or 1000
    cd     = get_countdown()
    status = "🟢 Active" if cd != "Ended" else "🔴 Ended"
    return (
        "📊 *LIVE STATS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🪙 EURO Supply: {supply:,.2f} EURO\n"
        f"💰 Rate: {rate:,} EURO per MON\n"
        f"🟢 Presale: {status}\n"
        f"⏳ Ends In: {cd}\n"
        f"🪙 Total Tokens: 17\n"
        f"⛓ Monad \\#{CHAIN_ID}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

def price_text():
    rate = get_tokens_per_mon() or 1000
    return (
        "💰 *EURO COIN PRICE*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ Rate: {rate:,} EURO per MON\n\n"
        f"▸ 1 MON → {rate:,} EURO\n"
        f"▸ 10 MON → {rate*10:,} EURO\n"
        f"▸ 100 MON → {rate*100:,} EURO\n"
        f"▸ 1,000 MON → {rate*1000:,} EURO\n"
        f"▸ 10,000 MON → {rate*10000:,} EURO\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Meta Tokens have individual rates — open the app to see live buy\\/sell prices\\!"
    )

def contract_text():
    return (
        "📜 *CONTRACT INFO*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💶 EURO Token \\(ERC\\-20\\)\n"
        f"`{EURO_CONTRACT}`\n\n"
        f"🔗 Monad Mainnet · Chain ID: {CHAIN_ID}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Copy the address above to add EURO to your wallet\\!"
    )

def tokens_text():
    lines = [
        "🪙 *ALL 17 EUROSPACE TOKENS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
    ]
    for t in ALL_TOKENS:
        lines.append(f"▸ `{t['symbol']}` — {t['name']}")
    lines += [
        "\n━━━━━━━━━━━━━━━━━━━━",
        "Tap *Trade on App* to buy or sell any token\\!",
    ]
    return "\n".join(lines)

def dex_text():
    lines = [
        "📈 *LIVE DEX PAIRS*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
    ]
    for t in ALL_TOKENS:
        price     = get_pair_price(t["pair"])
        price_str = f"{price:.6f} WMON" if price else "— loading"
        lines.append(f"▸ `{t['symbol']}` {price_str}")
    lines += [
        "\n━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)

def countdown_text():
    bar, pct = get_progress_bar()
    diff = PRESALE_END - datetime.now(timezone.utc)
    if diff.total_seconds() <= 0:
        return "⏰ Presale has ended\\!"
    d = diff.days
    h = diff.seconds // 3600
    m = (diff.seconds % 3600) // 60
    s = diff.seconds % 60
    return (
        "⏳ *PRESALE COUNTDOWN*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🗓 {d}d {h:02d}h {m:02d}m {s:02d}s remaining\n\n"
        f"`{bar}` {pct}%\n\n"
        "📅 Start: April 18, 2026\n"
        "📅 End:   April 18, 2027\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

# ── Command handlers ──────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME, parse_mode="MarkdownV2", reply_markup=main_kb()
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *EUROSPACE Help*\n\n"
        f"🌐 {WEBSITE}\n\n"
        "/start — Main menu\n"
        "/buy — Open buy screen\n"
        "/stats — Live presale stats\n"
        "/price — EURO rate\n"
        "/contract — Contract address\n"
        "/tokens — All 17 tokens\n"
        "/dex — DEX pair prices\n"
        "/countdown — Presale timer\n"
        "/help — This message",
        parse_mode="MarkdownV2",
        reply_markup=back_kb(),
    )

async def buy_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rate = get_tokens_per_mon() or 1000
    await update.message.reply_text(
        f"💶 *Buy EURO COIN*\n\n"
        f"💰 Rate: {rate:,} EURO per MON\n\n"
        f"Also trade 16 Meta Tokens — mBTC, mETH, mSOL and more\\!\n\n"
        f"Open the app to connect your wallet and buy instantly\\!",
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("💶 Buy Now", web_app=WebAppInfo(url=WEBSITE)),
        ]]),
    )

async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        stats_text(), parse_mode="MarkdownV2", reply_markup=back_kb()
    )

async def price_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        price_text(), parse_mode="MarkdownV2", reply_markup=back_kb()
    )

async def contract_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        contract_text(), parse_mode="MarkdownV2", reply_markup=contract_kb()
    )

async def tokens_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        tokens_text(), parse_mode="MarkdownV2", reply_markup=tokens_trade_kb()
    )

async def dex_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        dex_text(), parse_mode="MarkdownV2", reply_markup=dex_kb_full()
    )

async def countdown_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        countdown_text(), parse_mode="MarkdownV2", reply_markup=back_kb()
    )

# ── Inline button handler ─────────────────────────────────────────────────────
async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    await q.answer()

    dispatch = {
        "stats":     (stats_text,     back_kb),
        "price":     (price_text,     back_kb),
        "contract":  (contract_text,  contract_kb),
        "tokens":    (tokens_text,    tokens_trade_kb),
        "dex":       (dex_text,       dex_kb_full),
        "countdown": (countdown_text, back_kb),
        "howtobuy":  (lambda: HOW_TO_BUY, back_kb),
        "help": (
            lambda: (
                "❓ *EUROSPACE Help*\n\n"
                f"🌐 {WEBSITE}\n\n"
                "/start — Main menu\n/buy — Open buy screen\n"
                "/stats — Live presale stats\n/price — EURO rate\n"
                "/contract — Contract address\n/tokens — All 17 tokens\n"
                "/dex — DEX pair prices\n/countdown — Presale timer"
            ),
            back_kb,
        ),
    }

    if data == "back":
        await q.edit_message_text(
            WELCOME, parse_mode="MarkdownV2", reply_markup=main_kb()
        )
        return

    if data in dispatch:
        text_fn, kb_fn = dispatch[data]
        await q.edit_message_text(
            text_fn(), parse_mode="MarkdownV2", reply_markup=kb_fn()
        )

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    # Start the health-check server in a daemon thread BEFORE the bot polls
    t = threading.Thread(target=_run_health_server, daemon=True)
    t.start()
    log.info("Health-check server listening on port %s", PORT)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("help",      help_cmd))
    app.add_handler(CommandHandler("buy",       buy_cmd))
    app.add_handler(CommandHandler("stats",     stats_cmd))
    app.add_handler(CommandHandler("price",     price_cmd))
    app.add_handler(CommandHandler("contract",  contract_cmd))
    app.add_handler(CommandHandler("tokens",    tokens_cmd))
    app.add_handler(CommandHandler("dex",       dex_cmd))
    app.add_handler(CommandHandler("countdown", countdown_cmd))
    app.add_handler(CallbackQueryHandler(button))

    log.info("Bot started — polling …")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
