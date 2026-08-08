import os
import json
import glob
import random
import requests
import shutil
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Import upload functions (YouTube only)
try:
    from upload.upload_to_youtube import upload_to_youtube
except ImportError as e:
    print(f"Error importing upload modules: {e}")
    # Still want to proceed or stop?
    pass

PROCESSED_DIR = "Processed_Videos"
PUBLISHED_LOG = "published_videos.json"

def get_already_published():
    if os.path.exists(PUBLISHED_LOG):
        with open(PUBLISHED_LOG, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def get_repost_counts():
    """Count how many times each video has been posted."""
    published = get_already_published()
    counts = {}
    for entry in published:
        vname = entry.get("video_name", "")
        counts[vname] = counts.get(vname, 0) + 1
    return counts

def mark_as_published(video_name, metadata):
    published = get_already_published()
    published.append({
        "video_name": video_name,
        "metadata": metadata
    })
    with open(PUBLISHED_LOG, 'w', encoding='utf-8') as f:
        json.dump(published, f, indent=4)

def select_video(specific_video=None):
    published = [item["video_name"] for item in get_already_published()]
    all_videos = sorted(glob.glob(os.path.join(PROCESSED_DIR, "*.mp4")))

    if specific_video:
        # specific_video might be a full path or just a filename
        if os.path.exists(specific_video):
            # It's a full path
            vid_path = specific_video
            name = os.path.basename(specific_video)
        else:
            # It's just a filename, join with PROCESSED_DIR
            vid_path = os.path.join(PROCESSED_DIR, specific_video)
            name = specific_video

        if os.path.exists(vid_path):
            if name in published:
                post_count = sum(1 for p in published if p == name)
                print(f"🔄 Video {name} was already published ({post_count}x) - Re-publishing (recycling)")
            return vid_path, name
        else:
            print(f"❌ Error: Specific video {name} not found")
            return None, None

    # Find unpublished videos first
    unpublished = [(vid, os.path.basename(vid)) for vid in all_videos if os.path.basename(vid) not in published]

    if unpublished:
        vid, name = unpublished[0]
        return vid, name

    # All videos published - use weighted random selection (less posted = more likely)
    if all_videos:
        repost_counts = get_repost_counts()
        weights = []
        for vid in all_videos:
            name = os.path.basename(vid)
            count = repost_counts.get(name, 0)
            weight = max(1, 1000 // (3 ** min(count, 6)))
            weights.append(weight)

        selected_vid = random.choices(all_videos, weights=weights, k=1)[0]
        name = os.path.basename(selected_vid)
        post_count = repost_counts.get(name, 0)
        print(f"🎲 All videos published. Weighted random reuse (posted {post_count}x): {name}")
        return selected_vid, name

    return None, None

def generate_caption():
    import random
    import time

    api_key = os.getenv("POLLINATIONS_API_KEY")
    model = os.getenv("AI_MODEL", "openai")

    fallback_titles = [
        "The Art of Letting Go — A Buddhist Perspective",
        "Why Attachment Is the Root of Suffering",
        "The Power of Silence — Lessons From Zen Monks",
        "What Buddhism Teaches Us About Happiness",
        "The Illusion of Control — A Zen Lesson",
        "How to Find Peace in a Chaotic World",
        "The Wisdom of Impermanence — Nothing Lasts Forever",
        "Why Your Mind Creates Your Suffering",
        "The Middle Path — Balance in Everything",
        "Meditation Is Not What You Think",
        "The Monk's Guide to Dealing With Anger",
        "Why We Chase Pleasure and Still Feel Empty",
        "The Four Noble Truths — The Heart of Buddhism",
        "How to Train Your Mind Like a Zen Monk",
        "Non-Attachment Doesn't Mean You Don't Care",
    ]

    fallback_descriptions = [
        "Letting go is not losing — it's the first step to true freedom. In Buddhist philosophy, attachment is the root of all suffering. The more we cling to people, outcomes, and identities, the more we suffer when they change. And everything changes. Learning to release with love is one of the most powerful practices you can cultivate. Like if this wisdom spoke to your soul today. 🙏 #buddhism #lettinggo #attachment #zen #mindfulness #wisdom #innerpeace #philosophy #lifelessons #spirituality #monk #detachment",
        "The Buddha said desire is the root of suffering. But what does that really mean? It doesn't mean you can't want things. It means your peace should not depend on getting them. When you attach your happiness to outcomes, you give your power away. True freedom comes from enjoying the journey without being chained to the destination. Drop a 🪷 if this resonates with you.",
        "In silence, you find what the noise hides. Zen monks spend years in silence not because they have nothing to say, but because they've discovered something deeper. Silence isn't empty — it's full of presence. Try sitting in silence for just 10 minutes today. No phone, no music, no distraction. Just you and your breath. That space is where real wisdom lives. Share this with someone who needs peace. 🧘 #zen #silence #meditation #mindfulness #buddhism #innerpeace #monk #wisdom",
        "Happiness is not something to chase — it's something to realize. Buddhist wisdom teaches that happiness isn't found in getting more, but in wanting less. When you stop measuring life by achievements and start experiencing it with presence, everything changes. The happiest people aren't the ones who have the most — they're the ones who need the least. Like if you agree. ☸️ #buddhism #happiness #zen #mindfulness #wisdom #simpleliving #contentment #philosophy #lifelessons",
        "You can't control the wind, but you can adjust your sails. So much of our suffering comes from trying to control what can't be controlled. Other people, the future, how things turn out. A Zen monk learns to focus only on what's within their power — their response, their attitude, their presence right now. Everything else is a lesson in letting go. Comment what you're learning to let go of. 🌬️ #buddhism #zen #control #lettinggo #wisdom #mindfulness #acceptance #innerpeace",
        "Peace doesn't require a perfect life — it requires a calm mind. You can be in the middle of chaos and still find stillness within. That's the practice. That's the path. Monks train for years to stay centered no matter what happens around them. The good news? You can start today. One breath at a time. Double tap if you're working on finding your inner peace. 🕊️ #peace #zen #buddhism #mindfulness #innerpeace #calm #meditation #wisdom",
        "Everything changes. That's not a tragedy — it's a revelation. Impermanence (anicca) is one of the core teachings of Buddhism. The fact that nothing lasts forever is what makes every moment precious. The flower blooms, then wilts. The sun rises, then sets. And you too are constantly changing. Don't fight it. Flow with it. Like if this perspective shifts something in you. 🌸 #impermanence #buddhism #zen #mindfulness #change #wisdom #lifelessons #presence",
        "Your mind creates stories, and then you suffer from them. Someone doesn't text back — your mind creates a story. A plan falls through — your mind creates another story. Buddhism calls this the 'monkey mind.' The practice is to see the story for what it is — just a thought, not the truth. When you stop believing every thought, you stop creating unnecessary suffering. 🐒 #buddhism #mindfulness #zen #overthinking #monkeymind #wisdom #meditation #mentalhealth",
        "The Middle Path — not too tight, not too loose. The Buddha taught that the path to wisdom lies in avoiding extremes. Not indulgence, not asceticism. Not clinging, not rejecting. Balance in all things. This is the way of the wise. Whether it's work, relationships, or your spiritual practice, find the middle way. Save this as a reminder to stay balanced. ⚖️ #buddhism #middlepath #zen #wisdom #balance #mindfulness #philosophy #lifelessons",
        "Meditation isn't about emptying your mind. That's a common misconception. It's about sitting with what is, without judgment. Thoughts will come. Let them. Feelings will arise. Let them. The practice is not to stop thinking — it's to stop being controlled by your thoughts. Even 5 minutes a day changes everything. Drop a 🧘 if you meditate.",
        "Anger is like holding a hot coal expecting someone else to get burned. Buddhist wisdom teaches that anger destroys the one who holds it first. The monk's approach is not to suppress anger, but to understand its root. Watch it arise. See its impermanence. Let it pass without acting on it. This is true strength. Like if you're learning to master your emotions. 🔥 #buddhism #anger #zen #mindfulness #emotionalintelligence #wisdom #monk #innerpeace",
        "You can get everything you want and still feel empty. Why? Because desire is an endless cycle. You get the thing, you want the next thing. The Buddha called this samsara — the endless wheel of craving. The way out isn't getting more — it's understanding the nature of desire itself. Real fulfillment comes from within. Share this with someone chasing happiness in all the wrong places. 🔄 #buddhism #desire #zen #mindfulness #contentment #wisdom #philosophy",
        "The Four Noble Truths are the foundation of all Buddhist teaching. First: life involves suffering. Second: suffering is caused by craving and attachment. Third: it is possible to end suffering. Fourth: the Eightfold Path shows the way. This isn't pessimistic — it's profoundly hopeful. It says you are not condemned to suffer forever. There is a way out. And it starts with understanding. Drop a ☸️ if you find this teaching powerful.",
        "A Zen monk trains the mind like a warrior trains the body. Discipline, focus, and presence in every action. Not through force, but through awareness. Thich Nhat Hanh said, 'Walk as if you are kissing the earth with your feet.' Every moment is an opportunity to practice mindfulness. Eating, walking, breathing, listening. This is the path. Comment one way you practice mindfulness daily. 👣 #zen #mindfulness #buddhism #discipline #monk #awareness #presence",
        "Non-attachment doesn't mean you stop caring. It means you care so deeply that you don't need to possess. You can love without clinging. You can appreciate without grasping. You can enjoy the present moment without desperately trying to hold onto it. That's the paradox at the heart of Buddhist wisdom. Let go a little, and see how much more you experience. 💫 #nonattachment #buddhism #zen #love #mindfulness #lettinggo #wisdom #spirituality",
    ]

    if not api_key:
        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        print("Warning: POLLINATIONS_API_KEY not found. Using fallback captions.")
        return chosen_title, chosen_desc

    vibes = [
        "peaceful and wise — speak with the calm presence of a Zen monk sharing timeless truths",
        "thought-provoking and deep — make people stop scrolling and reflect on their own mind",
        "gentle and compassionate — speak with warmth and understanding, like a wise teacher",
        "simple and profound — use simple words to convey deep spiritual insights",
        "mindful and present — bring the viewer into the now with every word",
        "reflective and meditative — create space for contemplation and inner stillness",
        "grounded and authentic — share Buddhist wisdom in a way that feels real and applicable",
    ]
    chosen_vibe = random.choice(vibes)

    prompt = (
        f"Write a completely unique, long, and captivating title and description for a short video "
        f"for the social media page 'Monk Tashirok'. "
        f"The page shares Buddhist philosophy, Zen wisdom, and life lessons — "
        f"helping people find peace, presence, and purpose in a chaotic world. "
        f"Speak as a wise and compassionate monk sharing timeless teachings with warmth and clarity. "
        f"Make the vibe {chosen_vibe}. "
        f"The description should be LONG (4-6 sentences minimum), deeply insightful, and calming. "
        f"Include engagement calls-to-action such as: "
        f"- Like if this wisdom spoke to your soul! "
        f"- Comment your thoughts on this teaching! "
        f"- Share this with someone who needs peace today! "
        f"- Follow Monk Tashirok for more timeless wisdom! "
        f"Include relevant hashtags in ALL LOWERCASE such as #buddhism #zen #mindfulness #wisdom #meditation #innerpeace #spirituality #lifelessons #monk #philosophy #peace #presence #lettinggo #buddha. "
        f"Return ONLY a valid JSON object in this format: {{\"title\": \"<title>\", \"description\": \"<description>\"}} "
        f"Do not include any other text or markdown block backticks."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "seed": random.randint(1, 999999)
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        return result.get("title", chosen_title), result.get("description", chosen_desc)
    except Exception as e:
        print(f"Error generating caption: {e}")
        return random.choice(fallback_titles), random.choice(fallback_descriptions)

def main():
    print("=" * 60)
    print("🚀 DAILY AUTOMATION STARTING")
    print("=" * 60)
    
    specific_video = sys.argv[1] if len(sys.argv) > 1 else None
    video_path, video_name = select_video(specific_video)
    if not video_path:
        print("✅ No new videos found to publish. Exiting.")
        return
        
    print(f"👉 Selected Video: {video_name}")
    print("🧠 Generating caption via Pollination AI...")
    title, description = generate_caption()
    
    print(f"📝 Title: {title}")
    print(f"📝 Description:\n{description}")
    
    # Combined caption for platforms that use a single text field
    combined_caption = f"{title}\n\n{description}"
    
    success_flags = {
        "youtube": False
    }
    
    # YouTube Shorts
    try:
        upload_to_youtube(video_path, title, description, tags=["buddhism", "zen", "mindfulness", "meditation", "wisdom", "innerpeace", "spirituality", "lifelessons", "monk", "philosophy", "peace", "presence", "lettinggo", "buddha", "monk tashirok"])
        success_flags["youtube"] = True
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        
    # Record as published regardless of partial success,
    # to avoid repeating the same video. Alternatively, only record if fully successful.
    print("\n✅ Marking video as published.")
    
    # Check if this is a recycled video (already in published_videos.json)
    published_list = get_already_published()
    is_recycled = any(item["video_name"] == video_name for item in published_list)
    
    if is_recycled:
        print(f"   🔄 This is a recycled video (re-publishing)")
    
    mark_as_published(video_name, {
        "title": title,
        "description": description,
        "success_flags": success_flags,
        "recycled": is_recycled
    })
    
    # Move the published video to Published_Videos folder
    published_dir = "Published_Videos"
    if not os.path.exists(published_dir):
        os.makedirs(published_dir)
        
    try:
        dest_path = os.path.join(published_dir, video_name)
        shutil.move(video_path, dest_path)
        print(f"📦 Moved published video to {dest_path}")
    except Exception as e:
        print(f"❌ Failed to move published video: {e}")
    
    print("🎉 DAILY AUTOMATION COMPLETE")

if __name__ == "__main__":
    main()
