import discord
import asyncio
from apiclient.discovery import build

# Loading keys from keys.txt
arq = open('keys.txt', 'r') # 1st line = Youtube Key // 2nd line = Discord Key
youtubeKey = arq.readline().strip()
discordKey = arq.readline().strip()
arq.close()

print(youtubeKey)
print(discordKey)


print("Building youtube")
DEVELOPER_KEY = youtubeKey # Youtube API Key (console.developers.google.com)
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
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



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

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
        fala = "```Servers: "+str(serverList)+"\nLinks: "+str(links)+"\nPrefixos: "+str(prefixo)+"\nUsuarios na fila de escolha: "+str(escolhaUsuario)+"\nTitulos: "+str(titulosMusicas)+"\nEsperando escolha: "+str(esperandoEscolha)+"```"
        await bot.send_message(message.channel, fala)




    if message.content.startswith(str.format('{}play ', prefixo[i])):
        if not conectadoVoiceChat[i]:
            try:
                chVoice[i] = await bot.join_voice_channel(message.author.voice.voice_channel)
                conectadoVoiceChat[i] = True
            except:
                await bot.send_message(message.channel, 'Você precisa se conectar em um canal de voz')

        termo = message.content[6:]

        if(conectadoVoiceChat[i]):
            if (termo.startswith("https://") or termo.startswith("http://")):
                try:
                    u = escolhaUsuario[i].index(message.author)
                    resetarEscolhas(i, u)
                except:
                    pass

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
                                str(message.author)[:-5], termo + 1, str(titulosMusicas[i][u][termo])))
                            resetarEscolhas(i,u)
                            if not tocando[i]:
                                await tocar(links[i][0], i)
                    except:
                        await procurarVideos(termo, i, u, message.channel)
                except:
                    print("{} não esta na lista de espera".format(message.author))
                    escolhaUsuario[i].append(message.author)
                    u = escolhaUsuario[i].index(message.author)
                    await procurarVideos(termo, i, u, message.channel)


    if message.content.startswith("{}skip".format(prefixo[i])):
        await pular(i)


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




    if message.content.startswith('{}pause'.format(prefixo[i])):
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


    if message.content.startswith("{}stop".format(prefixo[i])):
        player[i].stop()
        tocando[i] = False
        links[i] = []


    if message.content.startswith("{}playing".format(prefixo[i])):
        if tocando[i]:
            duracao = player[i].duration
            duracaoatual = converterTempo(contadorAtual[i])
            duracaofinal = converterTempo(duracao)
            resp = "Vídeo:\t\t\t\t\t" + str(player[i].title) + "\nLink:\t\t\t\t\t\t" + str(
                links[i][0]) + "\nDuração:\t\t\t\t" + str(duracaofinal) + " ( " + str(
                duracaoatual) + " )" + "\nLikes/Dislikes: \t" + str(player[i].likes) + "/" + str(
                player[i].dislikes) + "\n\nDescrição:\n" + str(player[i].description)
            await bot.send_message(message.channel, resp)
        else:
            await bot.send_message(message.channel, "Não to tocando nada :(")



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
    player[i] = await chVoice[i].create_ytdl_player(url)
    player[i].start()
    tocando[i] = True
    while not player[i].is_done():
        await asyncio.sleep(1)
        contadorAtual[i] += 1
    print ("Próxima música")
    await pular(i)

async def pular(i):
    contadorAtual[i] = 0
    if (len(links[i]) > 0):
        links[i].pop(0)
        await tocar(links[i][0], i)
    else:
        tocando[i] = False

async def procurarVideos(query, i, pos, ch):
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=5
    ).execute()
    videos = []
    esperandoEscolha[i][pos] = []
    titulosMusicas[i][pos] = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("1 - %s" % (search_result["snippet"]["title"]))
            titulosMusicas[i][pos].append(search_result["snippet"]["title"])
            esperandoEscolha[i][pos].append(search_result["id"]["videoId"])


    fala = "Escolha uma opção com **{}play #**:\n".format(prefixo[i])
    for escolha in videos:
        fala += "\n**{0} **-".format(videos.index(escolha) + 1) + escolha[3:]
    print(fala)
    await bot.send_message(ch, fala)

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
    prefixo.append("!")
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

def resetarEscolhas(i,u):
    escolhaUsuario[i].pop(u)
    esperandoEscolha[i].pop(u)
    titulosMusicas[i].pop(u)

    esperandoEscolha[i].append([])
    titulosMusicas[i].append([])


bot.run(discordKey) # discord bot token (discordapp.com/developers)