import os, time, random, requests
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN= "EAAkNirG9R4ABSvSCLyZAae4Clr6kpYgLhMDuwZAzCa11qhH3F5y0GfMGrF1c1Dmvq7byzcxGDrXfIin5bRhCW1525oeIwOxINCZBHPYZCWKndydBQGn9iYN7Db3PfpX7QfVeIwC40twd2GZAqDy7UuWuf0LHhKLhQP6CUjMnHnZAxVUrA7wDyitCl7XRZCJkqqjp8zrFaTBJr7y4s39TrIcXcgFluQAvBIci9BYvkrNRhZB4"
IG_USER_ID= "17841423698399102"
BASE = "https://graph.facebook.com/v21.0"

def log(t): print(f"[BOT] {t}")

# --- BIAS FILTER: Unaamua comment gani ijibiwe ---
POSITIVE_WORDS = ["poa","kali","safi","moto","🔥","❤️","nice","love","bomb"]
NEGATIVE_WORDS = ["mbaya","upuzi","fake"]


def check_me():
    url = f"{BASE}/me"
    r = requests.get(url, params={"fields":"id,username", "access_token": "ACCESS_TOKEN"}).json()
    print(r) #ita-print jibu lote
    log(f"Logged as @{r.get('username')}")
    return r

def should_reply(text):
    text = text.lower()
    # 1. Usijibu kama ni matusi
    if any(w in text for w in NEGATIVE_WORDS):
        return False, "skip_negative"
    # 2. Jibu tu kama kuna positive au swali
    if any(w in text for w in POSITIVE_WORDS) or "?" in text or len(text) > 10:
        return True, "positive"
    return False, "neutral"

def get_comments(media_id):
    r = requests.get(f"{BASE}/{media_id}/comments", params={
        "fields":"id,text,username","limit":100,"access_token":ACCESS_TOKEN
    }).json()
    return r.get("data", [])

def reply_comment(comment_id, msg):
    return requests.post(f"{BASE}/{comment_id}/replies", data={
        "message": msg, "access_token": ACCESS_TOKEN
    }).json()

def comment_on_post(media_id, msg):
    return requests.post(f"{BASE}/{media_id}/comments", data={
        "message": msg, "access_token": ACCESS_TOKEN
    }).json()

def post_media(public_url, caption, is_reel=False):
    data = {"caption": caption, "access_token": ACCESS_TOKEN}
    if is_reel:
        data.update({"media_type":"REELS","video_url":public_url})
    else:
        data.update({"image_url":public_url})

    container = requests.post(f"{BASE}/{IG_USER_ID}/media", data=data).json()
    if "id" not in container:
        log(f"Container error: {container}")
        return container
    log(f"Container {container['id']} created, wait 10s...")
    time.sleep(10)
    publish = requests.post(f"{BASE}/{IG_USER_ID}/media_publish", data={
        "creation_id": container["id"], "access_token": ACCESS_TOKEN
    }).json()
    log(f"Posted: {publish}")
    return publish

def smart_reply_my_post(media_id):
    comments = get_comments(media_id)
    log(f"Nimekuta comments {len(comments)} kwenye post {media_id}")
    for c in comments:
        ok, reason = should_reply(c["text"])
        if ok:
            msg = f"@{c['username']} Asante mkuu! 🙏🔥"
            reply_comment(c["id"], msg)
            log(f"✅ Nimemjibu {c['username']} ({reason})")
            time.sleep(random.randint(8,15))
        else:
            log(f"⏭️ Nimeruka {c['username']}: {c['text'][:20]} ({reason})")

# --- HASHTAG HUNTER ---
def hunt_and_comment(hashtag, comment_text, limit=5):
    log(f"Searching #{hashtag}")
    hs = requests.get(f"{BASE}/ig_hashtag_search", params={
        "user_id": IG_USER_ID, "q": hashtag, "access_token": ACCESS_TOKEN
    }).json()
    if not hs.get("data"): return log("Hashtag not found")
    hid = hs["data"][0]["id"]
    recent = requests.get(f"{BASE}/{hid}/recent_media", params={
        "user_id": IG_USER_ID, "fields":"id,permalink","limit":limit,"access_token":ACCESS_TOKEN
    }).json()
    for p in recent.get("data",[]):
        log(f"Commenting on {p['permalink']}")
        print(comment_on_post(p["id"], comment_text))
        time.sleep(random.randint(20,40))

if __name__ == "__main__":
   check_me()
    # MFANO 1: Jibu kwa akili post yako ya mwisho
    # smart_reply_my_post("1800000000000000") # weka ID ya post yako

    # MFANO 2: Comment kwa watu wa hashtag
    # hunt_and_comment("tanzania", "Content kali mkuu 🔥")

    # MFANO 3: Post
    # post_media("https://i.imgur.com/8Km9tLL.png", "PopJVC BOT LIVE 🚀")


