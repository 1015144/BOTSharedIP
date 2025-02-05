import pywikibot
import json
import pywikibot.page
import requests
from html.parser import HTMLParser

sf = ["school", "college", "learn", "district", "university", "intermediate unit", "escuela"]
corpf = ["electric", "plumb", "corporation", "llc", " inc", "corp", "consult", "agency", "group", "finance"]
corpexclude = ["verizon", "tele", "phone", "internet", "com", "network", "bell", "at&t", "broad", "psinet", "spacex services, inc", "hurricane electric", "cable", "zayo", "cogeco", "iboss", "arvig", "crown castle fiber llc", "wireless", "service provider", "fiber", "wideopenwest"]
govf = ["city", "government", "state", "province", "department", "county", "town", "agency", "division"]

alreadyflagged = ["{shared ip", "{sharedip", "{schoolip", "{anonblock", "{whois"]

unflagged = []

def user_checks(ip, type, check):
    y = requests.get(f"https://en.wikipedia.org/w/index.php?title=User_talk:{ip}&action=edit")
    flagged = not any(elem in y.text.lower() for elem in alreadyflagged)
    
    c = requests.get(f"https://en.wikipedia.org/wiki/Special:Contributions/{ip}")
    bad_user = c.text.lower().find('<span class="mw-tag-marker mw-tag-marker-mw-reverted">reverted</span>')

    t = requests.get(f"https://en.wikipedia.org/w/index.php?title=User_talk:{ip}&action=raw")
    warned = not (t.status_code == 404)
    if bad_user != -1 and warned and flagged:
        unflagged.append([ip, check, f"https://en.wikipedia.org/wiki/Special:Contributions/{ip}"])
        print(unflagged)

def get_ip_data(ip):
    x = requests.get(f"https://whois-referral.toolforge.org/gateway.py?lookup=true&ip={ip}&format=json")

    idata = json.loads(x.text)
    try:
        check1 = idata["nets"][0]["description"].lower()
    except AttributeError:
        check1 = "0"
    except KeyError:
        check1 = "0"
    try:
        check2 = idata["nets"][1]["description"].lower()
    except:
        check2 = "0"
    
    print(ip, check1, check2)
    #EDU
    if any(elem in check1 for elem in sf):
        user_checks(ip, "edu", check1)
    elif any(elem in check2 for elem in sf):
        user_checks(ip, "edu", check2)
    ##CORP
    elif any(elem in check1 for elem in corpf) and not (any(elem in check1 for elem in corpexclude)):
        user_checks(ip, "corp", check1)
    elif any(elem in check2 for elem in corpf) and not (any(elem in check2 for elem in corpexclude)):
        user_checks(ip, "corp", check2)
    #GOV
    elif any(elem in check1 for elem in govf) and not (any(elem in check1 for elem in corpexclude)):
        user_checks(ip, "gov", check1)
    elif any(elem in check2 for elem in govf) and not (any(elem in check2 for elem in corpexclude)):
        user_checks(ip, "gov", check2)

u = requests.get(f"https://en.wikipedia.org/w/index.php?damaging=likelybad%3Bverylikelybad&goodfaith=likelybad%3Bverylikelybad&userExpLevel=unregistered&hidebots=1&hidecategorization=1&hideWikibase=1&hidenewuserlog=1&limit=500&days=7&title=Special:RecentChanges&urlversion=2")

from html.parser import HTMLParser
from html.entities import name2codepoint

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == "href" and attr[1].startswith("/wiki/Special:Contributions/"):
                ipa = attr[1].replace("/wiki/Special:Contributions/", "")
                get_ip_data(ipa)
parser = MyHTMLParser()
try:
    parser.feed(u.text)
except:
    print("Session done (or failed)")
print(unflagged)
