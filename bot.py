import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN       = os.getenv("BOT_TOKEN", "8750468651:AAFmMxup8hgE5qLVtEfoXBkXuCl-SronxTE")
WEBSITE         = "https://gemscoin.imperamonad.xyz"
ICEBOX_WEBSITE  = "https://icebox.imperamonad.xyz"
PYRATHOS_SITE   = "https://pyrathos.imperamonad.xyz"
PORTFOLIO_SITE  = "https://imperamonad.xyz"
GEMS_CONTRACT   = "0x49931887171BF46922b2b80Aa834537A80C50B70"
ICEBOX_CONTRACT = "0xacCA7801fd5162eB7b0e8d4F62616c8B2e152BC2"

BOXES = [
    ("1",  "Amethyst Vault",  "💜", "Dark Baroque · Purple Crystal",     "SMALL → JACKPOT"),
    ("2",  "Emerald Forest",  "💚", "Ancient Forest · Living Gold",       "SMALL → JACKPOT"),
    ("3",  "Glacier Chest",   "🔵", "Arctic Ice · Frozen Lightning",      "SMALL → JACKPOT"),
    ("4",  "Inferno Relic",   "🔴", "Fire & Ice · Ruby Heat",             "SMALL → JACKPOT"),
    ("5",  "Prism Dragon",    "🌈", "Rainbow Crystal · Dragon Energy",    "MEDIUM → JACKPOT"),
    ("6",  "Abyssal Trove",   "🩵", "Deep Ocean · Bioluminescence",       "SMALL → JACKPOT"),
    ("7",  "Void Skull",      "☠️", "Dark Arts · Purple Lightning",       "EMPTY → JACKPOT"),
    ("8",  "Nebula Chest",    "🌸", "Deep Space · Pink Galaxy",           "SMALL → JACKPOT"),
    ("9",  "Lava Forge",      "🌋", "Volcano · Molten Gold",              "MEDIUM → JACKPOT"),
    ("10", "CryptoVault",     "💻", "Blockchain · Circuit Neon",          "SMALL → JACKPOT"),
    ("11", "Celestial Ark",   "👼", "Heavenly · Angel Guardian",          "MEDIUM → JACKPOT"),
    ("12", "Pharaoh IceBox",  "👑", "Ancient Egypt · Solar Gold OMEGA",   "BIG → JACKPOT"),
]

PRIZE_TIERS = """
⬛ *EMPTY*   — Common · No reward
🔴 *SMALL*   — Common · Small GEMS payout
🟢 *MEDIUM*  — Uncommon · Mid GEMS payout
💎 *BIG*     — Rare · Large GEMS payout
🖼 *NFT*     — Very Rare · Rare NFT card
🔮 *JACKPOT* — Legendary · Maximum GEMS
"""

# ── MAIN MENU KEYBOARD ──
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧊 IceBox — Mint & Open",  url=ICEBOX_WEBSITE)],
        [InlineKeyboardButton("🌐 GEMS Website",           url=WEBSITE)],
        [InlineKeyboardButton("📦 View All 12 Boxes",      callback_data="boxes")],
        [InlineKeyboardButton("🪙 GEMS Token Info",        callback_data="gems")],
        [InlineKeyboardButton("🏆 Prize Tiers",            callback_data="tiers")],
        [InlineKeyboardButton("📜 Smart Contracts",        callback_data="contracts")],
        [InlineKeyboardButton("🚀 How To Mint",            callback_data="mint")],
        [InlineKeyboardButton("🔥 More Projects",          callback_data="projects")],
    ])

# ── /start ──
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧊 *GEMSROCK — Ice Box Rewards*\n\n"
        "_Forged in Gold · Crowned in Crystal · Powered On-Chain_\n\n"
        "💎 Earn GEMS on Monad Mainnet\n"
        "🎮 Mint IceBox NFTs · Open · Claim GEMS\n"
        "🌐 Website: gemscoin.imperamonad.xyz\n"
        "🔥 Built on Monad Blockchain\n\n"
        "🎲 12 unique boxes · 6 prize tiers · 100% on-chain\n\n"
        "Choose an option below 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

# ── /boxes ──
async def boxes_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    text = "📦 *The 12 IceBoxes*\n\n"
    for num, name, emoji, theme, tier in BOXES:
        text += f"{emoji} *Box {num} — {name}*\n_{theme}_\n🎯 `{tier}`\n\n"
    await msg.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧊 Mint IceBox Now", url=ICEBOX_WEBSITE)],
            [InlineKeyboardButton("🌐 Full Collection", url=WEBSITE)],
            [InlineKeyboardButton("🔙 Back to Menu",    callback_data="menu")],
        ])
    )

# ── /gems ──
async def gems_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "🪙 *GEMS Token — ERC-20*\n\n"
        f"📋 Contract:\n`{GEMS_CONTRACT}`\n\n"
        "💰 *Supply Pools:*\n"
        "├ PUBLIC SUPPLY → circulating\n"
        "├ OWNER RESERVE → team\n"
        "└ BOX REWARD POOL → prizes\n\n"
        "⚡ GEMS auto-sent to wallet on box open!\n"
        "🔗 ERC-20 · Decimals: 18\n\n"
        f"🌐 {WEBSITE}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 GEMS Website",  url=WEBSITE)],
            [InlineKeyboardButton("🔙 Back to Menu",  callback_data="menu")],
        ])
    )

# ── /tiers ──
async def tiers_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "🏆 *Prize Tiers*\n" + PRIZE_TIERS + "\n💡 100% on-chain · Provably fair",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧊 Try Your Luck", url=ICEBOX_WEBSITE)],
            [InlineKeyboardButton("🔙 Back to Menu",  callback_data="menu")],
        ])
    )

# ── /contracts ──
async def contracts_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "📜 *Smart Contracts — Monad Mainnet*\n\n"
        f"🪙 *GEMS Token ERC-20*\n`{GEMS_CONTRACT}`\n\n"
        f"📦 *IceBox NFT ERC-721*\n`{ICEBOX_CONTRACT}`\n\n"
        "🔐 Fully automated on-chain payouts\n"
        "🔗 Verified on Monad Explorer",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Website",       url=WEBSITE)],
            [InlineKeyboardButton("🔙 Back to Menu",  callback_data="menu")],
        ])
    )

# ── /mint ──
async def mint_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "🚀 *How To Mint an IceBox*\n\n"
        "*Step 1* — Go to gemscoin.imperamonad.xyz\n"
        "*Step 2* — Connect MetaMask or Rabby wallet\n"
        "*Step 3* — Switch to Monad Mainnet (Chain ID: 143)\n"
        "*Step 4* — Click Mint IceBox\n"
        "*Step 5* — Open your box anytime\n"
        "*Step 6* — GEMS auto-sent to your wallet! 💰\n\n"
        f"📦 IceBox Contract:\n`{ICEBOX_CONTRACT}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧊 Mint on Website", url=ICEBOX_WEBSITE)],
            [InlineKeyboardButton("🔙 Back to Menu",    callback_data="menu")],
        ])
    )

# ── /projects ──
async def projects_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "🔥 *More Projects by 00IMPERA*\n\n"
        "🧊 IceBox NFT Mint\n"
        "🪙 PYRATHOS Mining Token\n"
        "⚛️ Quantum Engine NFT\n"
        "🐉 Dragon Lock\n"
        "🎰 Joker 777 Slot\n"
        "📊 Monad DEX\n\n"
        "All built on Monad Mainnet 🔥",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧊 IceBox",         url=ICEBOX_WEBSITE)],
            [InlineKeyboardButton("🪙 PYRATHOS Mining", url=PYRATHOS_SITE)],
            [InlineKeyboardButton("🌐 All Projects",    url=PORTFOLIO_SITE)],
            [InlineKeyboardButton("🔙 Back to Menu",    callback_data="menu")],
        ])
    )

# ── /website ──
async def website_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *GemsRock Websites*\n\n"
        f"🧊 IceBox: {ICEBOX_WEBSITE}\n"
        f"💎 GEMS: {WEBSITE}\n"
        f"🏠 Portfolio: {PORTFOLIO_SITE}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧊 IceBox Website",  url=ICEBOX_WEBSITE)],
            [InlineKeyboardButton("💎 GEMS Website",    url=WEBSITE)],
            [InlineKeyboardButton("🏠 All Projects",    url=PORTFOLIO_SITE)],
        ])
    )

# ── /help ──
async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *GemsRock Bot Commands*\n\n"
        "/start — Main menu\n"
        "/boxes — All 12 IceBoxes\n"
        "/gems — GEMS token info\n"
        "/tiers — Prize tiers\n"
        "/contracts — Contract addresses\n"
        "/mint — How to mint\n"
        "/projects — All projects\n"
        "/website — Visit websites\n"
        "/help — This menu\n\n"
        f"🌐 {WEBSITE}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧊 Open IceBox", url=ICEBOX_WEBSITE)],
        ])
    )

# ── BUTTON HANDLER ──
async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "menu":
        await q.message.reply_text(
            "💎 *GemsRock Menu*\n\nChoose an option 👇",
            parse_mode="Markdown",
            reply_markup=main_menu_kb()
        )
    elif q.data == "boxes":     await boxes_cmd(update, ctx)
    elif q.data == "gems":      await gems_cmd(update, ctx)
    elif q.data == "tiers":     await tiers_cmd(update, ctx)
    elif q.data == "contracts": await contracts_cmd(update, ctx)
    elif q.data == "mint":      await mint_cmd(update, ctx)
    elif q.data == "projects":  await projects_cmd(update, ctx)

# ── MAIN ──
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("boxes",     boxes_cmd))
    app.add_handler(CommandHandler("gems",      gems_cmd))
    app.add_handler(CommandHandler("tiers",     tiers_cmd))
    app.add_handler(CommandHandler("contracts", contracts_cmd))
    app.add_handler(CommandHandler("mint",      mint_cmd))
    app.add_handler(CommandHandler("projects",  projects_cmd))
    app.add_handler(CommandHandler("website",   website_cmd))
    app.add_handler(CommandHandler("help",      help_cmd))
    app.add_handler(CallbackQueryHandler(button))
    logger.info("🚀 GemsRock Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
