"""
Conversation Simulator with RAG
================================
This module implements a RAG-based conversation simulation system that learns
from user message history to generate realistic responses matching their texting style.
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import re
from collections import Counter

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Message:
    """Represents a single message in a conversation."""
    id: str
    sender_id: str
    text: str
    timestamp: datetime
    conversation_id: str

@dataclass
class UserProfile:
    """Stores analyzed texting style characteristics for a user."""
    user_id: str
    avg_length: float
    uses_emojis: bool
    emoji_frequency: float
    capitalization: str  # 'lowercase', 'sentence_case', 'mixed'
    common_phrases: List[str]
    avg_response_time: float  # in seconds
    punctuation_style: str
    vocabulary_richness: float

# ============================================================================
# MOCK DATA
# ============================================================================

def create_mock_messages() -> Dict[str, List[Dict]]:
    """
    Create mock message history for two users.
    Returns a dictionary with user_id as key and list of message records.
    """

    # User A: Casual, uses emojis, lowercase, short responses
    user_a_messages = [
        # Greetings
        {"context": "Them: hey what's up", "response": "nm just chillin hbu", "timestamp": "2025-01-01T10:00:00"},
        {"context": "Them: hi!", "response": "heyyy", "timestamp": "2025-01-02T14:00:00"},
        {"context": "Them: good morning", "response": "morning! how'd u sleep", "timestamp": "2025-01-03T08:00:00"},
        {"context": "Them: yo", "response": "yooo what's good", "timestamp": "2025-01-04T16:00:00"},
        {"context": "Them: hey!", "response": "hey! whats up", "timestamp": "2025-01-21T09:00:00"},
        {"context": "Them: hiii", "response": "hiiii how r u", "timestamp": "2025-01-22T11:00:00"},
        {"context": "Them: good afternoon", "response": "hey hey", "timestamp": "2025-01-23T14:00:00"},
        {"context": "Them: sup", "response": "not much wbu", "timestamp": "2025-01-24T16:00:00"},
        {"context": "Them: hellooo", "response": "heyy whats going on", "timestamp": "2025-01-25T10:00:00"},
        {"context": "Them: good evening", "response": "heyyy how was ur day", "timestamp": "2025-01-26T18:00:00"},

        # Plans/Invitations
        {"context": "Them: want to get dinner tonight?", "response": "yes I'm starving lol where were u thinking", "timestamp": "2025-01-05T17:00:00"},
        {"context": "Them: dinner tomorrow?", "response": "sure! what time works for u", "timestamp": "2025-01-06T12:00:00"},
        {"context": "Them: are you free tonight", "response": "yeah what's up", "timestamp": "2025-01-07T15:00:00"},
        {"context": "Them: wanna grab coffee", "response": "down! when", "timestamp": "2025-01-08T10:00:00"},
        {"context": "Them: party at mike's saturday", "response": "ooh I'm in, what time", "timestamp": "2025-01-09T20:00:00"},
        {"context": "Them: movies this weekend?", "response": "yesss what do u wanna see", "timestamp": "2025-01-10T11:00:00"},
        {"context": "Them: brunch sunday?", "response": "omg yes where", "timestamp": "2025-01-27T09:00:00"},
        {"context": "Them: want to study together", "response": "yeah sure library?", "timestamp": "2025-01-28T13:00:00"},
        {"context": "Them: gym later?", "response": "down what time u thinking", "timestamp": "2025-01-29T07:00:00"},
        {"context": "Them: concert next friday", "response": "wait who's playing", "timestamp": "2025-01-30T20:00:00"},
        {"context": "Them: road trip this summer?", "response": "yooo im so down where to", "timestamp": "2025-01-31T15:00:00"},
        {"context": "Them: beach day tomorrow", "response": "yesss finally, what time", "timestamp": "2025-02-01T11:00:00"},
        {"context": "Them: game night at my place", "response": "ooh fun what games", "timestamp": "2025-02-02T18:00:00"},
        {"context": "Them: hiking saturday morning", "response": "how early tho lol", "timestamp": "2025-02-03T21:00:00"},
        {"context": "Them: want to try that new restaurant", "response": "which one the ramen place?", "timestamp": "2025-02-04T12:00:00"},
        {"context": "Them: karaoke tonight", "response": "lmaoo ok im in", "timestamp": "2025-02-05T17:00:00"},

        # Reactions/Emotions
        {"context": "Them: I got the job!", "response": "omggg congrats!!! thats amazing", "timestamp": "2025-01-11T14:00:00"},
        {"context": "Them: my flight got cancelled", "response": "nooo that sucks :( can u get another one", "timestamp": "2025-01-12T09:00:00"},
        {"context": "Them: check out this meme", "response": "lmaooo dead", "timestamp": "2025-01-13T22:00:00"},
        {"context": "Them: I'm so tired", "response": "same honestly need more coffee", "timestamp": "2025-01-14T07:00:00"},
        {"context": "Them: I passed my exam!", "response": "lets goooo knew u would", "timestamp": "2025-02-06T16:00:00"},
        {"context": "Them: I'm so stressed", "response": "aw whats wrong", "timestamp": "2025-02-07T22:00:00"},
        {"context": "Them: look at this sunset", "response": "woahh thats so pretty", "timestamp": "2025-02-08T19:00:00"},
        {"context": "Them: my car broke down", "response": "oh no do u need a ride", "timestamp": "2025-02-09T08:00:00"},
        {"context": "Them: I got a puppy!", "response": "WHAT no way send pics immediately", "timestamp": "2025-02-10T15:00:00"},
        {"context": "Them: feeling sick today", "response": "aw no :( rest up and drink water", "timestamp": "2025-02-11T10:00:00"},
        {"context": "Them: I'm so happy rn", "response": "yay! whats up", "timestamp": "2025-02-12T14:00:00"},
        {"context": "Them: ugh mondays", "response": "literally same i cant", "timestamp": "2025-02-13T08:00:00"},
        {"context": "Them: look what I made", "response": "oooh that looks so good", "timestamp": "2025-02-14T19:00:00"},
        {"context": "Them: I'm bored", "response": "same wanna do something", "timestamp": "2025-02-15T16:00:00"},
        {"context": "Them: just had the best food", "response": "ooh where at", "timestamp": "2025-02-16T13:00:00"},
        {"context": "Them: finally friday", "response": "fr this week was so long", "timestamp": "2025-02-17T17:00:00"},

        # Questions
        {"context": "Them: where are you?", "response": "omw be there in 5", "timestamp": "2025-01-15T19:00:00"},
        {"context": "Them: did you see my text", "response": "just saw it sorry! yeah that works", "timestamp": "2025-01-16T13:00:00"},
        {"context": "Them: what do you think", "response": "hmm I think the first one is better tbh", "timestamp": "2025-01-17T16:00:00"},
        {"context": "Them: how was your day", "response": "pretty good! busy tho hbu", "timestamp": "2025-01-18T21:00:00"},
        {"context": "Them: what are you doing", "response": "just watching netflix wbu", "timestamp": "2025-02-18T20:00:00"},
        {"context": "Them: have you eaten", "response": "not yet im starving", "timestamp": "2025-02-19T12:00:00"},
        {"context": "Them: when do you get off work", "response": "like 6ish why", "timestamp": "2025-02-20T15:00:00"},
        {"context": "Them: did you finish the assignment", "response": "lol no im struggling", "timestamp": "2025-02-21T23:00:00"},
        {"context": "Them: what should I wear", "response": "hmm the blue one is cute", "timestamp": "2025-02-22T18:00:00"},
        {"context": "Them: can you help me with something", "response": "yeah ofc what's up", "timestamp": "2025-02-23T14:00:00"},
        {"context": "Them: what time is it there", "response": "like 3pm why", "timestamp": "2025-02-24T15:00:00"},
        {"context": "Them: did you hear about that", "response": "no what happened", "timestamp": "2025-02-25T11:00:00"},
        {"context": "Them: which one should I get", "response": "def the second one", "timestamp": "2025-02-26T16:00:00"},
        {"context": "Them: remember that place", "response": "omg yes that was so fun", "timestamp": "2025-02-27T19:00:00"},

        # Casual chat
        {"context": "Them: just finished that show", "response": "was it good? been meaning to watch it", "timestamp": "2025-01-19T23:00:00"},
        {"context": "Them: this weather is crazy", "response": "ikr its so cold out", "timestamp": "2025-01-20T12:00:00"},
        {"context": "Them: I can't sleep", "response": "same its 2am and im wide awake", "timestamp": "2025-02-28T02:00:00"},
        {"context": "Them: this song is so good", "response": "which one send it", "timestamp": "2025-03-01T21:00:00"},
        {"context": "Them: I love this weather", "response": "same its so nice out finally", "timestamp": "2025-03-02T14:00:00"},
        {"context": "Them: just woke up", "response": "lol same i slept forever", "timestamp": "2025-03-03T11:00:00"},
        {"context": "Them: traffic is so bad", "response": "ugh i hate that", "timestamp": "2025-03-04T08:00:00"},
        {"context": "Them: I miss traveling", "response": "same we need to plan a trip", "timestamp": "2025-03-05T20:00:00"},
        {"context": "Them: this coffee is amazing", "response": "ooh where from", "timestamp": "2025-03-06T09:00:00"},
        {"context": "Them: I need a vacation", "response": "literally same im so burnt out", "timestamp": "2025-03-07T17:00:00"},
        {"context": "Them: just saw the funniest thing", "response": "lol what", "timestamp": "2025-03-08T15:00:00"},
        {"context": "Them: I love weekends", "response": "fr weekdays are the worst", "timestamp": "2025-03-09T10:00:00"},
        {"context": "Them: this book is so good", "response": "ooh what is it", "timestamp": "2025-03-10T22:00:00"},
        {"context": "Them: my wifi is so slow", "response": "thats so annoying", "timestamp": "2025-03-11T19:00:00"},

        # Opinions/Preferences
        {"context": "Them: pizza or tacos", "response": "tacos 100%", "timestamp": "2025-03-12T12:00:00"},
        {"context": "Them: what's your favorite movie", "response": "hmm prob inception or interstellar", "timestamp": "2025-03-13T20:00:00"},
        {"context": "Them: morning person or night owl", "response": "night owl for sure lol", "timestamp": "2025-03-14T23:00:00"},
        {"context": "Them: coffee or tea", "response": "coffee always", "timestamp": "2025-03-15T08:00:00"},
        {"context": "Them: cats or dogs", "response": "dogs but cats are cute too", "timestamp": "2025-03-16T16:00:00"},
        {"context": "Them: summer or winter", "response": "summer for sure i hate being cold", "timestamp": "2025-03-17T14:00:00"},
        {"context": "Them: sweet or savory", "response": "savory but i have a sweet tooth too", "timestamp": "2025-03-18T11:00:00"},
        {"context": "Them: city or nature", "response": "both honestly depends on my mood", "timestamp": "2025-03-19T15:00:00"},

        # Confirmations/Agreements
        {"context": "Them: see you at 7?", "response": "yep see u then!", "timestamp": "2025-03-20T18:00:00"},
        {"context": "Them: so we're good for tomorrow", "response": "yup all set", "timestamp": "2025-03-21T21:00:00"},
        {"context": "Them: you're coming right", "response": "ofc wouldn't miss it", "timestamp": "2025-03-22T17:00:00"},
        {"context": "Them: 8pm works?", "response": "perfect see u there", "timestamp": "2025-03-23T16:00:00"},
        {"context": "Them: I'll pick you up", "response": "ok sounds good ty!", "timestamp": "2025-03-24T19:00:00"},
        {"context": "Them: meet at the usual spot", "response": "yup otw now", "timestamp": "2025-03-25T13:00:00"},

        # Declining/Unavailable
        {"context": "Them: can you come out tonight", "response": "ugh i wish but i have so much work", "timestamp": "2025-03-26T19:00:00"},
        {"context": "Them: party this weekend", "response": "i cant :( im out of town", "timestamp": "2025-03-27T15:00:00"},
        {"context": "Them: lunch today?", "response": "i have a meeting but maybe tmrw?", "timestamp": "2025-03-28T11:00:00"},
        {"context": "Them: want to join us", "response": "maybe next time! im exhausted rn", "timestamp": "2025-03-29T22:00:00"},

        # Random/Misc
        {"context": "Them: guess what", "response": "what!!", "timestamp": "2025-03-30T14:00:00"},
        {"context": "Them: you'll never believe this", "response": "omg what happened", "timestamp": "2025-03-31T16:00:00"},
        {"context": "Them: I need to tell you something", "response": "uh oh whats up", "timestamp": "2025-04-01T20:00:00"},
        {"context": "Them: remind me later", "response": "ok about what", "timestamp": "2025-04-02T10:00:00"},
        {"context": "Them: nvm figured it out", "response": "oh ok nice", "timestamp": "2025-04-03T13:00:00"},
        {"context": "Them: sorry wrong person", "response": "lol all good", "timestamp": "2025-04-04T17:00:00"},
        {"context": "Them: can I call you", "response": "yeah give me 5 min", "timestamp": "2025-04-05T19:00:00"},
        {"context": "Them: check your email", "response": "ok one sec", "timestamp": "2025-04-06T09:00:00"},
    ]

    # User B: More formal, proper punctuation, longer responses
    user_b_messages = [
        # Greetings
        {"context": "Them: hey what's up", "response": "Hey! Not much, just working on some stuff. How about you?", "timestamp": "2025-01-01T10:00:00"},
        {"context": "Them: hi!", "response": "Hi there! How's your day going?", "timestamp": "2025-01-02T14:00:00"},
        {"context": "Them: good morning", "response": "Good morning! Hope you slept well.", "timestamp": "2025-01-03T08:00:00"},
        {"context": "Them: yo", "response": "Hey! What's going on?", "timestamp": "2025-01-04T16:00:00"},
        {"context": "Them: hey!", "response": "Hey! Good to hear from you. What's new?", "timestamp": "2025-01-21T09:00:00"},
        {"context": "Them: hiii", "response": "Hi! How have you been?", "timestamp": "2025-01-22T11:00:00"},
        {"context": "Them: good afternoon", "response": "Good afternoon! How's your day treating you?", "timestamp": "2025-01-23T14:00:00"},
        {"context": "Them: sup", "response": "Hey! Not much going on here. You?", "timestamp": "2025-01-24T16:00:00"},
        {"context": "Them: hellooo", "response": "Hello! What's going on?", "timestamp": "2025-01-25T10:00:00"},
        {"context": "Them: good evening", "response": "Good evening! How was your day?", "timestamp": "2025-01-26T18:00:00"},

        # Plans/Invitations
        {"context": "Them: want to get dinner tonight?", "response": "That sounds great! What kind of food are you in the mood for?", "timestamp": "2025-01-05T17:00:00"},
        {"context": "Them: dinner tomorrow?", "response": "Sure, I'd be down for that. Any preferences on where?", "timestamp": "2025-01-06T12:00:00"},
        {"context": "Them: are you free tonight", "response": "I am! Did you have something in mind?", "timestamp": "2025-01-07T15:00:00"},
        {"context": "Them: wanna grab coffee", "response": "Definitely! When works for you?", "timestamp": "2025-01-08T10:00:00"},
        {"context": "Them: party at mike's saturday", "response": "Oh nice! I'll be there. Should I bring anything?", "timestamp": "2025-01-09T20:00:00"},
        {"context": "Them: movies this weekend?", "response": "Yes! I've been wanting to see that new thriller. What about you?", "timestamp": "2025-01-10T11:00:00"},
        {"context": "Them: brunch sunday?", "response": "That sounds perfect! Do you have a place in mind?", "timestamp": "2025-01-27T09:00:00"},
        {"context": "Them: want to study together", "response": "Sure! Should we meet at the library or somewhere else?", "timestamp": "2025-01-28T13:00:00"},
        {"context": "Them: gym later?", "response": "Sounds good! What time were you thinking?", "timestamp": "2025-01-29T07:00:00"},
        {"context": "Them: concert next friday", "response": "Oh cool! Who's performing? I might be interested.", "timestamp": "2025-01-30T20:00:00"},
        {"context": "Them: road trip this summer?", "response": "That would be amazing! Where were you thinking of going?", "timestamp": "2025-01-31T15:00:00"},
        {"context": "Them: beach day tomorrow", "response": "Yes! I've been wanting to go. What time should we meet?", "timestamp": "2025-02-01T11:00:00"},
        {"context": "Them: game night at my place", "response": "Sounds fun! What games are we playing? Should I bring anything?", "timestamp": "2025-02-02T18:00:00"},
        {"context": "Them: hiking saturday morning", "response": "I'm in! What trail were you thinking? And how early?", "timestamp": "2025-02-03T21:00:00"},
        {"context": "Them: want to try that new restaurant", "response": "Yes! I've heard great things about it. When were you thinking?", "timestamp": "2025-02-04T12:00:00"},
        {"context": "Them: karaoke tonight", "response": "Haha sure, why not! What time and where?", "timestamp": "2025-02-05T17:00:00"},

        # Reactions/Emotions
        {"context": "Them: I got the job!", "response": "Congratulations!! That's such great news! When do you start?", "timestamp": "2025-01-11T14:00:00"},
        {"context": "Them: my flight got cancelled", "response": "Oh no, that's really frustrating. Were you able to rebook?", "timestamp": "2025-01-12T09:00:00"},
        {"context": "Them: check out this meme", "response": "Haha that's hilarious! Where did you find that?", "timestamp": "2025-01-13T22:00:00"},
        {"context": "Them: I'm so tired", "response": "I know the feeling. Maybe try to get some rest tonight?", "timestamp": "2025-01-14T07:00:00"},
        {"context": "Them: I passed my exam!", "response": "That's amazing! I knew you could do it. How are you celebrating?", "timestamp": "2025-02-06T16:00:00"},
        {"context": "Them: I'm so stressed", "response": "I'm sorry to hear that. Do you want to talk about it?", "timestamp": "2025-02-07T22:00:00"},
        {"context": "Them: look at this sunset", "response": "Wow, that's beautiful! Where did you take that?", "timestamp": "2025-02-08T19:00:00"},
        {"context": "Them: my car broke down", "response": "Oh no! Do you need help? I can come pick you up if needed.", "timestamp": "2025-02-09T08:00:00"},
        {"context": "Them: I got a puppy!", "response": "Oh my goodness! That's so exciting! What kind? Send pictures!", "timestamp": "2025-02-10T15:00:00"},
        {"context": "Them: feeling sick today", "response": "I'm sorry to hear that! Make sure to rest and stay hydrated.", "timestamp": "2025-02-11T10:00:00"},
        {"context": "Them: I'm so happy rn", "response": "That's great! What's making you so happy?", "timestamp": "2025-02-12T14:00:00"},
        {"context": "Them: ugh mondays", "response": "I know, right? Hope your week gets better from here!", "timestamp": "2025-02-13T08:00:00"},
        {"context": "Them: look what I made", "response": "That looks amazing! You're so talented. What's the recipe?", "timestamp": "2025-02-14T19:00:00"},
        {"context": "Them: I'm bored", "response": "Same here! Want to do something? I'm free if you are.", "timestamp": "2025-02-15T16:00:00"},
        {"context": "Them: just had the best food", "response": "Oh nice! Where at? I'm always looking for good food recommendations.", "timestamp": "2025-02-16T13:00:00"},
        {"context": "Them: finally friday", "response": "I know! This week felt so long. Any plans for the weekend?", "timestamp": "2025-02-17T17:00:00"},

        # Questions
        {"context": "Them: where are you?", "response": "On my way! Should be there in about 5 minutes.", "timestamp": "2025-01-15T19:00:00"},
        {"context": "Them: did you see my text", "response": "Just saw it now, sorry about that! Yes, that works for me.", "timestamp": "2025-01-16T13:00:00"},
        {"context": "Them: what do you think", "response": "I think the first option is better. It seems more practical.", "timestamp": "2025-01-17T16:00:00"},
        {"context": "Them: how was your day", "response": "It was good, thanks for asking! Pretty productive. How was yours?", "timestamp": "2025-01-18T21:00:00"},
        {"context": "Them: what are you doing", "response": "Just relaxing at home, watching some TV. How about you?", "timestamp": "2025-02-18T20:00:00"},
        {"context": "Them: have you eaten", "response": "Not yet! I was actually just thinking about what to eat.", "timestamp": "2025-02-19T12:00:00"},
        {"context": "Them: when do you get off work", "response": "Around 6pm. Did you have something in mind?", "timestamp": "2025-02-20T15:00:00"},
        {"context": "Them: did you finish the assignment", "response": "Still working on it! It's taking longer than I expected. How about you?", "timestamp": "2025-02-21T23:00:00"},
        {"context": "Them: what should I wear", "response": "Hmm, I think the blue one would look great! It suits you.", "timestamp": "2025-02-22T18:00:00"},
        {"context": "Them: can you help me with something", "response": "Of course! What do you need help with?", "timestamp": "2025-02-23T14:00:00"},
        {"context": "Them: what time is it there", "response": "It's about 3pm here. Why, what's up?", "timestamp": "2025-02-24T15:00:00"},
        {"context": "Them: did you hear about that", "response": "No, I didn't! What happened?", "timestamp": "2025-02-25T11:00:00"},
        {"context": "Them: which one should I get", "response": "I'd go with the second one. It seems like better value.", "timestamp": "2025-02-26T16:00:00"},
        {"context": "Them: remember that place", "response": "Yes! That was such a good time. We should go back there.", "timestamp": "2025-02-27T19:00:00"},

        # Casual chat
        {"context": "Them: just finished that show", "response": "Oh nice! How was it? I've been meaning to start it.", "timestamp": "2025-01-19T23:00:00"},
        {"context": "Them: this weather is crazy", "response": "Right? It's so cold. I can't wait for spring.", "timestamp": "2025-01-20T12:00:00"},
        {"context": "Them: I can't sleep", "response": "Same here! It's so late but I'm wide awake. Maybe try some tea?", "timestamp": "2025-02-28T02:00:00"},
        {"context": "Them: this song is so good", "response": "Which one? Send it to me! I'm always looking for new music.", "timestamp": "2025-03-01T21:00:00"},
        {"context": "Them: I love this weather", "response": "Same! It's so nice to finally have some warm weather.", "timestamp": "2025-03-02T14:00:00"},
        {"context": "Them: just woke up", "response": "Haha same here! I slept in way too late today.", "timestamp": "2025-03-03T11:00:00"},
        {"context": "Them: traffic is so bad", "response": "That's so frustrating! Hopefully it clears up soon.", "timestamp": "2025-03-04T08:00:00"},
        {"context": "Them: I miss traveling", "response": "Me too! We should definitely plan a trip soon.", "timestamp": "2025-03-05T20:00:00"},
        {"context": "Them: this coffee is amazing", "response": "Oh nice! Where did you get it from? I need to try it.", "timestamp": "2025-03-06T09:00:00"},
        {"context": "Them: I need a vacation", "response": "Same here! I'm feeling pretty burnt out lately.", "timestamp": "2025-03-07T17:00:00"},
        {"context": "Them: just saw the funniest thing", "response": "Oh really? What was it? I could use a laugh.", "timestamp": "2025-03-08T15:00:00"},
        {"context": "Them: I love weekends", "response": "Same! Weekdays can be so draining sometimes.", "timestamp": "2025-03-09T10:00:00"},
        {"context": "Them: this book is so good", "response": "What book is it? I've been looking for something new to read.", "timestamp": "2025-03-10T22:00:00"},
        {"context": "Them: my wifi is so slow", "response": "That's so annoying! Have you tried restarting your router?", "timestamp": "2025-03-11T19:00:00"},

        # Opinions/Preferences
        {"context": "Them: pizza or tacos", "response": "That's tough! I'd probably go with pizza, but tacos are great too.", "timestamp": "2025-03-12T12:00:00"},
        {"context": "Them: what's your favorite movie", "response": "Hmm, that's hard to say! I really love Inception and The Shawshank Redemption.", "timestamp": "2025-03-13T20:00:00"},
        {"context": "Them: morning person or night owl", "response": "Definitely a morning person! I'm most productive in the early hours.", "timestamp": "2025-03-14T23:00:00"},
        {"context": "Them: coffee or tea", "response": "Coffee for sure! I need it to function in the morning.", "timestamp": "2025-03-15T08:00:00"},
        {"context": "Them: cats or dogs", "response": "I love both, but I'd probably say dogs. They're so loyal!", "timestamp": "2025-03-16T16:00:00"},
        {"context": "Them: summer or winter", "response": "Summer! I love the warm weather and being able to go outside.", "timestamp": "2025-03-17T14:00:00"},
        {"context": "Them: sweet or savory", "response": "Savory for me! Though I do have a sweet tooth occasionally.", "timestamp": "2025-03-18T11:00:00"},
        {"context": "Them: city or nature", "response": "It depends on my mood! I like the convenience of the city but nature is so peaceful.", "timestamp": "2025-03-19T15:00:00"},

        # Confirmations/Agreements
        {"context": "Them: see you at 7?", "response": "Yes, see you then! Looking forward to it.", "timestamp": "2025-03-20T18:00:00"},
        {"context": "Them: so we're good for tomorrow", "response": "Yep, all set! Can't wait.", "timestamp": "2025-03-21T21:00:00"},
        {"context": "Them: you're coming right", "response": "Of course! Wouldn't miss it for anything.", "timestamp": "2025-03-22T17:00:00"},
        {"context": "Them: 8pm works?", "response": "Perfect! That works great for me. See you there!", "timestamp": "2025-03-23T16:00:00"},
        {"context": "Them: I'll pick you up", "response": "Sounds good! Thank you, I appreciate it.", "timestamp": "2025-03-24T19:00:00"},
        {"context": "Them: meet at the usual spot", "response": "Got it! I'm heading there now.", "timestamp": "2025-03-25T13:00:00"},

        # Declining/Unavailable
        {"context": "Them: can you come out tonight", "response": "I wish I could, but I have a lot of work to catch up on. Next time!", "timestamp": "2025-03-26T19:00:00"},
        {"context": "Them: party this weekend", "response": "Unfortunately I can't make it - I'll be out of town. Have fun though!", "timestamp": "2025-03-27T15:00:00"},
        {"context": "Them: lunch today?", "response": "I have a meeting during lunch, but could we do tomorrow instead?", "timestamp": "2025-03-28T11:00:00"},
        {"context": "Them: want to join us", "response": "I'd love to, but I'm really tired tonight. Maybe next time?", "timestamp": "2025-03-29T22:00:00"},

        # Random/Misc
        {"context": "Them: guess what", "response": "What?! Tell me!", "timestamp": "2025-03-30T14:00:00"},
        {"context": "Them: you'll never believe this", "response": "Oh no, what happened? Now I'm curious!", "timestamp": "2025-03-31T16:00:00"},
        {"context": "Them: I need to tell you something", "response": "Of course! What's going on?", "timestamp": "2025-04-01T20:00:00"},
        {"context": "Them: remind me later", "response": "Sure thing! What should I remind you about?", "timestamp": "2025-04-02T10:00:00"},
        {"context": "Them: nvm figured it out", "response": "Oh good! Glad you got it sorted.", "timestamp": "2025-04-03T13:00:00"},
        {"context": "Them: sorry wrong person", "response": "No worries at all! Happens to the best of us.", "timestamp": "2025-04-04T17:00:00"},
        {"context": "Them: can I call you", "response": "Sure! Give me about 5 minutes and I'll be ready.", "timestamp": "2025-04-05T19:00:00"},
        {"context": "Them: check your email", "response": "Just checked it! Thanks for letting me know.", "timestamp": "2025-04-06T09:00:00"},

        # Work/Professional
        {"context": "Them: how's the project going", "response": "It's going well! We're making good progress. Should be done by the deadline.", "timestamp": "2025-04-07T10:00:00"},
        {"context": "Them: did you send that email", "response": "Yes, I sent it about an hour ago. Let me know if you didn't receive it.", "timestamp": "2025-04-08T14:00:00"},
        {"context": "Them: meeting at 3", "response": "Got it, I'll be there! Do I need to prepare anything?", "timestamp": "2025-04-09T11:00:00"},
        {"context": "Them: can you cover for me", "response": "Sure, no problem! What do I need to know?", "timestamp": "2025-04-10T09:00:00"},

        # Appreciation/Thanks
        {"context": "Them: thanks for your help", "response": "Of course! Happy to help anytime. Let me know if you need anything else.", "timestamp": "2025-04-11T16:00:00"},
        {"context": "Them: you're the best", "response": "Aww, thank you! That really means a lot.", "timestamp": "2025-04-12T20:00:00"},
        {"context": "Them: I owe you one", "response": "Don't worry about it! That's what friends are for.", "timestamp": "2025-04-13T15:00:00"},
        {"context": "Them: couldn't have done it without you", "response": "I'm glad I could help! You did most of the work though.", "timestamp": "2025-04-14T18:00:00"},
    ]

    return {
        "user_a": user_a_messages,
        "user_b": user_b_messages
    }


def create_mock_embeddings(messages: List[Dict]) -> List[np.ndarray]:
    """
    Create mock embeddings for messages.
    In production, you'd use OpenAI's text-embedding-3-small or similar.

    For demo purposes, we create simple embeddings based on message characteristics.
    """
    embeddings = []

    for msg in messages:
        text = msg['response']

        # Create a simple feature vector (in production, use real embeddings)
        features = [
            len(text) / 100,  # normalized length
            text.count('!') / max(len(text), 1) * 10,  # exclamation density
            text.count('?') / max(len(text), 1) * 10,  # question density
            1.0 if any(c in text for c in '😀😂🙂❤️👍🎉') else 0.0,  # emoji presence
            sum(1 for c in text if c.isupper()) / max(len(text), 1),  # capitalization ratio
            len(text.split()) / 20,  # word count normalized
            text.count('lol') + text.count('haha') + text.count('lmao'),  # humor indicators
            1.0 if text.endswith('?') else 0.0,  # ends with question
        ]

        # Pad to 384 dimensions (similar to real embeddings)
        embedding = np.zeros(384)
        embedding[:len(features)] = features

        # Add some noise for variation
        embedding += np.random.randn(384) * 0.01

        embeddings.append(embedding)

    return embeddings


# ============================================================================
# USER PROFILE ANALYSIS
# ============================================================================

def analyze_user_style(messages: List[Dict]) -> UserProfile:
    """
    Analyze a user's texting style from their message history.

    Args:
        messages: List of message records with 'response' key

    Returns:
        UserProfile with analyzed characteristics
    """
    texts = [msg['response'] for msg in messages]

    # Average message length
    avg_length = sum(len(t) for t in texts) / len(texts)

    # Emoji detection
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    emoji_count = sum(len(emoji_pattern.findall(t)) for t in texts)
    uses_emojis = emoji_count > len(texts) * 0.1
    emoji_frequency = emoji_count / len(texts)

    # Capitalization style
    first_char_caps = sum(1 for t in texts if t and t[0].isupper())
    caps_ratio = first_char_caps / len(texts)

    if caps_ratio > 0.8:
        capitalization = 'sentence_case'
    elif caps_ratio < 0.2:
        capitalization = 'lowercase'
    else:
        capitalization = 'mixed'

    # Common phrases
    all_words = ' '.join(texts).lower().split()
    word_freq = Counter(all_words)

    # Find common 2-3 word phrases
    bigrams = []
    for text in texts:
        words = text.lower().split()
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")

    phrase_freq = Counter(bigrams)
    common_phrases = [phrase for phrase, count in phrase_freq.most_common(5) if count > 1]

    # Punctuation style
    exclamation_count = sum(t.count('!') for t in texts)
    period_count = sum(t.count('.') for t in texts)

    if exclamation_count > period_count:
        punctuation_style = 'exclamatory'
    elif period_count > len(texts) * 0.5:
        punctuation_style = 'formal'
    else:
        punctuation_style = 'minimal'

    # Vocabulary richness (unique words / total words)
    unique_words = len(set(all_words))
    total_words = len(all_words)
    vocabulary_richness = unique_words / total_words if total_words > 0 else 0

    return UserProfile(
        user_id="",  # Will be set by caller
        avg_length=round(avg_length, 1),
        uses_emojis=uses_emojis,
        emoji_frequency=round(emoji_frequency, 2),
        capitalization=capitalization,
        common_phrases=common_phrases,
        avg_response_time=0,  # Would need timestamps to calculate
        punctuation_style=punctuation_style,
        vocabulary_richness=round(vocabulary_richness, 2)
    )


# ============================================================================
# VECTOR DATABASE (MOCK IMPLEMENTATION)
# ============================================================================

class MockVectorDB:
    """
    Mock vector database for storing and retrieving message embeddings.
    In production, use Pinecone, Qdrant, or pgvector.
    """

    def __init__(self):
        self.vectors: Dict[str, Dict] = {}

    def upsert(self, id: str, embedding: np.ndarray, metadata: Dict):
        """Store a vector with its metadata."""
        self.vectors[id] = {
            'embedding': embedding,
            'metadata': metadata
        }

    def query(
        self,
        vector: np.ndarray,
        top_k: int = 10,
        filter: Optional[Dict] = None
    ) -> Dict:
        """
        Find the most similar vectors.

        Args:
            vector: Query embedding
            top_k: Number of results to return
            filter: Metadata filters (e.g., {"user_id": {"$eq": "user_a"}})

        Returns:
            Dictionary with 'matches' containing scored results
        """
        results = []

        for id, data in self.vectors.items():
            # Apply filters
            if filter:
                match = True
                for key, condition in filter.items():
                    if '$eq' in condition:
                        if data['metadata'].get(key) != condition['$eq']:
                            match = False
                            break
                if not match:
                    continue

            # Calculate cosine similarity
            stored_vec = data['embedding']
            similarity = np.dot(vector, stored_vec) / (
                np.linalg.norm(vector) * np.linalg.norm(stored_vec) + 1e-8
            )

            results.append({
                'id': id,
                'score': float(similarity),
                'metadata': data['metadata']
            })

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return {'matches': results[:top_k]}


# ============================================================================
# RETRIEVAL SYSTEM
# ============================================================================

def create_embedding(text: str) -> np.ndarray:
    """
    Create an embedding for the given text.

    In production, use:
        from openai import OpenAI
        client = OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding)
    """
    # Mock embedding based on text characteristics
    features = [
        len(text) / 100,
        text.count('!') / max(len(text), 1) * 10,
        text.count('?') / max(len(text), 1) * 10,
        1.0 if any(c in text for c in '😀😂🙂❤️👍🎉') else 0.0,
        sum(1 for c in text if c.isupper()) / max(len(text), 1),
        len(text.split()) / 20,
        text.count('lol') + text.count('haha') + text.count('lmao'),
        1.0 if text.endswith('?') else 0.0,
    ]

    embedding = np.zeros(384)
    embedding[:len(features)] = features
    embedding += np.random.randn(384) * 0.01

    return embedding


def store_user_messages(
    vector_db: MockVectorDB,
    user_id: str,
    messages: List[Dict]
):
    """
    Create embeddings and store messages in vector database.

    Args:
        vector_db: The vector database instance
        user_id: User identifier
        messages: List of message records
    """
    embeddings = create_mock_embeddings(messages)

    for i, (msg, embedding) in enumerate(zip(messages, embeddings)):
        vector_db.upsert(
            id=f"{user_id}_{i}",
            embedding=embedding,
            metadata={
                'user_id': user_id,
                'context': msg['context'],
                'message_text': msg['response'],
                'timestamp': msg['timestamp']
            }
        )


def retrieve_similar_messages(
    vector_db: MockVectorDB,
    user_id: str,
    current_context: str,
    top_k: int = 10
) -> List[Dict]:
    """
    Find past messages similar to the current conversation context.

    Args:
        vector_db: The vector database instance
        user_id: Whose messages to search
        current_context: Recent conversation (what we're responding to)
        top_k: How many examples to retrieve

    Returns:
        List of retrieved examples with context, response, and similarity score
    """
    # Embed the current context
    query_embedding = create_embedding(current_context)

    # Search vector database
    results = vector_db.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"user_id": {"$eq": user_id}}
    )

    # Extract the relevant information
    retrieved = []
    for match in results['matches']:
        retrieved.append({
            'context': match['metadata']['context'],
            'response': match['metadata']['message_text'],
            'similarity': match['score']
        })

    return retrieved


# ============================================================================
# PROMPT BUILDING & RESPONSE GENERATION
# ============================================================================

def build_prompt(
    user_profile: UserProfile,
    retrieved_examples: List[Dict],
    current_conversation: str
) -> str:
    """
    Create the prompt for the LLM.

    Args:
        user_profile: Analyzed texting style
        retrieved_examples: Similar past messages
        current_conversation: The conversation to respond to

    Returns:
        Formatted prompt string
    """
    # Format the retrieved examples
    examples_text = ""
    for i, ex in enumerate(retrieved_examples, 1):
        examples_text += f"""
Example {i}:
Conversation: {ex['context']}
Their response: {ex['response']}
---
"""

    prompt = f"""You are simulating how a specific person texts based on their message history.

## Their Texting Style Profile:
- Average message length: {user_profile.avg_length} characters
- Uses emojis: {'Yes' if user_profile.uses_emojis else 'No'}
- Typical capitalization: {user_profile.capitalization}
- Punctuation style: {user_profile.punctuation_style}
- Common phrases: {', '.join(user_profile.common_phrases) if user_profile.common_phrases else 'N/A'}
- Vocabulary richness: {user_profile.vocabulary_richness}

## Examples of How They've Responded in Similar Situations:
{examples_text}

## Current Conversation:
{current_conversation}

## Instructions:
Generate a response that this person would send. Match their:
- Tone and energy level
- Message length patterns (aim for around {user_profile.avg_length} characters)
- Emoji and punctuation usage
- Vocabulary and slang
- Capitalization style ({user_profile.capitalization})

Respond with ONLY the message text, nothing else."""

    return prompt


def format_conversation(messages: List[Dict]) -> str:
    """Format a list of messages into a readable conversation string."""
    lines = []
    for msg in messages:
        sender = msg.get('sender', 'Unknown')
        text = msg.get('text', '')
        lines.append(f"{sender}: {text}")
    return '\n'.join(lines)


def simulate_response_mock(
    user_id: str,
    user_profile: UserProfile,
    retrieved_examples: List[Dict],
    conversation_history: List[Dict]
) -> str:
    """
    Generate a mock response simulating how user_id would text.

    In production, you'd use an actual LLM:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=150
        )
        return response.choices[0].message.content

    For demo purposes, we select from retrieved examples with some variation.
    """
    if not retrieved_examples:
        # Fallback responses based on user style
        if user_profile.capitalization == 'lowercase':
            return "hey! what's up"
        else:
            return "Hey! How are you?"

    # Use the most similar example as base
    best_match = retrieved_examples[0]['response']

    # Add some variation
    variations = {
        'lowercase': [
            best_match.lower(),
            best_match.lower().replace('.', ''),
        ],
        'sentence_case': [
            best_match,
            best_match + '!',
        ],
        'mixed': [
            best_match,
        ]
    }

    style_variations = variations.get(user_profile.capitalization, [best_match])

    # Pick a variation
    import random
    return random.choice(style_variations)


# ============================================================================
# MAIN SIMULATION ENGINE
# ============================================================================

class ConversationSimulator:
    """
    Main class for simulating conversations between two users.
    """

    def __init__(self):
        self.vector_db = MockVectorDB()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.messages_data: Dict[str, List[Dict]] = {}

    def setup_user(self, user_id: str, messages: List[Dict]):
        """
        Initialize a user with their message history.

        Args:
            user_id: Unique user identifier
            messages: List of message records with 'context' and 'response' keys
        """
        # Store messages
        self.messages_data[user_id] = messages

        # Analyze user style
        profile = analyze_user_style(messages)
        profile.user_id = user_id
        self.user_profiles[user_id] = profile

        # Store embeddings
        store_user_messages(self.vector_db, user_id, messages)

        print(f"Setup complete for {user_id}:")
        print(f"  - Avg message length: {profile.avg_length}")
        print(f"  - Capitalization: {profile.capitalization}")
        print(f"  - Uses emojis: {profile.uses_emojis}")
        print(f"  - Common phrases: {profile.common_phrases}")
        print()

    def generate_response(
        self,
        user_id: str,
        conversation_history: List[Dict],
        top_k: int = 8
    ) -> str:
        """
        Generate a response simulating how user_id would text.

        Args:
            user_id: The user to simulate
            conversation_history: List of previous messages
            top_k: Number of similar examples to retrieve

        Returns:
            Generated response text
        """
        # Format recent conversation as context
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        current_context = format_conversation(recent_messages)

        # Retrieve similar past situations
        retrieved = retrieve_similar_messages(
            self.vector_db,
            user_id,
            current_context,
            top_k=top_k
        )

        # Get user profile
        user_profile = self.user_profiles[user_id]

        # Build prompt (for actual LLM use)
        prompt = build_prompt(user_profile, retrieved, current_context)

        # Generate response (mock for demo)
        response = simulate_response_mock(
            user_id,
            user_profile,
            retrieved,
            conversation_history
        )

        return response

    def get_prompt_for_llm(
        self,
        user_id: str,
        conversation_history: List[Dict],
        top_k: int = 8
    ) -> str:
        """
        Get the full prompt that would be sent to an LLM.
        Useful for debugging or using with actual LLM APIs.
        """
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        current_context = format_conversation(recent_messages)

        retrieved = retrieve_similar_messages(
            self.vector_db,
            user_id,
            current_context,
            top_k=top_k
        )

        user_profile = self.user_profiles[user_id]

        return build_prompt(user_profile, retrieved, current_context)

    def simulate_conversation(
        self,
        user_a_id: str,
        user_b_id: str,
        starter_message: str,
        num_exchanges: int = 10
    ) -> List[Dict]:
        """
        Simulate a full conversation between two users.

        Args:
            user_a_id: First user (starts the conversation)
            user_b_id: Second user
            starter_message: The opening message from user_a
            num_exchanges: Number of back-and-forth exchanges

        Returns:
            List of message dictionaries with sender and text
        """
        conversation = [
            {"sender": user_a_id, "text": starter_message}
        ]

        for i in range(num_exchanges):
            # User B responds
            response_b = self.generate_response(user_b_id, conversation)
            conversation.append({
                "sender": user_b_id,
                "text": response_b
            })

            # User A responds
            response_a = self.generate_response(user_a_id, conversation)
            conversation.append({
                "sender": user_a_id,
                "text": response_a
            })

        return conversation


# ============================================================================
# EXAMPLE USAGE & DEMO
# ============================================================================

def run_demo():
    """Run a demonstration of the conversation simulator."""

    print("=" * 60)
    print("CONVERSATION SIMULATOR DEMO")
    print("=" * 60)
    print()

    # Initialize simulator
    simulator = ConversationSimulator()

    # Load mock data
    mock_data = create_mock_messages()

    # Setup users
    simulator.setup_user("user_a", mock_data["user_a"])
    simulator.setup_user("user_b", mock_data["user_b"])

    # Test retrieval
    print("=" * 60)
    print("RETRIEVAL TEST")
    print("=" * 60)
    print()

    test_context = "Them: want to get dinner tonight?"
    print(f"Query: {test_context}")
    print()

    for user_id in ["user_a", "user_b"]:
        retrieved = retrieve_similar_messages(
            simulator.vector_db,
            user_id,
            test_context,
            top_k=3
        )
        print(f"Top 3 similar messages for {user_id}:")
        for i, ex in enumerate(retrieved, 1):
            print(f"  {i}. Context: {ex['context']}")
            print(f"     Response: {ex['response']}")
            print(f"     Similarity: {ex['similarity']:.3f}")
            print()

    # Generate single response
    print("=" * 60)
    print("SINGLE RESPONSE GENERATION")
    print("=" * 60)
    print()

    conversation_so_far = [
        {"sender": "user_a", "text": "hey are you coming to the party tonight"},
        {"sender": "user_b", "text": "what party?"},
        {"sender": "user_a", "text": "mike's birthday at his place"},
    ]

    print("Conversation so far:")
    for msg in conversation_so_far:
        print(f"  {msg['sender']}: {msg['text']}")
    print()

    # Get the LLM prompt (for debugging)
    prompt = simulator.get_prompt_for_llm("user_b", conversation_so_far)
    print("Generated LLM Prompt for user_b:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()

    response = simulator.generate_response("user_b", conversation_so_far)
    print(f"user_b's simulated response: {response}")
    print()

    # Simulate full conversation
    print("=" * 60)
    print("FULL CONVERSATION SIMULATION")
    print("=" * 60)
    print()

    conversation = simulator.simulate_conversation(
        "user_a",
        "user_b",
        "hey wanna hang out tonight?",
        num_exchanges=5
    )

    print("Simulated conversation:")
    print("-" * 40)
    for msg in conversation:
        print(f"{msg['sender']}: {msg['text']}")
    print("-" * 40)
    print()

    print("Demo complete!")


if __name__ == "__main__":
    run_demo()
