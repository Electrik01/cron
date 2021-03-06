from datetime import datetime
from croniter import croniter
from crontab import CronTab
import logging
import logging.config
import subprocess
import os
import time
import config
import pytz



class Job:
    def __init__(self,cronItem):
        self.iter = croniter(str(cronItem.slices),base)
        self.command = cronItem.command
        self.time = self.iter.get_next(datetime)
    def create(self):
            pid = os.fork()
            if pid==0:
                try:
                    subprocess.call([self.command],shell=True)                
                except Exception as e:
                    logging.warning(e)
                    os._exit(os.EX_OSERR)
                logging.info("Process created. PID: "+str(os.getpid()))
                os._exit(os.EX_OK)
            else:
                self.time = self.iter.get_next(datetime)

def setCronJobs():
    cronJobs.clear()
    try:       
        cron = CronTab(tabfile=cronPath)
    except FileNotFoundError as e:
        logging.warning(e)
        os._exit(os.EX_OSERR)
    for cronItem in cron:
        cronJobs.append(Job(cronItem))
    if len(cronJobs)==0:
        logging.info("Hibernation. No task")
        m_time = os.stat(cronPath).st_mtime
        while os.stat(cronPath).st_mtime == m_time:
            time.sleep(h_time)
        logging.info("Trying to start")
        setCronJobs()
    

def initialization():
    global cronJobs,base,cronPath,h_time
    currentDate = datetime.now()
    try:
        logging.config.fileConfig(config.LOGS_CONFIG)
    except KeyError as e:
        print(e)
        os._exit(os.EX_OSERR)
    try:
        timeZone = pytz.timezone(config.TIME_ZONE)
        base = timeZone.localize(datetime.now())
        cronJobs=[]
        h_time = int(config.HIBERNATION_PERIOD)
        cronPath=config.CRONTAB_PATH
    except Exception as e:
        logging.warning(e)
        os._exit(os.EX_OSERR)
    logging.info("Initialization complete")

def cron():
    m_time = os.stat(cronPath).st_mtime
    while True:
        if os.stat(cronPath).st_mtime != m_time:
            logging.info("File has been modified")
            m_time = os.stat(cronPath).st_mtime
            setCronJobs()
        for job in cronJobs:
            if job.time.strftime("%d.%m.%Y %H:%M")==datetime.now().strftime("%d.%m.%Y %H:%M"):
                job.create()
        time.sleep(1)

def main():
    initialization()
    setCronJobs()
    cron()
    
                
main()

