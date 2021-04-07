from __future__ import print_function
import keyboard
import argparse
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
import re
import os
import json
import datetime
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ics import Calendar, Event
import sys
import getpass

from credentials.secretensiie import passw, gCal, user_name
from setup_files.filespath import *
from setup_files.colors import *

# Adresse d'AurionWeb
BASE_ADDRESS = "https://aurionweb.ensiie.fr/"

# Emplacement de sauvegarde des résultats bruts (inutilisé dans un mode de fonctionnement normal)
RAWRESULTSJSON_PATH = r"./results/results_raw.json"


class EDTExtr():
    def __init__(self,is_headless=False,is_free=True,links=False,verbose_mode=False):
        if(is_headless):
            print("\n--Headless mode--")
        print(
            f"\n-----------------\n{bcolors.OKCYAN}Initialising...{bcolors.ENDC}")
        options = Options()
        options.binary_location = BROWSER_PATH
        options.headless = is_headless
        if(verbose_mode):
            options.add_argument('log-level=0')
        else:
            options.add_argument('log-level=2')
        if(is_headless):
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
        self.headless = is_headless
        self.with_links = links
        self.asked_to_be_free = is_free
        self.driver = webdriver.Chrome(DRIVER_PATH, options=options)
        self.driver.get(BASE_ADDRESS)
        print(f"{bcolors.OKGREEN}Initialising done!{bcolors.ENDC}")
    
    def connect(self, input_user_name, input_passw):
        print(
            f"\n-----------------\n{bcolors.OKCYAN}Connecting...{bcolors.ENDC}")
        email_boite = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='username']")))
        try :
            email_boite.clear()
            if(input_user_name == ""):
                user2 = input(
                    f"{bcolors.WARNING}Please input your AurionWeb username (prenom.nom): \n{bcolors.ENDC}")
                email_boite.send_keys(user2)
            else:
                email_boite.send_keys(input_user_name)

            password_box = self.driver.find_element_by_xpath('//*[@id="password"]')
            password_box.clear()
            if(input_passw == ""):
                passw2 = getpass.getpass(
                    f"{bcolors.WARNING}Please input your AurionWeb password: \n{bcolors.ENDC}")
                password_box.send_keys(passw2)
            else:
                password_box.send_keys(input_passw)

            identifier = self.driver.find_element_by_xpath(
                '//*[@id="fm1"]/section[4]/input[4]')
            identifier.click()


        except Exception as e:
            if(input(f"{bcolors.FAIL}Connexion failed. An error occurred: {e}. Retry and input credentials? (y/n)\n{bcolors.ENDC}") == "y"):
                self.connect(r"", r"")
            else:
                if(not(self.headless)):
                    self.close()
                print(f"\n{bcolors.WARNING}Program closing...{bcolors.ENDC}")
                delete_tmp_files()
                sys.exit(0)
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/form/div[2]/div[2]/div/div[1]/div[1]/div/div/div[2]/ul/li[3]/a")))
            print(f"{bcolors.OKGREEN}Connected!{bcolors.ENDC}")
        except:
            if(input(f"{bcolors.FAIL}Connexion failed. Verify your credentials. Retry and input credentials? (y/n)\n{bcolors.ENDC}") == "y"):
                self.connect(r"", r"")
            else:
                if(not(self.headless)):
                    self.close()
                print(f"\n{bcolors.WARNING}Program closing...{bcolors.ENDC}")
                delete_tmp_files()
                sys.exit(0)
        


    def go_to_edt(self):
        print(f"\n-----------------\n{bcolors.OKCYAN}Going To EDT...{bcolors.ENDC}")
        
        try:
            WebDriverWait(self.driver, 0.25).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/form/div[2]/div[2]/div/div[1]/div[1]/div/div/div[2]/ul/li[4]/a"))).click()
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/form/div[2]/div[2]/div/div[1]/div[1]/div/div/div[2]/ul/li[4]/ul/li[1]/a"))).click()
        except:
            try:
                print(f"{bcolors.WARNING}\nWARNING: Impossible to click; Trying another method...{bcolors.ENDC}")
                edt_btn = self.driver.find_element_by_xpath(
                    '/html/body/div[1]/form/div[2]/div[2]/div/div[1]/div[1]/div/div/div[2]/ul/li[3]/a')
                edt_btn.click()
                sleep(1)
                my_edt_btn = self.driver.find_element_by_xpath(
                    '/html/body/div[1]/form/div[2]/div[2]/div/div[1]/div[1]/div/div/div[2]/ul/li[3]/ul/li[1]/a')
                my_edt_btn.click()
            except:
                print(f"{bcolors.FAIL}\nERROR: Impossible to connect. Exiting...{bcolors.ENDC}")
                if(not(self.headless)):
                    self.close()
                print(f"\n{bcolors.WARNING}Program closing...{bcolors.ENDC}")
                delete_tmp_files()
                sys.exit(0)

        print(f"{bcolors.OKGREEN}In EDT!{bcolors.ENDC}")
        k=0
        while(k<NB_SEMAINES_FUTUR):
            k+=1
            print(f"{bcolors.OKCYAN}Going to next week!{bcolors.ENDC}")
            try:
                next_week_btn = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id = 'form: j_idt117_container']/div[1]/div[1]/button[4]"))).click()
                next_week_btn.click()
            except:
                next_week_btn = self.driver.find_element_by_xpath('//*[@id = "form:j_idt117_container"]/div[1]/div[1]/button[4]')
                next_week_btn.click()
        if(k!=0):
            print(f"{bcolors.OKCYAN}Getting Schedule from {k} week(s) in the future...{bcolors.ENDC}")


    def get_html(self):
        print(f"\n-----------------\n{bcolors.OKCYAN}Getting HTML...{bcolors.ENDC}")
        sleep(0.25)
        self.source_code = self.driver.page_source
        #with open(r"./bug2.html", "w", encoding = "utf-8") as raw_f:
            #raw_f.write(self.source_code)
        print(f"{bcolors.OKGREEN}HTML saved!{bcolors.ENDC}")


    def get_courses(self):
        print(f"\n-----------------\n{bcolors.OKCYAN}Getting EDT...{bcolors.ENDC}")

        list_of_dates_raw = self.driver.find_elements_by_class_name(
            "fc-day-header")
        list_of_dates = (x.text for x in list_of_dates_raw)

        list_of_colonnes = self.driver.find_elements_by_class_name('fc-content-col')
        
        dico = {}
        passe = False

        for jour, colonne_raw, in zip(list_of_dates, list_of_colonnes):
            dico[jour] = []
            try:
                raw_day = re.match(
                    r".* (?P<jour>.*)/(?P<mois>.*)[ ]*", jour).groupdict()
                true_day = f'2021-{raw_day["mois"]}-{raw_day["jour"]}'
            
            except:
                print(
                    f"{bcolors.WARNING}WARNING: Date deducted manually{bcolors.ENDC}")
                true_day = f'2021-{jour[7:9]}-{jour[4:6]}'

            list_of_cours_raw = colonne_raw.find_elements_by_class_name("fc-content")
            
            list_of_cours = (x.text for x in list_of_cours_raw)
            
            list_of_hours_raw = colonne_raw.find_elements_by_class_name(
                "fc-time")
            list_of_hours = [x.get_attribute("data-full") for x in list_of_hours_raw]
            cours_dic = {}
            for heure, cours_infos in zip(list_of_hours, list_of_cours):
                passe = True
                try:
                    cours_dic = re.match(
                        r"-* -* (?P<module>.*) - (?P<prof>.*)[ /.*]* - (?P<salle>.*) - (?P<UE>.*)", cours_infos).groupdict()
                    cours_dic['type'] = "CONF"
                    
                except:
                    try:
                        cours_dic = re.match(
                            r"(?P<module>.*) - (?P<UE>.*) -.*(FISE)*[_, ](?P<type>.*) - (?P<prof>.*) - (?P<salle>.*)[ /.]*.*[,-, ]", cours_infos).groupdict()
                    except:
                        print(f"{bcolors.WARNING}\nWARNING: Impossible to parse data\n{bcolors.ENDC}")
                        cours_dic['infos'] = cours_infos
                
                true_hours = re.match(
                    r"(?P<sth>.*) - (?P<eth>.*)", heure).groupdict()

                tmp = datetime.strptime(true_hours['sth'], "%I:%M %p")
                true_hours['sth'] = datetime.strftime(tmp, "%H:%M")

                tmp = datetime.strptime(true_hours['eth'], "%I:%M %p")
                true_hours['eth'] = datetime.strftime(tmp, "%H:%M")

                cours_dic['startdate'] = true_day + f"T{true_hours['sth']}:00"
                cours_dic['enddate'] = true_day + f"T{true_hours['eth']}:00"
                dico[jour].append(cours_dic)
                
        self.raw_EDT = dico
        print(f"{bcolors.OKGREEN}Schedule saved!{bcolors.ENDC}")
        #only used for debug
        #self.save_results(dico)

        if(not passe):
            print(
                f"{bcolors.WARNING}\nWARNING: No lessons this week!{bcolors.ENDC} ❤ {bcolors.WARNING} Exiting...\n{bcolors.ENDC}")
            if(not(self.headless)):
                self.close()
            print(f"\n{bcolors.WARNING}Program closing...{bcolors.ENDC}")
            delete_tmp_files()
            sys.exit(0)

    def save_results(self,dico):
        with open(RAWRESULTSJSON_PATH, "w", encoding="utf-8") as res_file:
            json.dump(dico, res_file)
            print(f"{bcolors.OKGREEN}Results saved!{bcolors.ENDC}")

    def format_events(self):
        print(f"\n-----------------\n{bcolors.OKCYAN}Formatting results...{bcolors.ENDC}")
        if(asked_to_be_free):
            trsp = 'transparent'
        else:
            trsp = 'opaque'
        list_of_events_to_add = []
        gen_events = (self.raw_EDT[key] for key in self.raw_EDT)
        for elementmoche in gen_events:
            for element in elementmoche:
                try:
                    summary = f"{element['module']} -- {element['type']}"
                    ue_and_prof = f"Prof : {element['prof']} -- {element['UE']}"
                    if ('link' in element):
                        ue_and_prof += f'\n{element["link"]}'
                    new_event = {
                        'summary': f'{summary}',
                        'location': f'{element["salle"]}',
                        'transparency' : trsp,
                        'description': f'{ue_and_prof}',
                        'start': {
                            'dateTime': f'{element["startdate"]}',
                            'timeZone': 'Europe/Paris',
                        },
                        'end': {
                            'dateTime': f'{element["enddate"]}',
                            'timeZone': 'Europe/Paris',
                        },
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'popup', 'minutes': 10},
                            ],
                        },
                    }

                    if(element["type"] == "SOUTENANCE" or element["type"] == "EXAMEN"):
                        new_event["colorId"] = '9'
                    elif(element['type'] =='CONF'):
                        new_event['colorId'] = '8'
                except:
                    new_event = {
                        'summary': f'{element["infos"]}',
                        'transparency': trsp,
                        'colorId':'8',
                        'location': '',
                        'description': '',
                        'start': {
                            'dateTime': f'{element["startdate"]}',
                            'timeZone': 'Europe/Paris',
                        },
                        'end': {
                            'dateTime': f'{element["enddate"]}',
                            'timeZone': 'Europe/Paris',
                        },
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'popup', 'minutes': 10},
                            ],
                        },
                    }

                list_of_events_to_add.append(new_event)
        
        with open(RESULTSJSON_PATH, "w", encoding="utf-8") as res_file:
            json.dump(list_of_events_to_add, res_file)
        print(f"{bcolors.OKGREEN}Results are ready!{bcolors.ENDC}")
      
    def addRoomLinks(self):
        for elementmoche in (self.raw_EDT[day] for day in self.raw_EDT):
            for event in elementmoche:
                try:
                    if(event['prof'] == "BOUYER"):
                        event['link'] = "https://zoom.us/j/95848792822?pwd=dE51YitRYy9vakc2TElpVW5xM0xOQT09"
                    elif(event['prof'] == "DIDIER"):
                        event['link'] = "https://eu.bbcollab.com/guest/06bca9aa4cb240fcba7a535873f28e72\n Cours : https://drive.google.com/drive/folders/14QYFzUZMmGZQzdm4s4E3bT9zzHOeOyvv"
                    elif(event['prof'] == "BAILHE"):
                        event['link'] = "https://openmeetings-pedago.ensiie.fr/openmeetings/#room/89"
                    elif(event['prof'] == "DUBOIS"):
                        event['link'] = "https://openmeetings-pedago.ensiie.fr/openmeetings/#room/27"
                    elif(event['prof'][0:4] == "BABA"):
                        event['link'] = "https://zoom.us/j/4621066894?pwd=VGQvblUvOGdSRURGYlQraXN3elZZQT09"
                    elif(event['prof'] == "PIEDOT"):
                        event['link'] = "Zoom (mail)"
                    elif(event['prof'] == "JAROLIM"):
                        event['link'] = "https://openmeetings-pedago.ensiie.fr/openmeetings/#room/122"
                    elif(event['prof'] == "LIGOZAT"):
                        event['link'] = "https://openmeetings-pedago.ensiie.fr/openmeetings/#room/110 ou Zoom"
                    elif(event['prof'] == "GAIN"):
                        event['link'] = "https://openmeetings-pedago.ensiie.fr/openmeetings/#room/68"
                    elif(event['prof'] == "HUTZLER"):
                        event['link'] = "https://openmeetings-pedago.ensiie.fr/openmeetings/#room/131"
                    else:
                        event['link'] = ""
                except:
                    event['link'] = ""


    def close(self):
        print(f"\n\n----------\n{bcolors.WARNING}Closing browser...{bcolors.ENDC}")
        self.driver.close()

    def runAll(self):
        self.connect(user_name,passw)
        self.go_to_edt()
        self.get_html()
        self.get_courses()
        if(not(self.headless)):
            self.close()
        if(self.with_links):
            self.addRoomLinks()
        self.format_events()

#---------------------------------------
#---------------------------------------

class PostToGoogleCalendar():
    def __init__(self):
        if(gCal=="" or gCal=="xxx"):
            print(f"\n{bcolors.WARNING}Please add a gCal ID. Program closing...{bcolors.ENDC}")
            delete_tmp_files()
            sys.exit(0)
        self.calendarID = gCal
        self.creds = None

        if os.path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                SCOPES = ['https://www.googleapis.com/auth/calendar']
                flow = InstalledAppFlow.from_client_secrets_file(
                    r'./credentials/credentials.json', SCOPES)
                self.creds = flow.run_local_server()

            with open(r'./credentials/token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

        
    def delete_events(self,events):

        fromDate, toDate = '3970-01-01:T01:00:00', '1970-01-01:T01:00:00'
        for x, y in ((item['start']['dateTime'],item['end']['dateTime']) for item in events):
            fromDate, toDate = min(x, fromDate), max(y, toDate)
        fromDate = max(datetime.strptime(
            fromDate, '%Y-%m-%dT%H:%M:%S'), datetime.strptime(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), '%Y-%m-%dT%H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%S')

        offset1 = pytz.timezone(
            'Europe/Paris').localize(datetime.strptime(fromDate, '%Y-%m-%dT%H:%M:%S')).strftime('%z')
        offset2 = pytz.timezone(
            'Europe/Paris').localize(datetime.strptime(toDate, '%Y-%m-%dT%H:%M:%S')).strftime('%z')
        events = self.service.events().list(calendarId=self.calendarID,
                                            timeMax=f"{toDate}{offset1}", timeMin=f"{fromDate}{offset2}", timeZone='Europe/Paris').execute()['items']
        for event in events:
            if(event['start']['dateTime'] >= datetime.now().strftime('%Y-%m-%dT%H:%M:%S')):
                print(f"{bcolors.WARNING}Deleting : {event['summary']} starting {event['start']['dateTime']}{bcolors.ENDC}")
                self.service.events().delete(calendarId = self.calendarID, eventId=event['id']).execute()

    def get_events(self):
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=self.calendarID, timeMin=now,
                                                maxResults=500, singleEvents=True,
                                                orderBy='startTime').execute()
        return events_result.get('items', [])

    def upload_all_events(self, events_file):
        print(f"\n-----------------\n{bcolors.OKCYAN}Uploading all results...{bcolors.ENDC}")
        events = json.load(events_file)
        self.delete_events(events)
        print("\n-----------------")
        for event in events:
            if(event['start']['dateTime'] >= datetime.now().strftime('%Y-%m-%dT%H:%M:%S')):
                self.create_event(event)
        print(f"{bcolors.OKGREEN}\nAll events have been uploaded!{bcolors.ENDC}")

    def create_event(self, new_event):
        print(
            f"{bcolors.OKCYAN}Uploading event : {new_event['summary']} starting {new_event['start']['dateTime']}{bcolors.ENDC}")
        if not self.already_exists(new_event):
            event = self.service.events().insert(
                calendarId=self.calendarID, body=new_event).execute()
            return event.get('htmlLink')
            
        else:
            print(f'{bcolors.WARNING}\nEvent Already Exists{bcolors.ENDC}')
            #self.service.events().delete(calendarId=self.calendarID,eventId=event['id']).execute()
            return 'Event Already Exists'


    def already_exists(self, new_event):
        events = self.get_date_events(
            new_event['start']['dateTime'], self.get_events())
        event_list = [new_event['summary'] for new_event in events]
        if new_event['summary'] not in event_list:
            return False
        else:
            return True


    def get_date_events(self, date, events):
        lst = []
        date = date
        for event in events:
            if event.get('start').get('dateTime'):
                d1 = event['start']['dateTime']
                if d1 == date:
                    lst.append(event)
        return lst

#---------------------------------------
#---------------------------------------


class SaveToICS():

    def __init__(self, json_file,nb_semaines_futur):
        self.g_json = json.load(json_file)
        self.future = nb_semaines_futur

    def saveAllEvents(self):
        print(
            f"\n-----------------\n{bcolors.OKCYAN}Saving all events to ics file...{bcolors.ENDC}")
        cal = Calendar()
        for element in self.g_json:
            e = Event()
            fromOffset = pytz.timezone(
                    'Europe/Paris').localize(datetime.strptime(element['start']["dateTime"], '%Y-%m-%dT%H:%M:%S')).strftime('%z')
            toOffset = pytz.timezone(
                    'Europe/Paris').localize(datetime.strptime(element['end']["dateTime"], '%Y-%m-%dT%H:%M:%S')).strftime('%z')
            e.name = element['summary']
            e.begin = element['start']["dateTime"] + str(fromOffset)
            e.end = element['end']["dateTime"] + str(toOffset)
            e.transparent = element['transparency']

            try:
                e.location = element["location"]
                e.description = element['description']

            except:
                e.location = ""
                e.description = ""

            cal.events.add(e)
        if(self.future>0):
            bd = (datetime.now() + timedelta(weeks=self.future)).isocalendar()
        else:
            bd = datetime.now().isocalendar()

        base_week = bd[1]
        year = bd[0]
        RESULTSICS_PATH2 = RESULTSICS_PATH.split(
            ".ics")[0] + f"{year}_W{base_week}.ics"
        #print(repr(str(cal).replace('DTSTART', 'DTSTART;TZID=Europe/Paris').replace('DTEND', 'DTEND;TZID=Europe/Paris')))
        with open(RESULTSICS_PATH2, 'w') as f:
            f.write(str(cal).replace('DTSTART', 'DTSTART;TZID=Europe/Paris').replace('DTEND', 'DTEND;TZID=Europe/Paris'))
        
        print(
            f"{bcolors.OKGREEN}\nAll events have been saved to ics!{bcolors.ENDC}")

#---------------------------------------
# MAIN APP
#---------------------------------------
def delete_tmp_files():
    if os.path.exists(RAWRESULTSJSON_PATH):
        os.remove(RAWRESULTSJSON_PATH)
    else:
        pass
    if os.path.exists(RESULTSJSON_PATH) and not(keep_json):
        os.remove(RESULTSJSON_PATH)
    else:
        pass
    if(no_token and os.path.exists('./credentials/token.pickle')):
        os.remove('./credentials/token.pickle')

parser = argparse.ArgumentParser(prog='EDTExtractor',usage='%(prog)s [options]',description="Extracteur d'emploi du temps AurionWeb")
parser.add_argument('-ng', '--no-google', dest='google_mode',
                    action='store_false', help='do not upload events to google calendar')
parser.add_argument('-su', '--stop-upload', dest='auto_mode',
                    action='store_false', help='pauses the program before upload to google calendar. The file \"base_results.json\" can therefore be modified before upload')
parser.add_argument('-ics', '--ics', dest='save_to_ics',
                    action='store_true', help='saves events to an .ics file. Does not save auto reminders. Automatic when -ng is selected')
parser.add_argument('-w', '--week', dest='N', action='store',
                    default=0, help='fetches the schedule from N weeks in the future (0<=N<=10)')
parser.add_argument('-ui', '--user-interface', dest='is_headless',
                    action='store_false', help='opens the web browser during execution')
parser.add_argument('-b', '--busy', dest='asked_to_be_free',
                    action='store_false', help='set availability to "busy" in all events')
parser.add_argument('-l', '--links', dest='is_links',
                    action='store_true', help='adds Zoom/BbCollab/Openmeetings links to calendar events description (incomplete)')
parser.add_argument('-k', '--keep-json', dest='keep_json',
                    action='store_true', help='keeps generated json file \"base_results.json\" after program terminates')
parser.add_argument('-v', '--verbose', dest='verb',
                    action='store_true', help='verbose mode. Shows selenium log infos')
parser.add_argument('-nt', '--no-token', dest='token',
                    action='store_true', help='prevent the Google Oauth token to be saved for future uses')
parser.add_argument('--update', dest='want_update',
                    action='store_true', help='saves current version main .py files in the folder previous_version and updates the program to the latest version')
parser.add_argument('-mu','--manual-update', dest='manual_update',
                    action='store_true', help='to use if you want to manually install an update (no fetch through url)')


py_args = parser.parse_args()

asked_to_be_free = py_args.asked_to_be_free
is_headless = py_args.is_headless
auto_mode = py_args.auto_mode

NB_SEMAINES_FUTUR = min(max(0,int(py_args.N)),10)
keep_json = py_args.keep_json
with_links = py_args.is_links
google_mode = py_args.google_mode
save_ics = py_args.save_to_ics
verbose = py_args.verb
no_token = py_args.token


#--------------------------------------------------------------------
if(py_args.want_update):
    from update import auto_update, manual_update
    if(not(py_args.manual_update)):
        auto_update()
    else:
        manual_update()

    print(f"\n{bcolors.WARNING}Program closing... Please restart program to use lastest version{bcolors.ENDC}")
    sys.exit(0)
#--------------------------------------------------------------------

edtApp = EDTExtr(is_headless, asked_to_be_free,with_links,verbose)
edtApp.runAll()

if(not(google_mode)):
    save_ics = True

if(save_ics):
    with open(RESULTSJSON_PATH, "r", encoding="utf-8") as json_file:
        saver = SaveToICS(json_file, NB_SEMAINES_FUTUR)
        saver.saveAllEvents()

if(google_mode):
    if(auto_mode):
        print(f'{bcolors.OKGREEN}\nAuto uploading results to Google Calendar...{bcolors.ENDC}')
    else:
        print("Appuyez q pour quitter. Appuyez sur une touche pour uploader les résultats sur le calendrier Google")

    if(auto_mode or keyboard.read_key() != "q"):
        googleUploader = PostToGoogleCalendar()
        with open(RESULTSJSON_PATH, "r", encoding="utf-8") as json_file:
            googleUploader.upload_all_events(json_file)
print(f"\n{bcolors.WARNING}Program closing...{bcolors.ENDC}")
delete_tmp_files()
