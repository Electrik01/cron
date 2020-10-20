import schedule
import time
import logging
import subprocess
import os
from datetime import datetime
from crontab import CronTab

class Job:
    def __init__(self,cronLine):
        self.time = cronLine.schedule(date_from=datetime.now()).get_next().strftime("%d.%m.%Y %H:%M")
        self.command = cronLine.command


def getCronJobs():
    cron = CronTab(tabfile="jobs.tab")  
    cronJobs.clear()
    for cronLine in cron:
        cronJobs.append(Job(cronLine))

def initialization():
    logging.info("Initialization start")
    starttime = datetime.now().second
    logging.info("Getting cron jobs")
    getCronJobs()
    time.sleep(60-starttime)
    createJobs()

###    
logging.basicConfig(filename='cron.log', filemode='a', level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d:%(name)s:%(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
cronJobs =  []
###

def createJobs():
    for job in cronJobs:
        if job.time==datetime.now().strftime("%d.%m.%Y %H:%M"):
            pid = os.fork()
            if pid==0:
                try:
                    logging.info("Trying to create a process")
                    subprocess.call([job.command])                
                except Exception as e:
                    logging.warning(e)
                    os._exit(os.EX_OSERR)
                logging.info("Process created")
                os._exit(os.EX_OK)
    logging.info("Updating cron jobs")
    getCronJobs()

def main():
    initialization()
    schedule.every().minute.do(createJobs)
    while True:
        schedule.run_pending()
        time.sleep(1)

main()