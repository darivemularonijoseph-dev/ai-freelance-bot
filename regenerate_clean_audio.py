"""
Clean Audio Re-renderer
Eliminates any raw XML/SSML tag leakage and uses natural punctuation (commas, ellipsis)
for authentic human conversational cadence.
"""

import asyncio
import os
import edge_tts

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "voice_agent", "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

CLEAN_CLIPS = [
    {
        "file": "realestate_greeting_shruti_v2.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "-4%",
        "text": "హలో సార్, గుడ్ మార్నింగ్ అండి! ... నేను శృతి ని, ఆటోమేట్ హైదరాబాద్ నుంచి కాల్ చేస్తున్నానండి. ... రీసెంట్ గా మీరు గచ్చిబౌలి మరియు ఫైనాన్షియల్ డిస్ట్రిక్ట్ దగ్గర గేటెడ్ కమ్యూనిటీ అపార్ట్\u200cమెంట్స్ గురించి చూస్తున్నారు కదా సర్? ... దాని గురించే ఒక బెస్ట్ ప్రాజెక్ట్ డీటెయిల్స్ షేర్ చేద్దామని కాల్ చేశాను అండి. ... మీ బడ్జెట్ మరియు రిక్వైర్మెంట్స్ కొంచెం చెప్తారా సర్?"
    },
    {
        "file": "realestate_greeting_mohan_v2.mp3",
        "voice": "te-IN-MohanNeural",
        "rate": "-4%",
        "text": "నమస్కారం అండి! ... నేను మోహన్, ఆటోమేట్ హైదరాబాద్ రియల్ ఎస్టేట్ అడ్వైజర్\u200cని. ... గచ్చిబౌలి, నార్సింగి మరియు తెల్లాపూర్ మెయిన్ ఏరియాల్లో, బెస్ట్ లగ్జరీ గేటెడ్ కమ్యూనిటీ ప్రాజెక్ట్స్ గురించి మీకు గైడ్ చేద్దామని కాల్ చేశాను అండి. ... ప్రస్తుతం మీరు 2BHK కోసం చూస్తున్నారా, లేదా 3BHK కోసమా అండి సర్?"
    },
    {
        "file": "realestate_budget_3bhk_shruti_v2.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "-4%",
        "text": "తప్పకుండా అండి! ... గచ్చిబౌలి మరియు తెల్లాపూర్ మెయిన్ రోడ్ దగ్గర, మా దగ్గర 1.5 కోట్ల నుంచి 2.2 కోట్ల రేంజ్ లో సూపర్బ్ 3BHK ఫ్లాట్స్ ఉన్నాయండి. ... ఇందులో 100% వాస్తు కంప్లైంట్ తో పాటు, 50,000 స్క్వేర్ ఫీట్ గ్రాండ్ క్లబ్\u200cహౌస్, స్విమ్మింగ్ పూల్, జిమ్ మరియు 40కి పైగా వరల్డ్ క్లాస్ అమెనిటీస్ ఉన్నాయండి సర్."
    },
    {
        "file": "realestate_amenities_shruti_v2.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "-4%",
        "text": "అమెనిటీస్ గురించి చెప్పాలంటే అండి, ... ఇందులో గ్రాండ్ 50 వేల స్క్వేర్ ఫీట్ క్లబ్\u200cహౌస్ తో పాటు, టెంపరేచర్ కంట్రోల్డ్ స్విమ్మింగ్ పూల్, బ్యాడ్మింటన్ కోర్ట్స్, జిమ్ మరియు జాగింగ్ ట్రాక్ ఉన్నాయి. ... పిల్లల కోసం సపరేట్ ప్లే ఏరియా, మరియు సీనియర్ సిటిజన్స్ పార్క్ కూడా ప్లాన్ చేశారండి. ... 24/7 త్రీ-టైర్ సెక్యూరిటీ మరియు 100% పవర్ బ్యాకప్ కూడా ఉంటుంది సర్!"
    },
    {
        "file": "realestate_sitevisit_shruti_v2.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "-4%",
        "text": "చాలా సంతోషం అండి! ... ఈ శనివారం ఉదయం 11 గంటలకు గానీ, లేదా సాయంత్రం 4 గంటలకు గానీ మీకు వీలవుతుందా అండి? ... మీరు టైమ్ చెప్తే, మా సీనియర్ మేనేజర్ మీకు మోడల్ ఫ్లాట్ ని స్వయంగా చూపిస్తారు. ... అవసరమైతే మీ ఇంటి దగ్గర నుంచి క్యాబ్ పికప్ కూడా మేమే అరేంజ్ చేస్తాము సర్!"
    },
    {
        "file": "realestate_whatsapp_shruti_v2.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "-4%",
        "text": "తప్పకుండా అండి! ... ప్రాజెక్ట్ బ్రోచర్, ఫ్లోర్ ప్లాన్స్, మాస్టర్ లేఅవుట్ మరియు కంప్లీట్ ప్రైసింగ్ షీట్, ఇప్పుడే మీ వాట్సాప్ నంబర్ కి సెండ్ చేస్తున్నానండి. ... మీరు ఒకసారి చూసి, మీ కన్వీనియంట్ టైమ్ చెప్తే ఫర్దర్ గా మాట్లాడదాం సర్."
    },
    {
        "file": "realestate_bankloan_shruti_v2.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "-4%",
        "text": "అవునండి సర్! ... ఈ ప్రాజెక్ట్ SBI, HDFC మరియు ICICI బ్యాంకుల ద్వారా 100% రెరా అప్రూవ్డ్ అండి. ... మీకు 80% వరకు హోమ్ లోన్ అసిస్టెన్స్ తో పాటు, అతి తక్కువ వడ్డీ రేట్లతో ఈజీ EMI ఆప్షన్స్ కూడా కల్పిస్తాము అండి."
    },
    {
        "file": "realestate_greeting_english_v2.mp3",
        "voice": "en-IN-NeerjaExpressiveNeural",
        "rate": "-3%",
        "text": "Hello sir, good morning! ... This is Shruti calling from AutomateHyd Real Estate Advisory. ... You recently enquired about premium gated community apartments near Gachibowli, right sir? ... Calling to share details of our brand new luxury project. ... Are you looking for 2 BHK or 3 BHK sir?"
    }
]

async def regenerate():
    print(f"Regenerating {len(CLEAN_CLIPS)} clean audio files without any XML tags...")
    for idx, item in enumerate(CLEAN_CLIPS, 1):
        target = os.path.join(AUDIO_DIR, item["file"])
        print(f"[{idx}/{len(CLEAN_CLIPS)}] Synthesizing clean: {item['file']} ({item['voice']})...")
        comm = edge_tts.Communicate(item["text"], item["voice"], rate=item["rate"])
        await comm.save(target)
        print(f"  -> Saved {target} ({os.path.getsize(target)} bytes)")
    print("\n[SUCCESS] All audio files cleanly regenerated with zero markup leakage!")

if __name__ == "__main__":
    asyncio.run(regenerate())
