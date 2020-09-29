from selenium import webdriver
import platform
import time
import random


class Engine(object):
    def __init__(self):
        self.driver_path = './chromedriver'
        if(platform.system() != 'Linux'):
            self.driver_path += '.exe'
        self.log_file = 'log.txt'
        self.started_file = 'started.txt'
        self.names = open('names.txt', 'r').read().strip().split('\n')
        self.phones = open('phones.txt', 'r').read().strip().split('\n')
        self.image = open('image.txt', 'r').read().strip()
        self.msg = open('msg.txt', 'r').read().strip()
        self.delay = open('delay.txt', 'r').read().strip().split(',')
        self.delay = [int(d) for d in self.delay]

    def start_driver(self):
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.driver.get('https://web.whatsapp.com/')

    def send_msg(self, phone, text, image_path=''):
        self.driver.get('http://web.whatsapp.com/send?phone=' + phone + '&text=' + text)  # noqa
        time.sleep(5)
        if('Phone number shared via url is invalid.' in self.driver.page_source):  # noqa
            return False
        time.sleep(2)
        if(len(image_path.strip()) > 0):
            self.driver.find_element_by_xpath("//div[@title='Attach']").click()
            time.sleep(1)
            inpt = self.driver.find_element_by_xpath("//input[@type='file']")
            inpt.send_keys(image_path)
            time.sleep(1)
            self.driver.execute_script("document.getElementsByClassName('_3y5oW _3qMYG')[0].click()")  # noqa
        else:
            if(len(text.strip()) > 0):
                self.driver.find_element_by_xpath("//button[@class='_1U1xa']").click()  # noqa
        return True

    def start_sending(self):
        f2 = open(self.started_file, 'w')
        f2.write('yes')
        f2.close()
        for i, (phone, name) in enumerate(zip(self.phones, self.names)):
            f = open(self.log_file, 'a')
            try:
                send = self.send_msg(phone, self.msg.replace('{name}', '{}').format(name), image_path=self.image)  # noqa
            except:  # noqa
                f.write('err\n')
                f.close()
                continue
            if(send):
                sleep_time = random.choices(self.delay)[0]
                log_msg1 = f"Sent to: {name}:{phone}"
                f.write(log_msg1 + '\n')
                f.close()
                if(i < len(self.phones) - 1):
                    log_msg2 = f'sleeping for {sleep_time} seconds...'
                    f.write(log_msg2 + '\n')
                    time.sleep(sleep_time)
                    f.close()
            else:
                f.write(f"Couldn't send to {name}:{phone}\n")
                f.close()
        time.sleep(2)
        f = open(self.log_file, 'a')
        f2 = open(self.started_file, 'w')
        f.write('done!\n')
        f.write('-' * 20 + '\n')
        f2.write('no')
        f.close()
        f2.close()


if __name__ == '__main__':
    wa_sender = Engine()
    wa_sender.start_driver()
    time.sleep(10)
    wa_sender.start_sending()
