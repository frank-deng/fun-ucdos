#!/usr/bin/env python3
#encoding=UTF-8

import argparse;
parser = argparse.ArgumentParser();
parser.add_argument(
    '--host',
    '-H',
    help='Specify binding host for the server.',
    default=''
);
parser.add_argument(
    '--port',
    '-p',
    help='Specify port for the server.',
    type=int,
    default=8080
);
args = parser.parse_args();

from bottle import route, run, view, template, request, response, redirect;
import models, urllib;

from multiprocessing.pool import ThreadPool;
@route('/')
@view('index')
def index():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();

    pool = ThreadPool(processes=8);
    weatherInfo = pool.apply_async(models.getWeatherInfo, (city,));
    articles = pool.apply_async(models.getArticles);

    return {
        'weather':weatherInfo.get(),
        'articles':articles.get()['content'][0:17],
    };

@route('/weather/detail.do')
def weatherDetail():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();
    weather = models.getWeatherInfo(city);
    if None != weather:
        return template('weatherDetail', {
            'weather':weather,
        });
    else:
        return template('error', {'error':'Failed To Fetch Weather'});

@route('/weather/setcity.do')
@view('weatherSetCity')
def weatherSetCity():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();
    return {
        'city': city,
    };

@route('/weather/setcity.do', method='POST')
def doWeatherSetCity():
    response.set_cookie('city', urllib.parse.quote(request.forms.city.strip()), path='/', max_age=3600*24*356);
    response.status = 301;
    response.set_header('Location', '/weather/detail.do');

@route('/currency')
def currency():
    currencies = models.getCurrencies();
    if not currencies:
        return template('error', {'error':'Initialization Failed'});
    return template('currency', {
        'currencies':currencies,
        'hasResult':False,
        'fromCurrency':request.cookies.getunicode('fromCurrency', ''),
        'toCurrency':request.cookies.getunicode('toCurrency', ''),
        'amount':'',
    });

@route('/news')
def newsList():
    page = int(request.query.get('page', 1));
    data, total = models.getNewsList(page, config.PAGESIZE);
    if (None == data):
        return template('error', {'error':'No News'});
    return template('newsList', {'newsList':data, 'page':page, 'total':total});

@route('/news/<newsId:re:[0-9A-Za-z]+>')
def newsDetail(newsId):
    data = models.getNewsDetail(newsId);
    if (None == data):
        return template('error', {'error':'No News'});
    return template('newsDetail', {'news':data});

@route('/inews')
def iNewsList():
    page = int(request.query.get('page', 1));
    data, total = models.getNewsList(page, config.PAGESIZE, '5572a108b3cdc86cf39001d1');
    if (None == data):
        return template('error', {'error':'No News'});
    return template('iNewsList', {'newsList':data, 'page':page, 'total':total});

@route('/currency', method='POST')
def currencyExchage():
    fromCurrency = request.forms.get('from');
    toCurrency = request.forms.to;
    amount = request.forms.amount;
    response.set_cookie('fromCurrency', fromCurrency, path='/', max_age=3600*24*356);
    response.set_cookie('toCurrency', toCurrency, path='/', max_age=3600*24*356);

    currencies = models.getCurrencies();
    if not currencies:
        return template('error', {'error':'Initialization Failed'});
    fromCurrencyName, toCurrencyName = fromCurrency, toCurrency;
    for c in currencies:
        if (fromCurrency == c['code']):
            fromCurrencyName = c['name'];
        if (toCurrency == c['code']):
            toCurrencyName = c['name'];

    return template('currency', {
        'currencies':currencies,
        'hasResult':True,
        'fromCurrency':fromCurrency,
        'toCurrency':toCurrency,
        'fromCurrencyName':fromCurrencyName,
        'toCurrencyName':toCurrencyName,
        'amount':amount,
        'result':models.doCurrencyExchange(fromCurrency, toCurrency, amount),
    });

@route('/dict')
@view('dict')
def dict():
    word = request.query.word;
    result = models.queryDictionary(word);
    return {
        'word': word,
        'result': result,
    };

@route('/articles')
def articles():
    data = models.getArticles();
    page = int(request.query.get('page', 1));
    if None == data:
        return template('error', {'error':'Failed to load article'});
    return template('articleList', {'articles':data['content'], 'page':page});

@route('/article/<aid:re:[0-9A-Za-z]+>')
def articleDetail(aid):
    title, content = models.getArticleDetail(aid);
    if None == content:
        return template('error', {'error':'Failed to load article'});
    return template('articleDetail', {'title':title, 'article':content});

# Update news every 1 minute
import threading, time, datetime, config;
class ThreadNewsUpdate(threading.Thread):
    def __init__(self, channel=''):
        threading.Thread.__init__(self)
        self.__channel = channel;
    def stop(self):
        self.__running = False;
    def run(self):
        self.__running = True;
        self.__timestamp = time.time();
        models.updateNews(self.__channel);
        print('{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + ' Update News');
        while self.__running:
            time.sleep(1);
            timestamp = time.time();
            if ((timestamp - self.__timestamp) > config.NEWS_UPDATE_INTERVAL):
                self.__timestamp = timestamp;
                models.updateNews(self.__channel);
                print('{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + ' Update News');
        print('{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + ' Stop updating news');

try:
    threadNewsUpdate = ThreadNewsUpdate();
    threadNewsUpdate.start();
    threadNewsUpdate2 = ThreadNewsUpdate('5572a108b3cdc86cf39001d1');
    threadNewsUpdate2.start();
    run(server='eventlet', host=args.host, port=args.port);
except KeyboardInterrupt:
    pass;
finally:
    threadNewsUpdate.stop();
    threadNewsUpdate2.stop();

