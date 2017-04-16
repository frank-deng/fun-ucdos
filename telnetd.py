#!/usr/bin/env python3

import os, sys, time, subprocess, pty, fcntl, socket, select, argparse;

class EnvironParser(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        environ = getattr(namespace, self.dest);
        e = values.split('=');
        if len(e) < 2:
            parser.error('Invalid format detected when specifing environment variable.');
        key = e[0];
        value = '='.join(e[1:]);
        environ[key] = value;
        setattr(namespace, self.dest, environ);

parser = argparse.ArgumentParser();
parser.add_argument(
    '--host',
    '-H',
    help='Specify host for the telnet server.',
    default=''
);
parser.add_argument(
    '--port',
    '-P',
    help='Specify port for the telnet server.',
    type=int,
    default=23
);
parser.add_argument(
    '--environ',
    '-E',
    action=EnvironParser,
    help='Specify environment variable for the login program.',
    default={}
);
parser.add_argument(
    '--login',
    '-L',
    nargs=argparse.REMAINDER,
    help='Specify login program.',
    default=['/bin/login', '-p']
);
args = parser.parse_args();

class Terminal:
    __active = False;
    def __init__(self):
        self.__master, self.__slave = pty.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        self.__startProc();

    def __startProc(self):
        global args;
        env = os.environ.copy();
        env.update(args.environ);
        self.__proc = subprocess.Popen(args.login,
            stdin = self.__slave, stdout = self.__slave, stderr = self.__slave,
            env = env, close_fds = True);

    def close(self):
        self.__active = False;
        self.__proc.kill();
        os.close(self.__slave);
        os.close(self.__master);

    def read(self):
        if (None != self.__proc.poll()):
            self.__startProc();
        try:
            return os.read(self.__master, 65536);
        except BlockingIOError:
            return b'';

    def write(self, data):
        if (None != self.__proc.poll()):
            self.__startProc();
        if self.__active:
            os.write(self.__master, data);
        else:
            self.__active = True;

inputs = [];
outputs = [];
terms = {};
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    server.setblocking(0);
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    server.bind((args.host, args.port));
    server.listen(5);
    inputs.append(server);
except OSError as e:
    print(str(e));
    exit(1);

try:
    while True:
        time.sleep(0.1);
        readable, writable, exceptional = select.select(inputs, outputs, inputs);
        for s in readable:
            if s is server:
                conn, addr = s.accept();
                conn.setblocking(0);
                inputs.append(conn);
                terms[str(conn.fileno())] = Terminal();
            else:
                try:
                    data = s.recv(1024);
                    if data:
                        terms[str(s.fileno())].write(data);
                        if s not in outputs:
                            outputs.append(s);
                except (ConnectionResetError, KeyError):
                    if str(s.fileno()) in terms:
                        terms.pop(str(s.fileno())).close();
                    if s in inputs:
                        inputs.remove(s);
                    if s in outputs:
                        outputs.remove(s);
                    s.close();

        for s in writable:
            try:
                s.sendall(terms[str(s.fileno())].read());
            except (BrokenPipeError, KeyError):
                if str(s.fileno()) in terms:
                    terms.pop(str(s.fileno())).close();
                if s in inputs:
                    inputs.remove(s);
                if s in outputs:
                    outputs.remove(s);
                s.close();

        for s in exceptional:
            if str(s.fileno()) in terms:
                terms.pop().close();
            if s in inputs:
                inputs.remove(s);
            if s in outputs:
                outputs.remove(s);
            s.close();

except KeyboardInterrupt:
    pass;
finally:
    for key, term in terms.items():
        term.close();

