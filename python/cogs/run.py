"""This is a cog for a discord.py bot.
It will add the run command for everyone to use

Commands:
    run            Run code using the Piston API

"""

import typing
from discord.ext import commands
from discord import Embed


class Run(commands.Cog, name='Run'):
    def __init__(self, client):
        self.client = client
        self.languages = {
            'asm': 'nasm',
            'awk': 'awk',
            'bash': 'bash',
            'bf': 'brainfuck',
            'brainfuck': 'brainfuck',
            'c': 'c',
            'c#': 'csharp',
            'c++': 'cpp',
            'cpp': 'cpp',
            'cs': 'csharp',
            'csharp': 'csharp',
            'duby': 'ruby',
            'go': 'go',
            'java': 'java',
            'javascript': 'javascript',
            'jl': 'julia',
            'julia': 'julia',
            'js': 'javascript',
            'nasm': 'nasm',
            'node': 'javascript',
            'php': 'php',
            'php3': 'php',
            'php4': 'php',
            'php5': 'php',
            'py': 'python3',
            'py3': 'python3',
            'python': 'python3',
            'python2': 'python2',
            'python3': 'python3',
            'r': 'r',
            'rb': 'ruby',
            'ruby': 'ruby',
            'rs': 'rust',
            'rust': 'rust',
            'sage': 'python3',
            'swift': 'swift',
            'ts': 'typescript',
            'typescript': 'typescript',
        }
        self.last_message = dict()

    async def get_api_response(self, ctx, language):
        language = language.replace('```', '')
        if language not in self.languages:
            return f'`Unsupported language: {language}`'
        language = self.languages[language]
        message = ctx.message.content.split('```')
        if len(message) < 3:
            return '`No code or invalid code present`'
        source = message[1]
        source = source[source.find('\n'):].strip()

        url = 'https://emkc.org/api/internal/piston/execute'
        headers = {'Authorization': self.client.config["emkc_key"]}
        data = {'language': language, 'source': source}

        async with self.client.session.post(
            url,
            headers=headers,
            data=data
        ) as response:
            r = await response.json()
        if not r or 'status' not in r:
            return '`Sorry, invalid response from Piston server`'
        if r['status'] not in 'ok' or r['payload']['output'] is None:
            return '`Sorry, execution problem`'
        return (
            f'Here is your output {ctx.author.mention}\n'
            + '```\n'
            + '\n'.join(r['payload']['output'].split('\n')[:30])
            + '```'
        )

    @commands.command(hidden=True)
    async def runhelp(self, ctx):
        """How to properly run code with Felix"""
        languages = []
        last = ''
        for language in sorted(set(self.languages.values())):
            current = language[0].lower()
            if current not in last:
                languages.append([language])
            else:
                languages[-1].append(language)
            last = current
        languages = map('/'.join, languages)

        run_instructions = (
            '**Here are my supported languages:**\n'
            + '\n'.join(languages) +
            '\n\n**You can run code like this:**\n'
            'felix run python\n'
            '\\`\\`\\`python\nyour code\n\\`\\`\\`\n'
        )

        e = Embed(title='I can run code',
                  description=run_instructions,
                  color=0x2ECC71)
        await ctx.send(embed=e)

    @commands.command()
    async def run(self, ctx, language: typing.Optional[str] = None):
        """Run some code
        Type "felix run" for instructions"""
        await ctx.trigger_typing()
        if not language:
            await self.client.get_command('runhelp').invoke(ctx)
            return
        api_response = await self.get_api_response(ctx, language)
        msg = await ctx.send(api_response)
        self.last_message[ctx.author.id] = msg


    @commands.command(hidden=True)
    async def run_after_edit(self, ctx, language: typing.Optional[str] = None):
        """Run some edited code"""
        if not language:
            await self.client.get_command('runhelp').invoke(ctx)
            return
        api_response = await self.get_api_response(ctx, language)
        try:
            msg_to_edit = self.last_message[ctx.author.id]
            await msg_to_edit.edit(content=api_response)
        except KeyError:
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        content = after.content.lower()
        if not content.split()[1] == 'run':
            return
        prefixes = await self.client.get_prefix(after)
        if isinstance(prefixes, str):
            prefixes = [prefixes,]
        if any(content.startswith(f'{prefix}run') for prefix in prefixes):
            ctx = await self.client.get_context(after)
            if ctx.valid:
                await self.client.get_command('run_after_edit').invoke(ctx)


def setup(client):
    client.add_cog(Run(client))
