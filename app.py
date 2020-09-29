from flask import Flask, request, render_template, redirect
import os
import signal
import subprocess


files = [
    'started.txt',
    'log.txt',
    'names.txt',
    'phones.txt',
    'msg.txt',
    'image.txt',
    'delay.txt'
]

for f in files:
    if(not os.path.isfile(f)):
        f = open(f, 'w')
        f.write('')
        f.close()


app = Flask('Whats app sender')


def save_data(names, phones, msg, image, delay):
    # save names and phones
    names_file = open('names.txt', 'w')
    phones_file = open('phones.txt', 'w')
    msg_file = open('msg.txt', 'w')
    image_file = open('image.txt', 'w')
    delay_file = open('delay.txt', 'w')
    # write data
    names_file.write(names + '\n')
    phones_file.write(phones + '\n')
    image_file.write(image + '\n')
    msg_file.write(msg + '\n')
    delay_file.write(f'{delay[0]},{delay[1]}' + '\n')
    # close files
    names_file.close()
    phones_file.close()
    image_file.close()
    msg_file.close()
    delay_file.close()


def read_data():
    # save names and phones
    names = open('names.txt', 'r').read()
    phones = open('phones.txt', 'r').read()
    msg = open('msg.txt', 'r').read()
    image = open('image.txt', 'r').read()
    delay = open('delay.txt', 'r').read().strip().split(',')
    if(len(delay) < 2):
        delay = [40, 50]
    return [names, phones, msg, image, delay]


@app.route('/', methods=['GET', 'POST'])
def index():
    # read fields
    names, phones, msg, image, delay = read_data()
    # define proc var that will handle sending process
    global proc
    # as default set started as no
    started = 'no'
    # try to get started value from saved file
    try:
        started = open('started.txt', 'r').read().strip()
    except FileNotFoundError:
        pass
    # if there is post request
    if(request.method == 'POST'):
        # get fields values
        delay = (
            int(request.form.get('delay_from', 40)),
            int(request.form.get('delay_to', 50)),
        )
        names = request.form.get('names', '')
        phones = request.form.get('phones', '')
        image = request.form.get('image', '')
        msg = request.form.get('msg', 'welcome {name}')
        save_data(names, phones, msg, image, delay)
        # open started file
        started_file = open('started.txt', 'w')
        # if user wants to start sending
        if(request.form.get('start', False)):
            started = open('started.txt', 'r').read().strip()
            if(started != 'yes'):
                # start sending process
                proc = subprocess.Popen(['python', 'engine.py'], preexec_fn=os.setsid)  # noqa
                # write started value
                started_file.write('yes')
                started = 'yes'
                # redirect to index to avoiding reload post request
                return redirect('/')
        # if user wants to stop sending
        if(request.form.get('stop', False)):
            # stop sending process
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except:  # noqa
                pass
            # write started value
            started_file.write('no')
            started = 'no'
        # if user wants to save data
        if(request.form.get('save', False)):
            save_data(names, phones, msg, image, delay)
            return redirect('/')
        started_file.close()
    return render_template('index.html',
                           started=started,
                           names=names,
                           phones=phones,
                           msg=msg,
                           image=image,
                           delay=delay
                           )


@app.route('/log')
def get_log():
    try:
        log = open('log.txt', 'r').read()
    except FileNotFoundError:
        log = ''
    return log


@app.route('/clear-log')
def clear_log():
    log_file = open('log.txt', 'w')
    log_file.write('')
    log_file.close()
    return 'done'


@app.route('/check', methods=['GET', 'POST'])
def check_process():
    try:
        started = open('started.txt', 'r').read()
    except FileNotFoundError:
        started = 'no'
    return started


app.run(port=3000, debug=True)
