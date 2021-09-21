from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")


def get_dir() -> str:
    bundle_dir = os.path.abspath(os.path.dirname(__file__))
    dir_path = os.path.join(bundle_dir, 'dest.txt')
    with open(dir_path) as f:
        return f.readline().strip()


@bot.event
async def on_ready():
    print(f"imageBot is ready! Current dir: {get_dir()}")


async def download(ctx, args):
    if get_dir() == "" or not len(args) == 3:
        await ctx.send("Not valid. Should be *!img dd [numMessages] [downloadName]* "
                       "and path should be set.")
        return
    limit = int(args[1])
    name = str(args[2])
    file_counter = 1
    # https://discordpy.readthedocs.io/en/stable/api.html#discord.Attachment
    messages = await ctx.channel.history(limit=limit + 1).flatten()
    for msg in messages[1:]:
        attachments = msg.attachments
        if not len(attachments) == 0:
            await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            for i, attachment in enumerate(attachments):
                filepath = f"{get_dir()}\\{name}{file_counter}.{attachment.content_type.split('/')[1]}"
                file_counter += 1
                await attachments[i].save(filepath)
                await ctx.send(f"Saved file to *{filepath}*")
        else:
            await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")


async def error_(ctx, args):
    await ctx.send(f"**{args[0]}** is not a valid command!\nFor more help use the command *!img help*")


async def set_path(ctx, args):
    path = args[1]
    bundle_dir = os.path.abspath(os.path.dirname(__file__))
    dir_path = os.path.join(bundle_dir, 'dest.txt')
    with open(dir_path, 'w') as f:
        f.write(path)
        await ctx.send(f"Set path to {path}")


async def show_path(ctx, args):
    dir_ = get_dir()
    if dir_ == "":
        await ctx.send(f"No download directory set.")
    else:
        await ctx.send(f"Current download directory:\n*{dir_}*")


async def help_(ctx, args):
    output = """
Commands:
    *setpath [absolutePath]*
        Sets the target download directory (or folder, whichever you call it). Must be an absolute path and MAKE SURE THE FOLDER EXISTS!!!.
    *showpath*
        Shows the path of the current target download directory.
    *dd [numMessages] [fileName]*
        Checks the last [x] amount of messages (not including the command) and downloads any attachments to the target folder.
    
Example:
    Download the attachments from the last 3 messages:
        *!img dd 3 mathhw*
    Set the path to a folder on your desktop:
        *!img setpath C://Users//[username]//Desktop//[dirName]*
    """
    await ctx.send(output)


@bot.command(name="img")
async def main(ctx, *args):
    cmd = args[0]
    func = {'dd': download,
            'setpath': set_path,
            'showpath': show_path,
            'help': help_, }.get(cmd, error_)
    await func(ctx, args)


bot.run(TOKEN)
