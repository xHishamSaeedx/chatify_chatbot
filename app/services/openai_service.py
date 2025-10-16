"""
OpenAI service for ChatGPT integration
"""

from typing import Optional, List, Dict, Any
from openai import OpenAI
from app.core.config import settings


class OpenAIService:
    """OpenAI service for ChatGPT integration"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        print(f"[KEY] OpenAI API Key loaded: {settings.OPENAI_API_KEY[:10]}..." if settings.OPENAI_API_KEY else "[KEY] No OpenAI API Key found")
        
        # Try to initialize OpenAI, fall back to demo mode if it fails
        try:
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key":
                raise ValueError("No API key configured")
            
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o-mini"
            self.demo_mode = False
            print("[OK] OpenAI API key found. Using real OpenAI API.")
        except Exception as e:
            print(f"[WARN] OpenAI initialization failed: {e}")
            print("[DEMO] Falling back to DEMO MODE with pre-built responses")
            self.client = None
            self.model = "demo-mode"
            self.demo_mode = True
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.9,  # Higher temperature for more natural, varied responses
        max_tokens: Optional[int] = 50,  # Limit tokens for short, natural responses
        enthusiasm_level: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using OpenAI API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: OpenAI model to use (defaults to gpt-3.5-turbo)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            enthusiasm_level: Current enthusiasm level (1-5) for demo mode
            **kwargs: Additional parameters for the API call
            
        Returns:
            Dictionary containing the chat completion response
        """
        try:
            print("\n" + "="*80)
            print("[OPENAI] GENERATING AI RESPONSE")
            print("="*80)
            print(f"Model: {model or self.model}")
            print(f"Temperature: {temperature}")
            print(f"Max Tokens: {max_tokens}")
            print(f"Enthusiasm Level: {enthusiasm_level}/5")
            print(f"Message Count: {len(messages)}")
            if messages:
                last_msg = messages[-1]
                print(f"Last Message: {last_msg.get('content', '')[:100]}...")
            print("="*80 + "\n")
            
            if not self.client or self.demo_mode:
                # Return demo response
                print("[DEMO] Using demo mode response")
                return self._get_demo_response(messages, enthusiasm_level)
            
            print("[API] ⚡ Calling real OpenAI API...")
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            ai_content = response.choices[0].message.content
            print("\n" + "="*80)
            print("[OPENAI] AI RESPONSE RECEIVED")
            print("="*80)
            print(f"Response: {ai_content}")
            print(f"Prompt Tokens: {response.usage.prompt_tokens}")
            print(f"Completion Tokens: {response.usage.completion_tokens}")
            print(f"Total Tokens: {response.usage.total_tokens}")
            print(f"Model Used: {response.model}")
            print("="*80 + "\n")
            
            return {
                "success": True,
                "content": ai_content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    async def simple_chat(self, user_message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Simple chat interface for basic conversations
        
        Args:
            user_message: The user's message
            system_prompt: Optional system prompt to set context
            
        Returns:
            Dictionary containing the chat response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat_completion(messages)
    
    async def conversational_chat(
        self,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        system_prompt: Optional[str] = None,
        enthusiasm_level: int = 3
    ) -> Dict[str, Any]:
        """
        Chat with conversation history context
        
        Args:
            conversation_history: Previous messages in the conversation
            user_message: The new user message
            system_prompt: Optional system prompt to set context
            enthusiasm_level: Current enthusiasm level (1-5) that affects response style
            
        Returns:
            Dictionary containing the chat response
        """
        messages = []
        
        if system_prompt:
            # Add enthusiasm context to system prompt
            enthusiasm_context = self._get_enthusiasm_context(enthusiasm_level)
            enhanced_prompt = f"{system_prompt}\n\n{enthusiasm_context}"
            
            messages.append({"role": "system", "content": enhanced_prompt})
            print(f"[PROMPT] System prompt added to OpenAI messages (length: {len(enhanced_prompt)} chars)")
            print(f"[PROMPT] System prompt preview: {enhanced_prompt[:150]}...")
            print(f"[ENTHUSIASM] Current level: {enthusiasm_level}")
        else:
            print(f"[WARN] No system prompt provided - using default OpenAI behavior")
        
        # Add conversation history (limit to last 10 messages for context)
        messages.extend(conversation_history[-10:])
        print(f"[CHAT] Conversation history: {len(conversation_history)} messages")
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Use optimized settings for natural conversation
        return await self.chat_completion(
            messages, 
            temperature=0.9,  # Higher temperature for more natural responses
            max_tokens=50,    # Short responses like texting
            enthusiasm_level=enthusiasm_level,  # Pass enthusiasm level
            presence_penalty=0.6,  # Reduce repetition
            frequency_penalty=0.6  # Reduce repetition
        )
    
    def _get_enthusiasm_context(self, enthusiasm_level: int) -> str:
        """
        Get enthusiasm context based on current level
        
        Args:
            enthusiasm_level: Current enthusiasm level (1-5)
            
        Returns:
            Enthusiasm context string to enhance system prompt
        """
        enthusiasm_contexts = {
            1: "CURRENT MOOD: Very low enthusiasm. You're feeling bored, uninterested, and giving minimal responses. Use very short replies (1-2 words), seem disengaged, and don't ask questions. Examples: 'ok', 'sure', 'meh', 'whatever'.",
            
            2: "CURRENT MOOD: Low enthusiasm. You're mildly disinterested but still responding. Keep responses short (2-4 words), show limited engagement. Examples: 'cool i guess', 'that's nice', 'maybe', 'alright'.",
            
            3: "CURRENT MOOD: Neutral enthusiasm. You're casually engaged, giving normal responses. Use typical short responses (3-6 words), moderate interest. Examples: 'that sounds cool', 'nice to know', 'yeah makes sense'.",
            
            4: "CURRENT MOOD: High enthusiasm. You're interested and engaged. Give slightly longer responses (4-8 words), show genuine interest, maybe ask a question. Examples: 'that's really cool!', 'wow tell me more', 'that sounds amazing'.",
            
            5: "CURRENT MOOD: Very high enthusiasm. You're excited and highly engaged. Give enthusiastic responses (5-10 words), use exclamation points, ask follow-up questions. Examples: 'omg that's so awesome!', 'wow that sounds incredible!', 'tell me everything!'."
        }
        
        return enthusiasm_contexts.get(enthusiasm_level, enthusiasm_contexts[3])
    
    def _get_demo_response(self, messages: List[Dict[str, str]], enthusiasm_level: int = 3) -> Dict[str, Any]:
        """
        Generate demo responses for testing without OpenAI API
        
        Args:
            messages: List of message dictionaries
            enthusiasm_level: Current enthusiasm level (1-5)
            
        Returns:
            Dictionary containing the demo response
        """
        import random
        import time
        
        # Get conversation history to prevent repetition
        conversation_history = []
        for msg in messages[-10:]:  # Get last 10 messages
            if msg["role"] == "assistant":
                conversation_history.append(msg["content"].lower())
        
        # Debug: Print conversation history
        print(f"[DEBUG] Conversation history: {conversation_history}")
        print(f"[DEBUG] User message: {user_message}")
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"].lower()
                break
        
        # Simple, natural responses with basic shortforms
        demo_responses = {
            # Basic greetings
            "hello": "Hey! What's up?",
            "hi": "Hi there! How's it going?",
            "hey": "Hey! What's up?",
            
            # Common shortforms
            "wyd": "Just chilling, you?",
            "wbu": "Same here", 
            "wbuu": "Same here",
            "hru": "I'm good, you?",
            "hbu": "How about you?",
            "lmao": "Haha",
            "lol": "Haha",
            "sup": "Not much, you?",
            "nm": "Nothing much",
            "omg": "Right?!",
            "tbh": "I agree",
            "fr": "For real",
            "idk": "Me neither",
            "ikr": "I know right",
            "btw": "By the way",
            "nvm": "Never mind",
            "ty": "Np",
            "yw": "Np",
            "np": "Sure",
            
            # Basic responses
            "how are you": "I'm good, thanks! You?",
            "what is": "What do you mean?",
            "help": "Sure, what do you need?",
            "bye": "See you later!",
            "thanks": "Np!",
            "name": "I'm Alex. What's yours?",
            "weather": "Nice day today!",
            "time": "It's getting late",
            "joke": "Why did the chicken cross the road?",
            "food": "I'm hungry",
            "music": "What music do you like?",
            "work": "Work can be tough",
            "study": "Learning is important",
            
            # Simple reactions
            "sure": "Sure thing",
            "ok": "Okay",
            "yeah": "Yeah",
            "nah": "Nah",
            "maybe": "Maybe",
            "cool": "Cool",
            "nice": "Nice",
            "awesome": "Awesome",
            "great": "Great",
            "good": "Good",
            "bad": "That sucks",
            "sad": "That's sad",
            "happy": "That's great",
            "tired": "Get some rest",
            "bored": "Let's do something",
            "excited": "That's exciting",
            "nervous": "Don't worry",
            "scared": "It's okay",
            "confused": "I get it",
            "surprised": "Wow really?",
            "lonely": "I'm here",
            "stressed": "Take it easy",
            "relaxed": "That's good",
            "motivated": "That's great",
            "demotivated": "You got this",
            
            # Basic questions
            "really": "Really?",
            "seriously": "Seriously?",
            "honestly": "Honestly",
            "same": "Same here",
            "right": "Right",
            "exactly": "Exactly",
            "totally": "Totally",
            "definitely": "Definitely",
            "absolutely": "Absolutely",
            "probably": "Probably",
            "maybe": "Maybe",
            "no way": "No way",
            "yes way": "Yes way"
        }
        
        # Find the best matching response
        response = "That's cool! Tell me more"
        
        # Check for specific patterns first
        if "personality" in user_message or "type" in user_message:
            response = "I'm pretty chill and easy going. What about you?"
        elif "think about" in user_message or "opinion" in user_message:
            if "car" in user_message:
                response = "Cars are cool! Do you have one?"
            elif "music" in user_message:
                response = "Music is great! What do you listen to?"
            else:
                response = "Hmm interesting question. What do you think?"
        elif "female" in user_message or "woman" in user_message or "girl" in user_message:
            response = "Yeah, I am"
        elif "male" in user_message or "man" in user_message or "guy" in user_message:
            response = "Nah, I'm not"
        elif "are you" in user_message:
            response = "What do you think?"
        elif "what do you" in user_message or "do you like" in user_message:
            response = "I like a lot of things. What about you?"
        elif "where" in user_message and ("from" in user_message or "live" in user_message):
            response = "I'm from around here. You?"
        elif "same" in user_message or "samee" in user_message:
            response = "Nice"
        elif "great" in user_message:
            response = "Nice"
        elif "nice" in user_message:
            response = "Yeah"
        elif "yeah" in user_message:
            response = "Cool"
        elif "cool" in user_message:
            response = "Right"
        elif "right" in user_message:
            response = "So what's up?"
        elif "what's up" in user_message or "whats up" in user_message:
            response = "Not much, you?"
        elif "not much" in user_message:
            response = "Same here"
        else:
            # Check other keywords
            found = False
            for keyword, demo_response in demo_responses.items():
                if keyword in user_message:
                    response = demo_response
                    found = True
                    break
            
            # If no keyword match, give contextual responses
            if not found:
                if "?" in user_message:
                    response = "Hmm good question. What do you think?"
                else:
                    response = "Oh really? That's interesting"
        
        # Add random shortform responses (45% chance)
        if random.random() < 0.45:
            shortform_responses = {
                "wyd": "wydd",
                "hru": "hruu", 
                "hbu": "hbuu",
                "nice": "nicee",
                "cool": "cooll",
                "yeah": "yeahh",
                "ok": "okk",
                "sure": "suree",
                "right": "rightt",
                "good": "goodd",
                "bad": "badd",
                "sad": "sadd",
                "mad": "madd",
                "tired": "tiredd",
                "bored": "boredd",
                "excited": "excitedd",
                "happy": "happyy",
                "angry": "angryy",
                "nervous": "nervouss",
                "scared": "scaredd",
                "confused": "confusedd",
                "surprised": "surprisedd",
                "disappointed": "disappointedd",
                "proud": "proudd",
                "jealous": "jealouss",
                "lonely": "lonelyy",
                "stressed": "stressedd",
                "relaxed": "relaxedd",
                "motivated": "motivatedd",
                "demotivated": "demotivatedd",
                "inspired": "inspiredd",
                "creative": "creativee",
                "artistic": "artistice",
                "musical": "musicale",
                "sporty": "sportyy",
                "academic": "academice",
                "professional": "professionale",
                "casual": "casuale",
                "formal": "formale",
                "informal": "informale",
                "friendly": "friendlyy",
                "polite": "politee",
                "rude": "rudee",
                "mean": "meann",
                "kind": "kindd",
                "generous": "generouss",
                "selfish": "selfishh",
                "honest": "honestt",
                "dishonest": "dishonestt",
                "trustworthy": "trustworthyye",
                "suspicious": "suspiciouss",
                "confident": "confidentt",
                "shy": "shyy",
                "outgoing": "outgoingg",
                "introverted": "introvertedd",
                "extroverted": "extrovertedd",
                "social": "sociall",
                "antisocial": "antisociall",
                "funny": "funnyy",
                "serious": "seriouss",
                "silly": "sillyy",
                "mature": "maturee",
                "immature": "immaturee",
                "wise": "wisee",
                "foolish": "foolishh",
                "smart": "smartt",
                "stupid": "stupidd",
                "clever": "cleverr",
                "dumb": "dumbb",
                "genius": "geniuss",
                "average": "averagee",
                "special": "speciall",
                "normal": "normall",
                "weird": "weirdd",
                "strange": "strangee",
                "different": "differentt",
                "unique": "uniquee",
                "common": "commonn",
                "rare": "raree",
                "popular": "popularr",
                "unpopular": "unpopularr",
                "famous": "famouss",
                "unknown": "unknownn",
                "successful": "successfull",
                "unsuccessful": "unsuccessfull",
                "rich": "richh",
                "poor": "poorr",
                "wealthy": "wealthyy",
                "broke": "brokee",
                "expensive": "expensivee",
                "cheap": "cheapp",
                "free": "freee",
                "paid": "paidd",
                "worth": "worthh",
                "value": "valuee",
                "price": "pricee",
                "cost": "costt",
                "money": "moneyy",
                "cash": "cashh",
                "card": "cardd",
                "bank": "bankk",
                "account": "accountt",
                "balance": "balancee",
                "debt": "debtt",
                "credit": "creditt",
                "loan": "loann",
                "mortgage": "mortgagee",
                "rent": "rentt",
                "bills": "billss",
                "salary": "salaryy",
                "wage": "wagee",
                "income": "incomee",
                "profit": "profitt",
                "loss": "losss",
                "gain": "gainn",
                "win": "winn",
                "lose": "losee",
                "tie": "tiee",
                "draw": "draww",
                "match": "matchh",
                "game": "gamee",
                "play": "playy",
                "fun": "funn",
                "boring": "boringg",
                "interesting": "interestingg",
                "exciting": "excitingg",
                "amazing": "amazingg",
                "incredible": "incrediblee",
                "fantastic": "fantasticc",
                "terrible": "terriblee",
                "awful": "awfull",
                "horrible": "horriblee",
                "disgusting": "disgustingg",
                "gross": "grosss",
                "nasty": "nastyy",
                "clean": "cleann",
                "dirty": "dirtyy",
                "fresh": "freshh",
                "old": "oldd",
                "new": "neww",
                "young": "youngg",
                "big": "bigg",
                "small": "smalll",
                "huge": "hugee",
                "tiny": "tinyy",
                "large": "largee",
                "little": "littlee",
                "massive": "massivee",
                "mini": "minii",
                "giant": "giantt",
                "micro": "microo",
                "macro": "macroo",
                "mega": "megaa",
                "super": "superr",
                "ultra": "ultraa",
                "hyper": "hyperr",
                "giga": "gigaa",
                "tera": "teraa",
                "peta": "petaa",
                "exa": "exaa",
                "zetta": "zettaa",
                "yotta": "yottaa",
                "sup": "supp",
                "nm": "nmm",
                "hbu": "hbuu",
                "same": "samee",
                "right": "rightt",
                "exactly": "exactlyy",
                "totally": "totallyy",
                "definitely": "definitelyy",
                "absolutely": "absolutelyy",
                "probably": "probablyy",
                "maybe": "maybee",
                "possibly": "possiblyy",
                "definitely not": "definitely nott",
                "no way": "no wayy",
                "yes way": "yes wayy",
                "really": "reallyy",
                "seriously": "seriouslyy",
                "honestly": "honestlyy",
                "tbh": "tbh",
                "fr": "fr",
                "no cap": "no capp",
                "facts": "factss",
                "true": "truee",
                "false": "falsee",
                "lie": "liee",
                "truth": "truthh",
                "real": "reall",
                "fake": "fakee",
                "genuine": "genuinee",
                "authentic": "authenticc",
                "legit": "legitt",
                "illegitimate": "illegitimatee",
                "valid": "validd",
                "invalid": "invalidd",
                "correct": "correctt",
                "incorrect": "incorrectt",
                "right": "rightt",
                "wrong": "wrongg",
                "accurate": "accuratee",
                "inaccurate": "inaccuratee",
                "precise": "precisee",
                "imprecise": "imprecisee",
                "exact": "exactt",
                "approximate": "approximatee",
                "close": "closee",
                "far": "farr",
                "near": "nearr",
                "distant": "distantt",
                "close by": "close byy",
                "far away": "far awayy",
                "nearby": "nearbyy",
                "local": "locall",
                "remote": "remotee",
                "downtown": "downtownn",
                "uptown": "uptownn",
                "suburban": "suburbann",
                "rural": "rurall",
                "urban": "urbann",
                "city": "cityy",
                "town": "townn",
                "village": "villagee",
                "hamlet": "hamlett",
                "metropolis": "metropoliss",
                "megalopolis": "megalopoliss",
                "conurbation": "conurbationn",
                "agglomeration": "agglomerationn",
                "settlement": "settlementt",
                "community": "communityy",
                "neighborhood": "neighborhoodd",
                "district": "districtt",
                "ward": "wardd",
                "precinct": "precinctt",
                "zone": "zonee",
                "area": "areaa",
                "region": "regionn",
                "territory": "territoryy",
                "province": "provincee",
                "state": "statee",
                "country": "countryy",
                "nation": "nationn",
                "continent": "continentt",
                "hemisphere": "hemispheree",
                "globe": "globee",
                "world": "worldd",
                "earth": "earthh",
                "planet": "planett",
                "universe": "universe",
                "cosmos": "cosmoss",
                "galaxy": "galaxy",
                "solar system": "solar systemm",
                "star": "starr",
                "sun": "sunn",
                "moon": "moonn",
                "planet": "planett",
                "asteroid": "asteroidd",
                "comet": "comett",
                "meteor": "meteorr",
                "meteorite": "meteoritee",
                "meteoroid": "meteoroidd",
                "satellite": "satellitee",
                "spacecraft": "spacecraftt",
                "rocket": "rockett",
                "shuttle": "shuttlee",
                "station": "stationn",
                "base": "basee",
                "facility": "facilityy",
                "building": "buildingg",
                "structure": "structuree",
                "construction": "constructionn",
                "architecture": "architecturee",
                "design": "designn",
                "plan": "plann",
                "blueprint": "blueprintt",
                "sketch": "sketchh",
                "drawing": "drawingg",
                "painting": "paintingg",
                "sculpture": "sculpturee",
                "art": "artt",
                "artwork": "artworkk",
                "masterpiece": "masterpiecee",
                "creation": "creationn",
                "work": "workk",
                "piece": "piecee",
                "item": "itemm",
                "object": "objectt",
                "thing": "thingg",
                "stuff": "stufff",
                "material": "materiall",
                "substance": "substancee",
                "matter": "matterr",
                "element": "elementt",
                "compound": "compoundd",
                "mixture": "mixturee",
                "solution": "solutionn",
                "suspension": "suspensionn",
                "colloid": "colloidd",
                "emulsion": "emulsionn",
                "foam": "foamm",
                "bubble": "bubblee",
                "drop": "dropp",
                "drip": "dripp",
                "spill": "spilll",
                "leak": "leakk",
                "flow": "floww",
                "stream": "streamm",
                "river": "riverr",
                "lake": "lakee",
                "ocean": "oceann",
                "sea": "seaa",
                "pond": "pondd",
                "pool": "pooll",
                "puddle": "puddlee",
                "water": "waterr",
                "liquid": "liquidd",
                "fluid": "fluidd",
                "gas": "gass",
                "vapor": "vaporr",
                "steam": "steamm",
                "smoke": "smokee",
                "fog": "fogg",
                "mist": "mistt",
                "haze": "hazee",
                "cloud": "cloudd",
                "sky": "skyy",
                "air": "airr",
                "atmosphere": "atmospheree",
                "weather": "weatherr",
                "climate": "climatee",
                "temperature": "temperaturee",
                "heat": "heatt",
                "cold": "coldd",
                "warm": "warmm",
                "cool": "cooll",
                "hot": "hott",
                "freezing": "freezingg",
                "boiling": "boilingg",
                "melting": "meltingg",
                "freezing": "freezingg",
                "solid": "solidd",
                "liquid": "liquidd",
                "gas": "gass",
                "plasma": "plasmaa",
                "crystal": "crystall",
                "ice": "icee",
                "snow": "snoww",
                "rain": "rainn",
                "storm": "stormm",
                "wind": "windd",
                "breeze": "breezee",
                "gust": "gustt",
                "hurricane": "hurricanee",
                "tornado": "tornadoo",
                "cyclone": "cyclonee",
                "typhoon": "typhoonn",
                "monsoon": "monsoonn",
                "drought": "droughtt",
                "flood": "floodd",
                "earthquake": "earthquakee",
                "volcano": "volcanoo",
                "tsunami": "tsunamii",
                "avalanche": "avalanchee",
                "landslide": "landslidee",
                "mudslide": "mudslidee",
                "rockslide": "rockslidee",
                "snowslide": "snowslidee",
                "ice slide": "ice slidee",
                "glacier": "glacierr",
                "iceberg": "iceberg",
                "frozen": "frozenn",
                "thawed": "thawedd",
                "melted": "meltedd",
                "solidified": "solidifiedd",
                "liquefied": "liquefiedd",
                "vaporized": "vaporizedd",
                "condensed": "condensedd",
                "evaporated": "evaporatedd",
                "sublimated": "sublimatedd",
                "deposited": "depositedd",
                "precipitated": "precipitatedd",
                "crystallized": "crystallizedd",
                "dissolved": "dissolvedd",
                "saturated": "saturatedd",
                "unsaturated": "unsaturatedd",
                "supersaturated": "supersaturatedd",
                "concentrated": "concentratedd",
                "diluted": "dilutedd",
                "pure": "puree",
                "impure": "impuree",
                "clean": "cleann",
                "dirty": "dirtyy",
                "contaminated": "contaminatedd",
                "polluted": "pollutedd",
                "toxic": "toxicc",
                "poisonous": "poisonouss",
                "harmful": "harmfull",
                "dangerous": "dangerouss",
                "safe": "safee",
                "secure": "securee",
                "protected": "protectedd",
                "exposed": "exposedd",
                "vulnerable": "vulnerablee",
                "defenseless": "defenselesss",
                "helpless": "helplesss",
                "powerless": "powerlesss",
                "weak": "weakk",
                "strong": "strongg",
                "powerful": "powerfull",
                "mighty": "mighty",
                "forceful": "forcefull",
                "intense": "intensee",
                "mild": "mildd",
                "gentle": "gentlee",
                "soft": "softt",
                "hard": "hardd",
                "tough": "toughh",
                "rough": "roughh",
                "smooth": "smoothh",
                "coarse": "coarsee",
                "fine": "finee",
                "thick": "thickk",
                "thin": "thinn",
                "wide": "widee",
                "narrow": "narroww",
                "broad": "broadd",
                "deep": "deepp",
                "shallow": "shalloww",
                "high": "highh",
                "low": "loww",
                "tall": "talll",
                "short": "shortt",
                "long": "longg",
                "brief": "briefe",
                "quick": "quickk",
                "slow": "sloww",
                "fast": "fastt",
                "rapid": "rapidd",
                "swift": "swiftt",
                "speedy": "speedyy",
                "fast": "fastt",
                "quick": "quickk",
                "rapid": "rapidd",
                "swift": "swiftt",
                "speedy": "speedyy",
                "fast": "fastt",
                "quick": "quickk",
                "rapid": "rapidd",
                "swift": "swiftt",
                "speedy": "speedyy"
            }
            
            # Check if we can use a shortform version
            for full_word, shortform in shortform_responses.items():
                if full_word in response.lower():
                    response = response.replace(full_word, shortform)
                    break
        
        # Apply enthusiasm-based modifications to response
        response = self._apply_enthusiasm_to_response(response, enthusiasm_level)
        
        # Prevent repetition by checking conversation history
        if response.lower() in conversation_history:
            # If we've said this before, try a different response based on enthusiasm
            alternative_responses = self._get_enthusiasm_based_alternatives(enthusiasm_level)
            
            # Pick a random alternative that hasn't been used recently
            for alt_response in alternative_responses:
                if alt_response.lower() not in conversation_history:
                    response = alt_response
                    break
        
        # Add rare emojis (only 3 types, very rarely)
        if random.random() < 0.1:  # 10% chance
            if "lol" in user_message or "haha" in user_message or "funny" in user_message:
                response = response.replace("Haha", "Haha 😂")
            elif "sad" in user_message or "bad" in user_message or "tired" in user_message:
                response = response.replace("That's sad", "That's sad 😔")
            elif "confused" in user_message or "what" in user_message:
                response = response.replace("What", "What 🤔")
        
        # Add response delay based on length (1-2 seconds)
        response_length = len(response)
        if response_length < 10:
            delay = 1.0
        elif response_length < 20:
            delay = 1.5
        else:
            delay = 2.0
        
        # Debug: Print final response
        print(f"[DEBUG] Final response: {response}")
        print(f"[DEBUG] Is repeating? {response.lower() in conversation_history}")
        
        # Simulate typing delay
        time.sleep(delay)
        
        return {
            "success": True,
            "content": response,
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "total_tokens": 80
            },
            "model": "demo-mode"
        }
    
    def _apply_enthusiasm_to_response(self, response: str, enthusiasm_level: int) -> str:
        """
        Apply enthusiasm-based modifications to a response
        
        Args:
            response: Original response
            enthusiasm_level: Current enthusiasm level (1-5)
            
        Returns:
            Modified response based on enthusiasm
        """
        if enthusiasm_level == 1:
            # Very low enthusiasm - make responses shorter and more monotone
            if len(response) > 10:
                response = response.split()[0]  # Just first word
            response = response.lower()
            
        elif enthusiasm_level == 2:
            # Low enthusiasm - shorter responses, less punctuation
            words = response.split()
            if len(words) > 3:
                response = " ".join(words[:3])
            response = response.replace("!", "").replace("?", "")
            
        elif enthusiasm_level == 4:
            # High enthusiasm - add some excitement
            if not response.endswith("!") and not response.endswith("?"):
                if "cool" in response.lower() or "nice" in response.lower() or "awesome" in response.lower():
                    response += "!"
            
        elif enthusiasm_level == 5:
            # Very high enthusiasm - add excitement and maybe elongate words
            if not response.endswith("!"):
                response += "!"
            # Elongate words occasionally
            if random.random() < 0.3:
                response = response.replace("cool", "coool").replace("nice", "nicee").replace("wow", "woww")
        
        return response
    
    def _get_enthusiasm_based_alternatives(self, enthusiasm_level: int) -> List[str]:
        """
        Get alternative responses based on enthusiasm level
        
        Args:
            enthusiasm_level: Current enthusiasm level (1-5)
            
        Returns:
            List of alternative responses
        """
        alternatives = {
            1: ["ok", "sure", "k", "meh", "whatever", "fine"],
            2: ["alright", "i guess", "maybe", "cool i guess", "that's nice"],
            3: ["yeah", "cool", "nice", "right", "okay", "sure thing"],
            4: ["that's cool!", "nice one", "awesome", "really?", "wow cool"],
            5: ["omg yes!", "that's amazing!", "wow awesome!", "so cool!", "incredible!"]
        }
        
        return alternatives.get(enthusiasm_level, alternatives[3])


# Create singleton instance
openai_service = OpenAIService()
