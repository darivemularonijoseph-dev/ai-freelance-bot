"""
Generate High-Fidelity Pre-Rendered Telugu Audio Clips using Edge-TTS Neural Models.
Provides 0ms latency playback for core demo scenarios on mobile devices.
"""

import asyncio
import os
import edge_tts

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "voice_agent", "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SCRIPTS = [
    # --- REAL ESTATE SCENARIOS (Shruti & Mohan) ---
    {
        "filename": "realestate_greeting_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "నమస్కారం అండి! ఆటోమేట్ హైదరాబాద్ రియల్ ఎస్టేట్ పార్ట్నర్ నుంచి శృతి మాట్లాడుతున్నాను. మీరు రీసెంట్\u200cగా గచ్చిబౌలి మరియు ఫైనాన్షియల్ డిస్ట్రిక్ట్ దగ్గర లగ్జరీ 3BHK గేటెడ్ కమ్యూనిటీ ప్రాజెక్ట్స్ గురించి విచారించారు కదా? మీ బడ్జెట్ మరియు రిక్వైర్మెంట్స్ చెబితే, ది బెస్ట్ ప్రాజెక్ట్ డీటెయిల్స్ షేర్ చేస్తాను అండి."
    },
    {
        "filename": "realestate_greeting_mohan.mp3",
        "voice": "te-IN-MohanNeural",
        "rate": "+2%",
        "text": "నమస్కారం అండి! నేను మోహన్, ఆటోమేట్ హైదరాబాద్ రియల్ ఎస్టేట్ అడ్వైజర్\u200cని. గచ్చిబౌలి, నార్సింగి మరియు తెల్లాపూర్ లొకేషన్లలో బెస్ట్ గేటెడ్ కమ్యూనిటీ అపార్ట్\u200cమెంట్స్ గురించి మీకు గైడ్ చేయడానికి కాల్ చేశాను. మీరు 2BHK కోసం చూస్తున్నారా లేదా 3BHK కోసమా అండి?"
    },
    {
        "filename": "realestate_budget_3bhk_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "ఖచ్చితంగా అండి! గచ్చిబౌలి మరియు తెల్లాపూర్ పరిసరాల్లో మా దగ్గర 1.5 కోట్ల నుంచి 2.2 కోట్ల రేంజ్\u200cలో ప్రీమియం 3BHK గేటెడ్ కమ్యూనిటీ ఫ్లాట్స్ అందుబాటులో ఉన్నాయి. 100% వాస్తు కంప్లైంట్, 50 వేల స్క్వేర్ ఫీట్ గ్రాండ్ క్లబ్\u200cహౌస్ మరియు 40కి పైగా వరల్డ్ క్లాస్ అమెనిటీస్ ఉన్నాయి అండి."
    },
    {
        "filename": "realestate_amenities_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "అమెనిటీస్ గురించి చెప్పాలంటే అండి, ఇందులో టెంపరేచర్ కంట్రోల్డ్ స్విమ్మింగ్ పూల్, బ్యాడ్మింటన్ కోర్ట్, జిమ్, జాగింగ్ ట్రాక్, చిల్డ్రన్స్ ప్లే ఏరియా, మరియు సీనియర్ సిటిజన్స్ పార్క్ ఉన్నాయి. అలాగే 24/7 త్రీ-టైర్ సెక్యూరిటీ మరియు 100% పవర్ బ్యాకప్ కూడా ఉంది అండి."
    },
    {
        "filename": "realestate_sitevisit_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "చాలా సంతోషం అండి! ఈ శనివారం ఉదయం 11 గంటలకు లేదా ఆదివారం సాయంత్రం 4 గంటలకు మీకు సైట్ విజిట్ కన్వీనియంట్ గా ఉంటుందా అండి? మా సీనియర్ రిలేషన్షిప్ మేనేజర్ మీకు మోడల్ ఫ్లాట్ ని స్వయంగా చూపిస్తారు. మీరు చెబితే క్యాబ్ పికప్ కూడా ప్లాన్ చేస్తాము అండి!"
    },
    {
        "filename": "realestate_whatsapp_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "తప్పకుండా అండి! మీ నంబర్ కి ప్రాజెక్ట్ బ్రోచర్, ఫ్లోర్ ప్లాన్స్, మాస్టర్ లేఅవుట్ మరియు ప్రైసింగ్ షీట్ ఇప్పుడే వాట్సాప్\u200cలో షేర్ చేశాను. దయచేసి ఒక్కసారి చెక్ చేసి మీ అభిప్రాయం చెప్పండి అండి."
    },
    {
        "filename": "realestate_bankloan_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "అవును అండి, ఈ ప్రాజెక్ట్ HDFC, SBI మరియు ICICI బ్యాంకుల ద్వారా 100% రెరా అప్రూవ్డ్. మీకు 80% వరకు హోమ్ లోన్ అసిస్టెన్స్ మరియు తక్కువ వడ్డీ రేట్లతో ఈజీ EMI ఆప్షన్స్ కూడా అందుబాటులో ఉన్నాయి అండి."
    },
    {
        "filename": "realestate_callback_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "థాంక్యూ అండి! మీ రిక్వైర్మెంట్ నోట్ చేసుకున్నాను. మీ వివరాలు మా సీనియర్ ప్రాపర్టీ కన్సల్టెంట్ కి అసైన్ చేశాము. మరికొద్ది సేపట్లో వారు మీకు పర్సనల్ గా కాల్ చేసి మరింత సమాచారం అందిస్తారు. హావ్ ఏ గ్రేట్ డే అండి!"
    },
    # --- HEALTHCARE / CLINIC SCENARIO ---
    {
        "filename": "clinic_greeting_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "నమస్కారం అండి! హైదరాబాద్ కేర్ క్లినిక్ నుంచి శృతి మాట్లాడుతున్నాను. మీరు డాక్టర్ అపాయింట్మెంట్ లేదా హెల్త్ చెకప్ గురించి విచారించారు కదా? నేను మీకు ఎలా సహాయపడగలను అండి?"
    },
    {
        "filename": "clinic_appointment_shruti.mp3",
        "voice": "te-IN-ShrutiNeural",
        "rate": "+2%",
        "text": "ఖచ్చితంగా అండి! రేపు సాయంత్రం 5:30 లేదా 6:30 కి డాక్టర్ గారి స్లాట్ అవైలబుల్ గా ఉంది. మీ అపాయింట్మెంట్ బుక్ చేసి కన్ఫర్మేషన్ మెసేజ్ మరియు లొకేషన్ మీ వాట్సాప్ కి పంపించమంటారా అండి?"
    }
]

async def generate_all():
    print(f"Generating {len(SCRIPTS)} Telugu neural audio clips into {AUDIO_DIR}...")
    for idx, item in enumerate(SCRIPTS, 1):
        target = os.path.join(AUDIO_DIR, item["filename"])
        if os.path.exists(target) and os.path.getsize(target) > 5000:
            print(f"[{idx}/{len(SCRIPTS)}] Already exists: {item['filename']}")
            continue
        print(f"[{idx}/{len(SCRIPTS)}] Synthesizing: {item['filename']} with {item['voice']}...")
        comm = edge_tts.Communicate(item["text"], item["voice"], rate=item["rate"])
        await comm.save(target)
        print(f"  -> Done! Size: {os.path.getsize(target)} bytes")
    print("\n[SUCCESS] All audio clips ready for 0ms latency mobile playback!")

if __name__ == "__main__":
    asyncio.run(generate_all())
