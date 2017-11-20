
from telegram.ext import Updater, CommandHandler
import logging
import os
import sys
import telepot
import sqlite3
import feedparser
import time
from bs4 import BeautifulSoup
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.request import urlopen


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def alarm(bot, job):
    try:
        conn = sqlite3.connect('feedero.db')
        chat_id='@feederinhoCanal'
        read = open('lista.txt', 'r+')
        linha = (read.readline(),)
        x = 0
        while(linha[x]):
            linha+=(read.readline(),)
            x+=1
        read.close()
        cont = 0
        for x in range(len(linha)-1):
            print ('Iniciando codigo: '+str(time.strftime("%Y-%m-%d %H:%M:%S" )))
            sql = 'SELECT post_id FROM feedero WHERE feed_link = (?)'
            rodar = 1
            post = feedparser.parse(linha[x])
            print ('Link: '+linha[x]+' :'+str(time.strftime("%Y-%m-%d %H:%M:%S" )))
            curs = conn.cursor()
            curs.execute(sql,(linha[x],))
            result = curs.fetchone()
            # verifica se o feed tem erro de bozo
            if (post['bozo'] == 1):
                print('com bozo: '+str(time.strftime("%Y-%m-%d %H:%M:%S" )))
                url = (linha[x])
                ler = urlopen(url)
                soup = BeautifulSoup(ler,'html.parser')
                #titulo da noticia
                titles = soup.find_all('title')

                #link da noticia
                posts = soup.find_all('guid')
                ler.close()
                if(result):
                    cont = 1
                    #atribui o guid(links da pagina) para a variavel i
                    for i in posts:
                        #i.text compara os links que estao no banco
                        if(result[0] == i.text):

                            for z in range(cont):
                                if(titles[z].text != 'Fundação Cultural Palmares'):
                                    bot.sendMessage(chat_id,''+titles[z].text+'\n'+posts[z].text, timeout=300)

                            sql = '''UPDATE feedero SET post_id = ? WHERE feed_link = ?'''
                            curs = conn.cursor()
                            params = (posts[0].text,linha[x])
                            curs.execute(sql,params)
                            conn.commit()

                            break
                        else:
                            cont+=1
                else:
                    print('nao existe'+str(time.strftime("%Y-%m-%d %H:%M:%S" )))
                    sql = 'INSERT INTO feedero VALUES (?,?)'
                    curs = conn.cursor()
                    params = (posts[0].text,linha[x])
                    result = curs.execute(sql,params)
                    for z in range(len(posts)):
                        if(titles[z].text != 'Fundação Cultural Palmares'):
                            bot.sendMessage(chat_id,""+titles[z].text+'\n'+posts[z].text, timeout=300)
                    conn.commit()
            else:
                if(result):
                    cont = 0
                    while (rodar):
                        for i in range(len(post['entries'])):
                            if (result[0] == (post['entries'][i]['id'])):
                                for z in range(cont):
                                    bot.sendMessage(chat_id,""+post['entries'][z]['title']+'\n'+post['entries'][z]['id'], timeout=300)
                                sql = '''UPDATE feedero SET post_id = ? WHERE feed_link = ?'''
                                curs = conn.cursor()
                                params = (post['entries'][0]['id'],linha[x])
                                curs.execute(sql,params)
                                conn.commit()
                                rodar = 0
                                break
                            else:
                                cont+=1
                else:
                    print('não existe'+str(time.strftime("%Y-%m-%d %H:%M:%S" )) )
                    sql = 'INSERT INTO feedero VALUES (?,?)'
                    curs = conn.cursor()
                    params = (post['entries'][0]['id'],linha[x])
                    result = curs.execute(sql,params)
                    for z in range(len(post['entries'])):
                        bot.sendMessage(chat_id,""+post['entries'][z]['title']+'\n'+post['entries'][z]['id'], timeout=300)
                    conn.commit()
        conn.close()

    except():
        bot.sendMessage(chat_id, "Erros-------------------------------------------------------")


def set_timer(bot, update, args, job_queue, chat_data):

    chat_id = update.message.chat_id
    try:

        due = 240  #Tempo em segundos!


        job = job_queue.run_repeating(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text('Serviço reiniciado com sucesso! \n Continuando execução...')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')

def error(bot, update, error):

    logger.warning('Update "%s" caused error "%s"', update, error)


def main():

    updater = Updater(os.environ.get('FEED_TOKEN'))


    dp = updater.dispatcher


    dp.add_handler(CommandHandler("start", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling(timeout=8220)

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
