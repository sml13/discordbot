import discord
import datetime
import requests
import os
import json
import random
from typing import Union
from translate import Translator
from discord.ext import commands
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import re
import asyncio

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
async def comandos(ctx:commands.Context):
    await ctx.send(f"Lembre de sempre usar o prefixo als.\nbluetuf = Meme do bluetuf\nola = teste de resposta com usuario e canal onde enviou mensagem\npiada = Pega uma piada aleatoria de uma api de piadas, obs: só tem 2 piadas por enquanto\nfrase = Manda uma frase famosa aleatória\nentrar = Bater o ponto de entrada\nsair = Bater o ponto de saida\ntransformar = Envia a imagem como você enviou como ASCII em file txt\nviraremoji = Transforma a sua imagem com emojis\nd20 = Roda um dado de 20 números.\nMais comandos em breve 👹!")

@bot.command()
async def bluetuf(ctx:commands.Context):
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


@bot.command()
async def d20(ctx: commands.Context):
    usuario = ctx.author
    # Generate a random number from 1 to 20
    number = random.randint(1, 20)

    # Create an embed
    embed = discord.Embed(title=f"{usuario.display_name} rolou um D20", description=f"O resultado foi: {number}", color=discord.Color.blue())
    
    # Add the image of the corresponding dice
    file_name = f"dices/{number}.png"  # Assuming the images are in a folder named "dices"
    file = discord.File(file_name, filename=f"{number}.png")
    embed.set_image(url=f"attachment://{number}.png")

    # Send the embed
    await ctx.reply(embed=embed, file=file)

COLORS = {
    (0, 0, 0): "⚫",
    (0, 0, 255): "🔵",
    (255, 0, 0): "🔴",
    (255, 255, 0): "🟡",
    (255, 165, 0): "🟠",
    (255, 255, 255): "⚪",
    (0, 255, 0): "🟢",
}


def euclidean_distance(c1, c2):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    d = ((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2) ** 0.5

    return d


def find_closest_emoji(color):
    c = min(COLORS, key=lambda k: euclidean_distance(color, k))
    return COLORS[c]


def emojify_image(img, size=14):
    WIDTH, HEIGHT = (size, size)
    small_img = img.resize((WIDTH, HEIGHT), Image.NEAREST)
    emoji = ""
    small_img = small_img.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            emoji += find_closest_emoji(small_img[x, y])
        emoji += "\n"
    return emoji


@bot.command()
async def viraremoji(ctx, url: Union[discord.Member, str], size: int = 14):
    if isinstance(url, discord.Member):
        url = url.avatar_url

    def get_emojified_image():
        try:
            r = requests.get(url, stream=True)
            image = Image.open(r.raw).convert("RGB")
            res = emojify_image(image, size)

            if size > 14:
                res = f"```{res}```"
            return res
        except Exception as e:
            print("Error in get_emojified_image:", e)
            return "Error processing the image."

    print("Starting image processing")
    result = await bot.loop.run_in_executor(None, get_emojified_image)
    print("Finished image processing")
    await ctx.send(result)



URL = "http://aspiadas.com/randomjoke.php"

@bot.command()
async def joke(ctx: commands.Context):
    response = requests.get(URL)
    if response.status_code == 200:
        # Decodifica a resposta ISO-8859-1 para UTF-8
        response.encoding = 'ISO-8859-1'
        html = response.text

        # Analisa o HTML para obter a piada
        soup = BeautifulSoup(html, 'html.parser')
        joke_div = soup.find('div', align='center')
        if joke_div:
            joke_text = joke_div.text.strip()
            # Limpa a piada removendo tags HTML restantes
            joke_text = re.sub(r'<.*?>', '', joke_text)
            await ctx.reply(joke_text)
        else:
            await ctx.reply("Não foi possível obter a piada")
    else:
        await ctx.reply("Serviço indisponível.")


#####################################CINEALLIES###############################################
        
@bot.command()
async def cineallies(ctx: commands.Context):
    embed = discord.Embed(title=f"Aqui estão alguns comandos para usar para o CineAllies",description=f"Para LTs:\nproibir: Proibe a pessoa que você mencionar de adicionar filmes.\nlimparlista:remove todos os filmes da lista.\nremoverfilme numero: remove o filme de acordo com numero que você colocou\nvotarfilme: Começa a votação\nOutros comandos:\nlistafilmes = Manda a lista de filmes\nindicar = Indica um filme pro Cineallies.", color=discord.Color.blue())

    await ctx.reply(embed=embed)

@bot.command()
async def indicar(ctx: commands.Context, *, nomedofilme):
    usuario = ctx.author
    # Verificar se o usuário está na lista de indicadores proibidos
    if usuario in indicadores_proibidos:
        await ctx.reply("Você está na lista de indicadores proibidos e não pode indicar filmes.")
    else:
        # Verificar se já existem 10 filmes na lista
        with open("movies.txt", "r") as file:
            filmes = file.readlines()
        if len(filmes) >= 10:
            await ctx.reply("Já existem 10 filmes na lista e não é possível adicionar mais. Utilize comando limparlista ou removerfilme")
        else:
            await ctx.reply(f"O usuário {usuario.display_name} indicou o filme {nomedofilme}.")
            # Salvar o nome do filme no arquivo movies.txt
            with open("movies.txt", "a") as file:
                file.write(nomedofilme + "\n")
                
def check_role(ctx):
    allies_role = discord.utils.get(ctx.guild.roles, name="Allies LT")
    return allies_role in ctx.author.roles

indicadores_proibidos = []

@bot.command()
async def proibir(ctx, proibido: discord.Member):
    if not check_role(ctx):
        await ctx.send("Você não tem permissão para usar este comando.")
        return
    if proibido not in indicadores_proibidos:
        indicadores_proibidos.append(proibido)
        await ctx.send(f'{proibido.display_name} foi adicionado à lista de indicadores proibidos.')
    else:
        await ctx.send(f'{proibido.display_name} já está na lista de indicadores proibidos.')

@bot.command()
async def limparlista(ctx: commands.Context):
    if not check_role(ctx):
        await ctx.send("Você não tem permissão para usar este comando.")
        return
    # Verificar se o arquivo movies.txt existe
    try:
        with open("movies.txt", "r"):
            pass
    except FileNotFoundError:
        await ctx.send("A lista de filmes já está vazia.")
        return

    # Limpar o conteúdo do arquivo movies.txt
    with open("movies.txt", "w") as file:
        file.truncate(0)

    await ctx.send("A lista de filmes foi limpa com sucesso.")

@bot.command()
async def listafilmes(ctx: commands.Context):
    # Ler os filmes do arquivo movies.txt
    with open("movies.txt", "r") as file:
        filmes = file.readlines()

    # Verificar se há filmes na lista
    if filmes:
        # Construir a mensagem com a lista numerada de filmes
        mensagem = "Lista de Filmes:\n"
        for i, filme in enumerate(filmes, start=1):
            mensagem += f"{i}. {filme}"

        # Criar o objeto Embed
        embed = discord.Embed(title="Lista de Filmes", description=mensagem, color=discord.Color.green())

        # Enviar a mensagem com a lista de filmes
        await ctx.send(embed=embed)
    else:
        await ctx.send("A lista de filmes está vazia.")



@bot.command()
async def removerfilme(ctx: commands.Context, indexremovido: int):
    # Verificar se o índice fornecido é válido
    if indexremovido <= 0:
        await ctx.send("O índice fornecido deve ser um número positivo.")
        return

    # Ler os filmes do arquivo movies.txt
    with open("movies.txt", "r") as file:
        filmes = file.readlines()

    # Verificar se o índice fornecido está dentro do intervalo da lista de filmes
    if indexremovido > len(filmes):
        await ctx.send("O índice fornecido está fora do intervalo da lista de filmes.")
        return

    # Remover o filme da lista com base no índice fornecido
    filme_removido = filmes.pop(indexremovido - 1)

    # Escrever a lista atualizada de filmes de volta no arquivo movies.txt
    with open("movies.txt", "w") as file:
        file.writelines(filmes)

    # Enviar mensagem confirmando a remoção do filme
    await ctx.send(f"Filme removido: {filme_removido.strip()}")

@bot.command()
async def votarfilme(ctx: commands.Context, minutosvotacao):
    # Verifica se o autor do comando possui a role "Allies LT"
    if not check_role(ctx):
        await ctx.send("Você não tem permissão para usar este comando.")
        return

    # Lê os filmes do arquivo movies.txt
    filmes = []
    with open("movies.txt", "r") as file:
        filmes = file.readlines()
    filmes = [filme.strip() for filme in filmes]

    if not filmes:
        await ctx.send("Não há filmes para votar.")
        return

    # Cria uma lista de reações para votação
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    # Envia a lista de filmes para votação
    vote_message = "Escolha um filme votando com as reações:\n\n"
    for index, filme in enumerate(filmes):
        vote_message += f"{index + 1}. {filme}\n"
    vote_message += "\nA votação durará " + minutosvotacao + " minutos."
    vote_message = await ctx.send(vote_message)

    # Adiciona as reações à mensagem para votação
    for i in range(min(len(filmes), len(reactions))):
        await vote_message.add_reaction(reactions[i])

    # Aguarda o tempo de votação
    await asyncio.sleep(int(minutosvotacao) * 60)

    # Obtém as reações da mensagem de votação
    vote_message = await ctx.channel.fetch_message(vote_message.id)
    reaction_counts = {react: react.count - 1 for react in vote_message.reactions}

    # Obtém o filme mais votado
    max_votes = max(reaction_counts.values())
    most_voted_film = [filme for filme, votes in reaction_counts.items() if votes == max_votes]
    # Envia o resultado da votação
    await ctx.send(f"O filme mais votado foi {most_voted_film[0]}")

@bot.event
async def on_ready():
    print("Ready")

bot.run("")