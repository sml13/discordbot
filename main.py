import discord
import datetime
import requests
import os
import json
from translate import Translator
from discord.ext import commands
from PIL import Image
from io import BytesIO

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True
bot = commands.Bot(command_prefix="als.", intents=permissoes)

@bot.command()
async def ola(ctx:commands.Context):
    usuario = ctx.author
    canal = ctx.channel
    await ctx.reply(f"ola {usuario.display_name} safado \nVocê está no canal: {canal.name}")

entrar_time = {}

@bot.command()
async def bluetuf(ctx:commands.Context):
    usuario = ctx.author
    canal = ctx.channel
    await ctx.reply(f"de bluetuf twice is suiri two hell, disconected 😞🥰💋💆‍♀️😍 ")


@bot.command()
async def entrar(ctx:commands.Context):
    usuario = ctx.author
    entrar_time[usuario] = datetime.datetime.now()
    await ctx.send(f'Oi {usuario.display_name}, você entrou às {entrar_time[usuario]}')

@bot.command()
async def sair(ctx: commands.Context):
    if ctx.author in entrar_time:
        sair_time = datetime.datetime.now()
        usuario = ctx.author
        time_difference = sair_time - entrar_time[ctx.author]
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send('Tchau {}, você saiu às {}. Gastou {} horas, {} minutos, e {} segundos.'.format(usuario.display_name, sair_time, hours, minutes, seconds))
        del entrar_time[ctx.author]
    else:
        await ctx.send('Você ainda não bateu seu ponto de entrada')

URL = "https://v2.jokeapi.dev/joke/Any?lang=pt"

@bot.command()
async def piada(ctx:commands.Context):
    response = requests.get(URL)
    if response.status_code ==200:
        piadadados = response.json()
        #await ctx.reply (f"{piadadados}")
        parte1 = piadadados.get("setup", "")
        parte2 = piadadados.get("delivery", "")
        if parte1 and parte2:
            await ctx.reply (f"{parte1} {parte2}")
        else:
            await ctx.reply (f"Não foi possível obter a piada")

URLFrase = "https://api.quotable.io/random"
@bot.command()
async def frase(ctx:commands.Context):
    response = requests.get(URLFrase)
    if response.status_code ==200:
        conteudofrase = response.json()["content"]
        print (conteudofrase)
        conteudofrase = traduzindo(conteudofrase)
        autorfrase = response.json()["author"]
        if conteudofrase and autorfrase:
            await ctx.reply (f"Sua frase do dia é: {conteudofrase} - {autorfrase}")
        else:
            await ctx.reply (f"Não foi possível obter a frase do dia")

def traduzindo(texto):
    translator = Translator(to_lang="pt")
    traducao = translator.translate(texto)
    return traducao

def asciiConvert(image, type, saveas, scale):
    scale = int(scale)

    #Para abrir a imagem e pegar o tamanho
    img = Image.open(image)
    w, h = img.size

    #Arrumar o tamanho
    img.resize((w // scale, h // scale)).save("resized.%s" % type)

    #abrir nova imagem
    img = Image.open("resized.%s" % type)
    w, h = img.size #vai pegar a nova altura e largura

    #listar com os novos tamanhos conforme a imagem resized
    grid = []
    for i in range(h):
        grid.append(["X"] * w)

    pix = img.load()

    for y in range (h):
        for x in range(w):
            if sum(pix[x, y]) == 0:
                grid[y][x] = "#"
            elif sum(pix[x, y]) in range(1, 100):
                grid[y][x] = "X"
            elif sum(pix[x, y]) in range(100, 200):
                grid[y][x] = "%"
            elif sum(pix[x, y]) in range(200, 300):
                grid[y][x] = "&"
            elif sum(pix[x, y]) in range(300, 400):
                grid[y][x] = "*"
            elif sum(pix[x, y]) in range(400, 500):
                grid[y][x] = "+"
            elif sum(pix[x, y]) in range(500, 600):
                grid[y][x] = "/"
            elif sum(pix[x, y]) in range(600, 700):
                grid[y][x] = "("
            elif sum(pix[x, y]) in range(700, 750):
                grid[y][x] = "'"
            else:
                grid[y][x] = " "

    art = open(saveas, "w")

    for row in grid:
        art.write("".join(row) + "\n")

    art.close()


@bot.command()
async def transformar (ctx:commands.Context, scale=3):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Por favor, adicione uma imagem ao seu comando.")
        return
    
    attachment = ctx.message.attachments[0]
    if attachment.content_type.startswith('image'):
        image_bytes = await attachment.read()
        image = Image.open(BytesIO(image_bytes))

        #Salvar imagem temporariamente na memoria
        temp_image = "temp_image." + attachment.filename.split('.')[-1]
        image.save(temp_image)

        #Conversor para ASCII
        ascii_file = "ascii_art.txt"
        asciiConvert(temp_image, attachment.filename.split('.')[-1],ascii_file,scale)

        #Enviar arquivo ASCII - note: isso é um teste
        await ctx.send(file=discord.File(ascii_file))

        #limpar cache
        os.remove(temp_image)
        os.remove(ascii_file)

    else:
        await ctx.send("O arquivo que enviou não é uma imagem.")

base_url = "https://api.musixmatch.com/ws/1.1/"
lyrics_matcher = "matcher.lyrics.get"
format_url = "?format=json&callback=callback"
artist_search_parameter = "&q_artist="
track_search_parameter = "&q_track="
api_key = "6527a4f33b51761b9f2d15c2c524ae10	"

@bot.command()
async def letra(ctx:commands.Context, musica: str, autormusica: str):
    api_call = base_url + lyrics_matcher + format_url + artist_search_parameter + autormusica + track_search_parameter + musica + api_key
    requests = requests.get(api_call)
    data = requests.json()
    if 'mesage' in data and 'body' in data ['mesage']:
        data = data ['mesage']['body']
        await ctx.reply("Letra de {} por: {}:\n{}".format(musica, autormusica, data ['lyrics']['lyrics_body']))
        print (musica)
        print ('lyrics')
    else:
        await ctx.reply("Letra não encontrada")






@bot.event
async def on_ready():
    print("Ready")

bot.run("")