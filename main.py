import discord
import asyncio
import re
from apiclient.discovery import build


# Loading keys from keys.txt
arq = open('keys.txt', 'r') # 1st line = Youtube Key // 2nd line = Discord Key
youtubeKey = arq.readline().strip()
discordKey = arq.readline().strip()
arq.close()

print("Youtube key: " + youtubeKey)
print("Discord key: " + discordKey)


print("Building youtube")
DEVELOPER_KEY = youtubeKey # Youtube API Key (console.developers.google.com)
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
search_response = youtube.search().list(
        q="Google",
        part="id,snippet",
        maxResults=5
    ).execute()
print("Youtube builded")

bot = discord.Client()
serverList = [] # server
prefixo = [] # string
tocando = [] # boolean
conectadoVoiceChat = [] # boolean
chVoice = [] # voice ch
links = [[]] # string
player = [[]] # player
contadorAtual = [] # int
esperandoEscolha = [[[]]]
titulosMusicas = [[[]]]
escolhaUsuario = [[]] # lista com usuarios que tão pra fazer escolha
pausado = [] # boolean
search_response = [[[]]]

prefixoOriginal = "!"

idsVideos = [[]]
filaApresentavel = [[]]
CONTMAXPADRAO = 3
contMax = [CONTMAXPADRAO] # quantas músicas aparecem em !list



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(game=discord.Game(name="w/ M1C"))

@bot.event
async def on_message(message):
    achou = False
    while not achou:

        for ch in serverList:
            if ch == message.server:
                i = serverList.index(ch)
                achou = True
                break
        if not achou:
            adcLista(message)

    if message.content.startswith("{}debugg".format(prefixo[i])):
        fala = "```Servers:\t "+str(serverList)+"\nLinks:\t "+str(links)+"\nPrefixos:\t "+str(prefixo)+"\nUsuarios na fila de escolha:\t "+str(escolhaUsuario)+"\nTitulos para escolher:\t "+str(titulosMusicas)+"\nEsperando escolha:\t "+str(esperandoEscolha)+"```"
        await bot.send_message(message.channel, fala)




    if message.content.startswith(str.format('{}play ', prefixo[i])):
        if not conectadoVoiceChat[i]:
            try:
                chVoice[i] = await bot.join_voice_channel(message.author.voice.voice_channel)
                conectadoVoiceChat[i] = True
            except:
                await bot.send_message(message.channel, 'Você precisa se conectar em um canal de voz')


        if message.content == "{}play".format(prefixo[i]):
            await bot.send_message(message.channel, "Type **{}play [query/link]** to search a music on youtube or insert it directly to the player!".format(prefixo[i]))
        else:
            termo = message.content[5+len(prefixo[i]):]

            if(conectadoVoiceChat[i]):
                if (termo.startswith("https://") or termo.startswith("http://")):
                    print("Adicionando por link")
                    try:
                        u = escolhaUsuario[i].index(message.author)
                        resetarEscolhas(i, u)
                    except:
                        pass
                    filaApresentavel[i].append(
                        " - {0} (**{1}**)".format(
                            retornarTitle(termo.split("https://www.youtube.com/watch?v=")[1][:11]),
                            str(message.author.nick)))
                    links[i].append(termo)
                    if not tocando[i]:
                        await tocar(links[i][0], i)
                else:
                    try:
                        u = escolhaUsuario[i].index(message.author)
                        print("{} esta na lista de espera".format(message.author))
                        try:
                            termo = int(termo)
                            termo -= 1
                            if termo < len(esperandoEscolha[i][u]) and termo >= 0:
                                links[i].append("https://www.youtube.com/watch?v=" + esperandoEscolha[i][u][termo])
                                await bot.send_message(message.channel, "{0}, você escolheu a opção **#{1}**: {2}".format(
                                    str(message.author.nick), termo + 1, str(titulosMusicas[i][u][termo])))
                                filaApresentavel[i].append(
                                    " - {0} (**{1}**)".format(
                                        retornarTitle(esperandoEscolha[i][u][termo]),
                                        str(message.author.nick)))
                                resetarEscolhas(i,u)
                                if not tocando[i]:
                                    await tocar(links[i][0], i)
                        except:
                            await procurarVideos(termo, i, u, message.channel)
                    except:
                        print("{} não esta na lista de espera".format(message.author))
                        novasEscolhas(i, message.author)
                        u = escolhaUsuario[i].index(message.author)
                        await procurarVideos(termo, i, u, message.channel)


    if message.content.startswith("{}skip".format(prefixo[i])):
        if message.content == "{}skip".format(prefixo[i]):
            if(tocando[i]):
                player[i].stop()
                if (len(links[i]) > 1):
                    await bot.send_message(message.channel, "NEXT SONG!")
                else:
                    await bot.send_message(message.channel, "The list ended")
            else:
                await bot.send_message(message.channel, "Não há nada para pular")
        else:
            try:
                termo = int(message.content.split()[1])
                await bot.send_message(message.channel, "Skipped track **#{0}**: **{1}**".format(termo, filaApresentavel[i][termo].split(" ",2)[2]))
                links[i].pop(termo)
                filaApresentavel[i].pop(termo)
                #filaApresentavel[i] = organizarFila(filaApresentavel[i])
            except:
                await bot.send_message(message.channel, "Command must be like **{}skip #** (number must be on list)".format(prefixo[i]))

    if message.content.startswith("{}leave".format(prefixo[i])):
        try:
            await chVoice[i].disconnect()
            conectadoVoiceChat[i] = False
            tocando[i] = False
            contadorAtual[i] = 0
        except:
            chVoice[i] = await bot.join_voice_channel(message.author.voice.voice_channel)
            await chVoice[i].disconnect()
            conectadoVoiceChat[i] = False
            tocando[i] = False
            contadorAtual[i] = 0

    if message.content == '{}pause'.format(prefixo[i]):
        if (not pausado[i]):
            await player[i].pause()
            pausado[i] = True
        else:
            await bot.say(message.channel, "Eu não to cantando mano, pra despausar use {}unpause".format(prefixo[i]))

    if message.content.startswith('{}unpause'.format(prefixo[i])):
        if (pausado[i]):
            player[i].resume()
            pausado[i] = False
        else:
            await bot.send_message(message.channel, "Já to cantando cara, ta lokão?")

    if message.content == "{}stop".format(prefixo[i]):
        tocando[i] = False
        links[i] = []
        filaApresentavel[i] = []
        player[i].stop()

    if message.content == "{}playing".format(prefixo[i]):
        if tocando[i]:
            duracao = player[i].duration
            duracaoatual = converterTempo(contadorAtual[i])
            duracaofinal = converterTempo(duracao)
            resp = "```Vídeo:\t\t\t\t\t" + str(player[i].title) + "\nLink:\t\t\t\t\t\t" + str(
                links[i][0]) + "\nDuração:\t\t\t\t" + str(duracaofinal) + " ( " + str(
                duracaoatual) + " )" + "\nLikes/Dislikes: \t" + str(player[i].likes) + "/" + str(
                player[i].dislikes) + "\n\nDescrição:\n" + str(player[i].description + "```")
            await bot.send_message(message.channel, resp)
        else:
            await bot.send_message(message.channel, "I'm not playing anything :(")

    if message.content == "{}list".format(prefixo[i]):
        #filaApresentavel[i] = organizarFila(filaApresentavel[i])
        if len(filaApresentavel[i]) > 0:
            msg = "What's in the playlist: \n\n"
            cont = 1
            for linha in filaApresentavel[i]:
                if (cont <= contMax[i]):
                    if filaApresentavel[i].index(linha) == 0:
                        msg += "**Now playing -> **"+linha[3:]+"\n\n"
                    else:
                        msg += str(filaApresentavel[i].index(linha)) + linha + "\n"
                else:
                    if(len(filaApresentavel[i]) - contMax[i] > 1 ):
                        msg += "\n +{} songs!".format(len(filaApresentavel[i]) - contMax[i])
                    else:
                        msg += "\n +1 song!"
                    break
                cont += 1
            await bot.send_message(message.channel, msg)
        else:
            await bot.send_message(message.channel, "No playlists :( use {}play to make me sing something :D".format(prefixo[i]))

    if message.content.startswith("{}cp ".format(prefixo[i])):
        termo = message.content.split()
        termo = termo[1]
        if not serverList[i].owner == message.author:
            await bot.send_message(message.channel, "Only the owner can change the prefix")
        elif re.match("[a-zA-Z0-9]", termo):
            await bot.send_message(message.channel, "New prefix can't be a letter nor number")
        elif len(termo) > 2:
            await bot.send_message(message.channel, "Prefix can't be bigger than 2 char")
        else:
            prefixo[i] = termo
            await bot.send_message(message.channel, "Prefix updated! now use `{}` to use commands (:".format(prefixo[i]))

    if message.content == "!rp" and serverList[i].owner == message.author:
        prefixo[i] = prefixoOriginal
        await bot.send_message(message.channel, "Prefix reseted to `{}` by an admin".format(prefixo[i]))

    if message.content.startswith("{}kappa".format(prefixo[i])):
        await bot.send_message(message.channel, "https://i.ytimg.com/vi/NPvAVBZGcGY/maxresdefault.jpg")


    if message.content.startswith('!test'):
        counter = 0
        tmp = await bot.send_message(message.channel, 'Calculating messages...')
        async for log in bot.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await bot.edit_message(tmp, 'You have {} messages.'.format(counter))

async def tocar(url, i):
    tocando[i] = True
    player[i] = await chVoice[i].create_ytdl_player(url,ytdl_options={"source_address": "0.0.0.0"})
    player[i].start()
    while not player[i].is_done():
        await asyncio.sleep(1)
        contadorAtual[i] += 1
    print ("Próxima música")
    #filaApresentavel[i] = organizarFila(filaApresentavel[i], i)
    await pular(i)

async def pular(i):
    contadorAtual[i] = 0
    if (tocando[i] == True):
        links[i].pop(0)
        if(len(links[i]) > 0):
            await tocar(links[i][0], i)
        else:
            tocando[i] = False

async def procurarVideos(query, i, pos, ch):
    search_response[i][pos] = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=5
    ).execute()
    videos = []
    esperandoEscolha[i][pos] = []
    titulosMusicas[i][pos] = []
    for search_result in search_response[i][pos].get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("1 - %s" % (search_result["snippet"]["title"]))
            titulosMusicas[i][pos].append(search_result["snippet"]["title"])
            esperandoEscolha[i][pos].append(search_result["id"]["videoId"])


    fala = "Type **{}play #** to choose something:\n".format(prefixo[i])
    for escolha in videos:
        fala += "\n**{0} **-".format(videos.index(escolha) + 1) + escolha[3:]
    print(fala)
    await bot.send_message(ch, fala)

def retornarTitle(vid):
    search_response = youtube.search().list(
        part="snippet",
        q=vid,
        type="video",
    ).execute()
    for result in search_response.get("items", []):
        if result["id"]["kind"] == "youtube#video":
            title = result["snippet"]["title"]
            break
    print("Title: "+title)
    return title

def converterTempo(duracao):
    duracaoMin = "00"
    if duracao > 60:
        if (duracao // 60 > 9):
            duracaoSegs = str(duracao % 60)
        else:
            duracaoSegs = "0" + str(duracao % 60)
    else:
        if (duracao > 9):
            duracaoSegs = str(duracao % 60)
        else:
            duracaoSegs = "0" + str(duracao % 60)
    duracao //= 60
    if duracao > 60:
        if (duracao // 60 > 9):
            duracaoMin = str(duracao % 60)
        else:
            duracaoMin = "0" + str(duracao % 60)
    duracao //= 60
    if (duracao > 9):
        duracaofinal = str(duracao) + ":" + duracaoMin + ":" + duracaoSegs
    else:
        duracaofinal = "0"+str(duracao) + ":" + duracaoMin + ":" + duracaoSegs
    return duracaofinal


def adcLista(message):
    serverList.append(message.server)
    prefixo.append(prefixoOriginal)
    tocando.append(False)
    conectadoVoiceChat.append(False)
    chVoice.append(None)
    links.append([])
    player.append('')
    contadorAtual.append(0)
    esperandoEscolha.append([[]])
    pausado.append(False)
    titulosMusicas.append([[]])
    escolhaUsuario.append([])
    search_response.append([[]])
    idsVideos.append([])
    filaApresentavel.append([])
    contMax.append(CONTMAXPADRAO)

def resetarEscolhas(i,u):
    escolhaUsuario[i].pop(u)
    esperandoEscolha[i].pop(u)
    titulosMusicas[i].pop(u)
    search_response[i].pop(u)

    esperandoEscolha[i].append([])
    titulosMusicas[i].append([])
    search_response.append([[]])

def novasEscolhas(i, autor):
    escolhaUsuario[i].append(autor)
    search_response[i].append([])
    esperandoEscolha[i].append([])
    titulosMusicas[i].append([])

def organizarFila(lista, i = None):
    '''
    if (not i == None):
        if player[i].is_done():
            if (len(lista) > 0):
                lista.pop(0)

    for linha in lista:
        if lista.index(linha) < 10:
            linha = str(lista.index(linha) - 1) + linha[1:]
        else:
            linha = str(lista.index(linha) - 1) + linha[2:]

    return lista
    '''
    pass

bot.run(discordKey) # discord bot token (discordapp.com/developers)