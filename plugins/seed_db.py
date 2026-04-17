import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

PACKAGE_DETAILS = {
  "harsil": {
    "package_id": "harsil",
    "eyebrow": "3N / 4D · Peaceful Himalayan Escape · ₹8999",
    "title": "Harsil Valley",
    "summary": "A slow, soulful journey into the heart of the Himalayas for travelers who want homestay warmth, alpine views, and enough breathing room to really feel the place.",
    "image": "./statics/assets/harshilvalley916.png",
    "card_image": "./statics/assets/harshilvalley.png",
    "badge": "Expert Choice",
    "price": "₹8999",
    "facts": ["Dehradun / Rishikesh", "Homestay", "6 Meals", "5% GST extra"],
    "itinerary": [
      {
        "day": "Day 1",
        "title": "Dehradun / Rishikesh to Harsil Valley",
        "items": [
          "Morning departure around 8 AM via Chamba and Uttarkashi",
          "Visit Kashi Vishwanath Temple and stop at Gangnani hot springs",
          "Arrive in Harsil by evening for check-in, chai, and bonfire"
        ]
      },
      {
        "day": "Day 2",
        "title": "Lama Top Trek and Village Exploration",
        "items": [
          "Breakfast followed by trek to Lama Top for valley views",
          "Explore Harsil market and local food spots",
          "Visit Hari Sheela Temple and Mukhba Village"
        ]
      },
      {
        "day": "Day 3",
        "title": "Gangotri Valley and Gartang Gali",
        "items": [
          "Visit Gartang Gali and Lanka Bridge after breakfast",
          "Continue to Gangotri Temple and Surya Kund",
          "Return for Bhagirathi riverside relaxation and bonfire evening"
        ]
      },
      {
        "day": "Day 4",
        "title": "Return to Dehradun / Rishikesh",
        "items": [
          "Early breakfast and checkout",
          "Visit NIM Campus in Uttarkashi",
          "Lunch en route, Tehri Lake viewpoint, and evening arrival"
        ]
      }
    ],
    "highlights": [
      "Scenic drive via Uttarkashi with tea stop at Gangnani hot springs",
      "Lama Top trek, Mukhba Village, and Hari Sheela Temple",
      "Gangotri Temple, Surya Kund, Gartang Gali, and Lanka Bridge",
      "Bonfire evenings, local food, and Bhagirathi riverside time"
    ],
    "inclusions": [
      "Tempo Traveller transportation",
      "3 nights homestay stay",
      "6 meals plus morning and evening tea",
      "Sightseeing, trek coordination, bonfire, group sessions, trip captain assistance"
    ],
    "exclusions": [
      "Lunch and extra meals",
      "Personal expenses",
      "Entry fees if applicable",
      "Travel insurance and 5% GST"
    ],
    "carry": [
      "Warm clothes and jacket",
      "Trekking shoes and 20–30L backpack",
      "Water bottle and personal medicines",
      "Sunglasses, sunscreen, cap, and ID proof"
    ]
  },
  "chakrata-retreat": {
    "package_id": "chakrata-retreat",
    "eyebrow": "2N / 3D · Adventure & Travel Retreat · ₹4999",
    "title": "Chakrata Retreat",
    "summary": "An overnight Delhi escape into pine forests and mountain air with a great balance of easy adventure, winterline sunsets, resort comfort, and bonfire nights.",
    "image": "./statics/assets/charkataretread916.png",
    "card_image": "./statics/assets/chakrataretreat.jpg",
    "badge": "Forest Run",
    "price": "₹4999",
    "facts": ["Delhi pickup", "Resort Stay", "Rock Climbing", "5% GST extra"],
    "itinerary": [
      {
        "day": "Day 0",
        "title": "Delhi to Chakrata",
        "items": [
          "Late-night departure from Akshardham Metro Station or Kashmiri Gate",
          "Overnight road journey towards Chakrata"
        ]
      },
      {
        "day": "Day 1",
        "title": "Arrival and Moila Top Trek",
        "items": [
          "Reach early morning, check-in, freshen up, and breakfast",
          "Drive to Lokhandi and trek to Moila Top via Budher Caves",
          "Sunset point visit followed by snacks, bonfire, music, and dinner"
        ]
      },
      {
        "day": "Day 2",
        "title": "Tiger Falls and Activities",
        "items": [
          "Sunrise views and breakfast at the resort",
          "Short hike with rock climbing experience",
          "Visit Tiger Falls and explore Chakrata market before overnight return"
        ]
      },
      {
        "day": "Day 3",
        "title": "Arrival in Delhi",
        "items": [
          "Reach Delhi early morning around 4–5 AM",
          "Trip wraps with breakfast plans and a head full of mountain air"
        ]
      }
    ],
    "highlights": [
      "Overnight journey from Delhi with pickup from Akshardham or Kashmiri Gate",
      "Moila Top trek via Budher Caves and sunset point visit",
      "Tiger Falls visit with short hike and rock climbing activity",
      "Bonfire, music, stargazing, and Chakrata market walk"
    ],
    "inclusions": [
      "AC Tempo Traveller or bus transport",
      "1 night resort stay",
      "2 breakfast, 1 snacks, 1 dinner, morning and evening tea",
      "Trek access, rock climbing, Tiger Falls visit, bonfire, trip captain and crew support"
    ],
    "exclusions": [
      "Extra meals during travel",
      "Entry fees and off-roading charges if any",
      "Personal expenses",
      "Travel insurance and 5% GST"
    ],
    "carry": [
      "Warm layers and jacket",
      "Trekking shoes and backpack",
      "Water bottle, sunglasses, sunscreen, cap",
      "Umbrella or poncho, personal medicines, and ID proof"
    ]
  },
  "chakrata-sprint": {
    "package_id": "chakrata-sprint",
    "eyebrow": "1 Day · One Day Mountain Escape · ₹1699",
    "title": "Chakrata Sprint",
    "summary": "Short on time but still want the mountains? This one-day route is built as a quick scenic reset from Dehradun with a mini trek, breakfast stop, and sunset line views.",
    "image": "./statics/assets/charkatavalley916.png",
    "card_image": "./statics/assets/chakratasprint.jpg",
    "badge": "Quick Escape",
    "price": "₹1699",
    "facts": ["Dehradun pickup", "Same-day return", "Breakfast", "5% GST extra"],
    "itinerary": [
      {
        "day": "06:45 AM",
        "title": "Departure from Dehradun",
        "items": [
          "Pickups from ISBT, Clock Tower, Ballupur, Premnagar, Suddhowala, Selaqui, and Vikasnagar",
          "Scenic drive through forest roads into the hills"
        ]
      },
      {
        "day": "08:45 AM",
        "title": "Breakfast Stop",
        "items": [
          "Paratha breakfast with chai",
          "Short refresh break before entering the higher roads"
        ]
      },
      {
        "day": "11:00 AM",
        "title": "Exploration Window",
        "items": [
          "Reach Lokhandi or Deoban region",
          "Short trek to Moila Top and open Himalayan viewpoints"
        ]
      },
      {
        "day": "04:30 PM",
        "title": "Sunset and Return",
        "items": [
          "Visit Chakrata Sunset Point for winterline and golden light",
          "Depart around 6 PM and reach Dehradun by about 8:45 PM"
        ]
      }
    ],
    "highlights": [
      "Early departure from Dehradun with multiple pickup points",
      "Breakfast stop with parathas and chai",
      "Moila Top or Deoban short trek with Lokhandi snow views",
      "Chakrata Sunset Point for winterline and golden light"
    ],
    "inclusions": [
      "Tempo Traveller round-trip transport",
      "Breakfast, refreshments, and evening tea",
      "Guided Moila Top trek",
      "Sunset point visit and trip captain assistance"
    ],
    "exclusions": [
      "Extra meals",
      "Entry and off-road charges if any",
      "Personal expenses",
      "Travel insurance and 5% GST"
    ],
    "carry": [
      "Comfortable shoes and warm clothes",
      "Small backpack and water bottle",
      "Umbrella or poncho, personal medicines, and ID proof",
      "Sunglasses, sunscreen, and cap"
    ]
  },
  "shangarh": {
    "package_id": "shangarh",
    "eyebrow": "2N / 3D · The Hidden Meadow Retreat · ₹7999",
    "title": "Shangarh",
    "summary": "Deep in the Sainj Valley, where devdar forests open up into a massive alpine meadow. This one is all about slow mornings, ancient temples, short trails, and cafe-hopping in one of Himachal’s quietest corners.",
    "image": "./statics/assets/shangarh.jpg",
    "card_image": "./statics/assets/shangarh.jpg",
    "badge": "Offbeat Pick",
    "price": "₹7999",
    "facts": ["Delhi pickup", "Homestay", "Meadows", "5% GST extra"],
    "itinerary": [
      {
        "day": "Day 0",
        "title": "Departure from Delhi",
        "items": ["Evening Volvo/Traveller departure from Delhi"]
      },
      {
        "day": "Day 1",
        "title": "Arrival in Shangarh",
        "items": ["Arrival by noon, check-in, visit Shangarh meadows, bonfire evening"]
      },
      {
        "day": "Day 2",
        "title": "Waterfalls and Cafes",
        "items": ["Visit Barshangarh waterfall, cafe hopping, explore local trails"]
      },
      {
        "day": "Day 3",
        "title": "Departure",
        "items": ["Morning breakfast and start the journey back to Delhi"]
      }
    ],
    "highlights": [
        "Vast Shangarh Meadows",
        "Barshangarh Waterfalls",
        "Quiet homestay living"
    ],
    "inclusions": ["Transport", "2 Nights stay", "Meals as per plan"],
    "exclusions": ["Any personal expenses", "Lunch"],
    "carry": ["Warm clothes", "Trekking shoes"]
  }

}

parsed_packages = list(PACKAGE_DETAILS.values())

import base64
import os

def load_image_as_base64(filepath):
    actual_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filepath.replace('./', ''))
    try:
        with open(actual_path, "rb") as f:
            ext = os.path.splitext(actual_path)[1][1:]
            if ext == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return filepath

for pkg in parsed_packages:
    if pkg.get("image", "").startswith("./"):
        pkg["image"] = load_image_as_base64(pkg["image"])
    if pkg.get("card_image", "").startswith("./"):
        pkg["card_image"] = load_image_as_base64(pkg["card_image"])


async def seed():
    uri = "mongodb+srv://nirusaki:nirusaki@cluster0.rrdouxd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = AsyncIOMotorClient(uri)
    db = client.ghoomne_chalo
    collection = db.packages
    
    # drop existing to prevent duplicates
    await collection.drop()
    
    await collection.insert_many(parsed_packages)
    print("Database seeded with packages!")

if __name__ == "__main__":
    asyncio.run(seed())
