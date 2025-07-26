# Offical_PF_Code
Paperfrenzy codebase raw full website regularly updated to reflect changes


CBSE_DOWNLOADER.py is a bot for downloading cbse papers still under dev

downloader.py is a full blown downloader that scrapes from papacambridge all the cambridge related to papers for hosting

inside paperfrenzy-proj folder

code.txt - is the security code for google cloud database i removed it for this commit for security

creds.json - is the very important authetication file for google cloud database too again removed the credentials for security

Procfile - is a file used during hosting of website it helps heroku identify the wsgi file for hosting which is essential

db.sqlite3 - old database used during dev its mainly an artifact from the past

manage.py - django manage file is crucial during dev allows to execute some commands 

requirements.txt - is a file showing all requirements and dependencies our project uses to run

runtime.txt - shows python version required for hosting

INSIDE APP FOLDER

app is the most important folder and contains 80% of the code this is where the shit really happens

models.py - all database fields used in admin and even some backend things basically all the fields that can be entered in database

admin.py - shows which of these is displayed in admin

middleware.py - security file that does not allow a certain pdf file injection malware hack on pdf view for papers

apps.py - general boilderplate file to show this folder exists to settings.py (will come here later)

tests.py - boilderplate file generally used for tests i dint really use it

views.py - THE CREAM AND BUTTER THE MOST IMPORTANT FILE ARGUEBALLY contains most of the brains of our product (python backend)

apu.py - bot uploading script for cambridge

cbseabu.py - bot uploading script for cbse

cbsems.py - bot uploading script for cbse marking schemes

log.txt - a remenant uneeded file that was temporarily generated to test uploads by bot


Inside templates folder

this folder contains all the html of our website

index.html - homepage html

ALevels.html - heavily under construction page for ALevels papers list

Alevelsinsert.html - insert display on seperate window

Alevelsview.html - Alevels paper viewer page

av12.html - class 12 papers viewing page

aviewer.html - class 10 papers viewing page (when i say viewing i mean when we open the paper to that tab where it shows pdf)

blog.html - under construction blog page

error.html - a remenant 404 page from the past maybe will be used in future

feedback.html - the contact us page

igcse.html - igcse paper list page

igcseinsert.html - the page that opens igcse inserts in new tab

igcsems.html - the page that opens igcse ms in new tab

igcseview.html - the page that allows u to view the igcse papers

jee.html - old jee paper list relic will maybe not be used anytime in future for a fresh alternative

jeeview.html - jee paper viewer again relic

ms.html - opens class 10 cbse marking scheme papers new tab

ms12.html - opens class 12 cbse marking scheme papers new tab

msjee.html - relic from past jee new ms tab

questionai.html - old relic of questionai which used to exist between around (janaury 2025? - april 2025?)

resourcerepo.html - a link redirect page for resourcerepo guys you know the discord server i planned on partnering us with

samplems.html - opens class 10 sample ms papers new tab

subjects_10_sample.html - sample papers class 10 list

subjects_10.html - class 10 paper list page

subject_ 12.html - class 12 paper list page



PAPERFRENZY FOLDER INSIDE

this folder contains some boilderplate but some vital files

___init___.py - useless file created during project creation

asgi.py - used for sockets (networking for like multiplayer games like warthunder for example) not useful in our project just boilerplate

urls.py - all urls that are on our website incudling the ones that are not seeable and backend related

seetings.py - very important file having most of hosting and databse setings linked

wsgi.py - a file used for hosting used by Procfile

gcloud.py - a file containing important credentials again for google cloud storage



--- all the available files on paperfrenzy github repo here --

