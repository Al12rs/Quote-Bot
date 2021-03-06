from discord.ext import commands
import discord
import asyncio


class Quote:
    """Quote a message by adding the reaction!"""

    def __init__(self, bot):
        self.bot = bot

    async def quote_message(self, message=None, message_to_quote=None, requestor=None, ctx=None):
        embed_args = {
            'description': message_to_quote if message_to_quote else message.content,
            'timestamp': ctx.message.created_at if message_to_quote else message.created_at,
        }
        try:
            embed_args['colour'] = requestor.colour if message_to_quote else message.author.colour
        except:
            pass
        embed = discord.Embed(**embed_args)
        avatar_url = message.author.avatar_url if message else requestor.avatar_url
        name = message.author.display_name if message else requestor.display_name
        embed.set_author(name=name, icon_url=avatar_url)
        if requestor:
            embed.set_footer(text="Requested by: {}".format(requestor.display_name))

        if message.content == "" or message.content is None:
            embed.set_image(url=message.attachments[0].url)

        if ctx:
            target = ctx
        else:
            target = message.channel

        await target.send(embed=embed)
        if not message_to_quote:
            await message.add_reaction('\U0001f44d')

        log_embed = embed
        if type(message.channel) == discord.channel.TextChannel:
            server_id = "{0.name} ({0.id})".format(message.channel.guild)
        else:
            server_id = "Private Message"
        log_embed.add_field(name="Server", value=server_id)
        log_embed.add_field(name="Requestor ID", value=requestor.id)
        log_embed.add_field(name="User ID", value=message.author.id)
        log_embed.add_field(name="Message ID", value=message.id)
        log_channel = self.bot.get_channel(self.bot.log_channel)
        await log_channel.send(embed=log_embed)

    async def on_raw_reaction_add(self, payload):
        try:
            emoji = payload.emoji
            message_id = payload.message_id
            channel_id = payload.channel_id
            user_id = payload.user_id
            channel = self.bot.get_channel(channel_id)
            message = await channel.get_message(message_id)
            user = channel.guild.get_member(user_id)
            if emoji.name != self.bot.quote_emote:
                return
            for reaction in message.reactions:
                if reaction.emoji == emoji.name and not user.bot and reaction.count == 1:
                    await self.quote_message(message, requestor=user)
        except Exception as e:
            self.bot.log(e)

    @commands.command(name='id')
    async def id_command(self, ctx, *, message_id):
        """Quote a message with a specific Message ID in the current channel"""
        try:
            message = await ctx.channel.get_message(int(message_id))
            await self.quote_message(message, requestor=ctx.channel.guild.get_member(ctx.author.id))
        except Exception as e:
            self.bot.log(e)
            await ctx.send("I couldn't find a message with that ID, sorry :(")
        try:
            await ctx.message.delete()
        except:
            pass
        
    @commands.command(name='from')
    async def id_command(self, ctx, *, channel: discord.TextChannel, *, message_id):
        """Quote a message from a specific channel with a specific Message ID in the current channel"""
        try:
            message = await channel.get_message(int(message_id))
            await self.quote_message(message, requestor=ctx.channel.guild.get_member(ctx.author.id))
        except Exception as e:
            self.bot.log(e)
            await ctx.send("I couldn't find a message with that ID from that channel, sorry :(")
        try:
            await ctx.message.delete()
        except:
            pass

    @commands.command(name='user')
    async def user_command(self, ctx, *, user : discord.Member):
        """Quote the last message from a specific user in the current channel"""
        message = None
        async for m in ctx.channel.history(limit=None, before=ctx.message, reverse=False):
            if m.author == user:
                message = m
                break
        if message:
            await self.quote_message(message, ctx=ctx, requestor=ctx.channel.guild.get_member(ctx.author.id))
        else:
            await ctx.send("I couldn't find the last message {} sent, sorry :(".format(user.name))
        try:
            await ctx.message.delete()
        except:
            pass
    
    @commands.command(name='quote')
    async def quote_command(self, ctx, *, message: str):
        """Quote a specific message"""
        if message:
            await self.quote_message(message=ctx.message, message_to_quote=message, ctx=ctx, requestor=ctx.channel.guild.get_member(ctx.author.id))
        else:
            await ctx.send("I can't quote that for some reason, sorry :(")
        try:
            await ctx.message.delete()
        except:
            pass


def setup(bot):
    bot.add_cog(Quote(bot))
