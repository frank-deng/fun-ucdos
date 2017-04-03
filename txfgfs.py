#!/usr/bin/env python3

FG_DATA_URL='http://localhost:5410/json/fgreport/';
FG_CRASHED_URL='http://localhost:5410/json/sim/crashed';
FG_FREEZE_STATE_URL='http://localhost:5410/json/sim/freeze/master';

import time, threading;
import httplib2, json, sysinfo;
import kbhit, TX;

def getFlightData():
    try:
        result = {};
        h = httplib2.Http();

        resp, content = h.request(FG_DATA_URL);
        data = json.loads(content.decode('UTF-8'));
        for item in data['children']:
            result[item['name']] = item['value'];

        resp, content = h.request(FG_FREEZE_STATE_URL);
        data = json.loads(content.decode('UTF-8'));
        if data.get('value'):
            result['paused'] = True;
        else:
            result['paused'] = False;

        resp, content = h.request(FG_CRASHED_URL);
        data = json.loads(content.decode('UTF-8'));
        if data.get('value'):
            result['crashed'] = True;
        else:
            result['crashed'] = False;

        return result;
    except Exception as e:
        return None;

class ShowClockThread(threading.Thread):
    def __init__(self, tx):
        threading.Thread.__init__(self);
        self.__tx = tx;
    def quit(self):
        self.__running = False;
    def refresh(self):
        self.__tx.write([
            TX.Color(0),
            TX.Text(time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime(time.time())), {
                'x':372, 'y':2, 'size':(24,24), 'fg':0,
            }),
            TX.Color(1),
        ]);
    def run(self):
        self.__running = True;
        while (self.__running):
            self.refresh();
            time.sleep(0.5);

class TXFgfsView:
    __hasFgData = False;
    def __init__(self, tx):
        self.__tx = tx;
        self.__drawFrame();
        self.__clock = ShowClockThread(self.__tx);
        self.__clock.start();

    def close(self):
        self.__tx.write([
            TX.ShowCursor(),
            TX.ShowBar(),
            TX.Clrscr(),
        ]);
        self.__clock.quit();

    def __drawFrame(self):
        self.__tx.write([
            TX.Clrscr(),
            TX.HideCursor(),
            TX.HideBar(),
            TX.Color(0),
            TX.Rect(0,0,640,400,True),
            TX.Color(1),
            TX.Rect(0,0,640,28,True),
            TX.Rect(0,380,640,400,True),
            TX.Line(4,76,636,76),
            TX.Text('飞控中心', {
                'x':4, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'bg':None, 'charSpace':0,
            }),
            TX.Text('CPU温度', {
                'x':12, 'y':32, 'size':(16,16), 'fg':1,
            }),
            TX.Text('GPU温度', {
                'x':140+12, 'y':32,
            }),
            TX.Text('CPU使用率', {
                'x':140*2+12, 'y':32,
            }),
            TX.Text('内存使用率', {
                'x':140*3+12, 'y':32,
            }),
            TX.Text('（没有飞行任务）', {
                'x':4, 'y':382, 'fg':0,
            }),
        ]);

    def update(self, sysdata, fgdata, redraw = False):
        if (redraw):
            self.__drawFrame();
            self.__clock.refresh();

        self.__tx.write([
            TX.Text(' %d℃  '%sysdata['cpu_temp'], {
                'x':0, 'y':48, 'size':(24,24), 'fg':1,
            }),
            TX.Text(' %d℃  '%sysdata['gpu_temp'], {
                'x':140, 'y':48,
            }),
            TX.Text(' %.1f%%  '%(sysdata['cpu_usage']['overall'] * 100), {
                'x':140*2, 'y':48,
            }),
            TX.Text(' %.1f%%  '%(sysdata['mem_usage'] * 100), {
                'x':140*3, 'y':48,
            }),
        ]);

        if None == fgdata:
            if self.__hasFgData:
                self.__hadFgData = False;
                self.__tx.write([
                    TX.Color(0), TX.Rect(0,77,640,379,True),
                    TX.Text('（没有飞行任务）', {
                        'x':4, 'y':382, 'size':(16,16), 'fg':0,
                    }),
                ]);
            return;
        elif None != fgdata and not self.__hasFgData:
            self.__hasFgData = True;
            self.__tx.write([
                TX.Text('机型', {
                    'x':12, 'y':80, 'size':(16,16), 'fg':1,
                }),
                TX.Text('经度', {
                    'x':12, 'y':80+44,
                }),
                TX.Text('纬度', {
                    'x':212, 'y':80+44,
                }),
                TX.Text('飞行时间', {
                    'x':12, 'y':80+44*2,
                }),
                TX.Text('剩余时间', {
                    'x':212, 'y':80+44*2,
                }),
                TX.Text('总距离', {
                    'x':12, 'y':80+44*3,
                }),
                TX.Text('剩余距离', {
                    'x':172, 'y':80+44*3,
                }),
                TX.Text('已飞行距离', {
                    'x':332, 'y':80+44*3,
                }),
            ]);

        if fgdata['longitude-deg'] >= 0:
            fgdata['longitude'] = " %.6fE   "%(abs(fgdata['longitude-deg']));
        else:
            fgdata['longitude'] = " %.6fW   "%(abs(fgdata['longitude-deg']));

        if fgdata['latitude-deg'] >= 0:
            fgdata['latitude'] = " %.6fN   "%(abs(fgdata['latitude-deg']));
        else:
            fgdata['latitude'] = " %.6fS   "%(abs(fgdata['latitude-deg']));

        if fgdata['crashed']:
            statusText = '已坠毁　　　　　';
        elif fgdata['paused']:
            statusText = '已暂停　　　　　';
        else:
            statusText = '飞行中……　　　';

        self.__tx.write([
            TX.Text(' '+fgdata['aircraft'], {
                'x':0, 'y':96, 'size':(24,24), 'fg':1,
            }),
            TX.Text(fgdata['longitude'], {
                'x':0, 'y':96+44,
            }),
            TX.Text(fgdata['latitude'], {
                'x':200, 'y':96+44,
            }),
            TX.Text(' '+fgdata['flight-time-string']+'   ', {
                'x':0, 'y':96+44*2,
            }),
            TX.Text(' '+fgdata['ete-string']+'   ', {
                'x':200, 'y':96+44*2,
            }),
            TX.Text(' %.1fnm'%fgdata['total-distance'], {
                'x':0, 'y':96+44*3,
            }),
            TX.Text(' %.1fnm    '%fgdata['distance-remaining-nm'], {
                'x':160, 'y':96+44*3,
            }),
            TX.Text(' %.1fnm    '%(fgdata['total-distance']-fgdata['distance-remaining-nm']), {
                'x':320, 'y':96+44*3,
            }),
            TX.Text(statusText, {
                'x':4, 'y':382, 'size':(16,16), 'fg':0,
            }),
        ]);

if __name__ == '__main__':
    running = True;
    kbhit.init();
    view = TXFgfsView(TX.TX());
    try:
        while running:
            view.update(sysinfo.SysInfo().fetch(), getFlightData());
            if kbhit.kbhit():
                ch = kbhit.getch();
                if '\x1b' == ch:
                    running = False;
            if (running):
                time.sleep(1);
    except KeyboardInterrupt:
        pass;
    view.close();
    kbhit.restore();
    exit(0);
