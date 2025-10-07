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
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key":
            self.client = None
            self.model = "gpt-4o-mini"  # Better model for natural conversation
            self.demo_mode = True
            print("[WARN] OpenAI API key not found. Running in demo mode with mock responses.")
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o-mini"  # Better model for natural conversation
            self.demo_mode = False
            print("[OK] OpenAI API key found. Using real OpenAI API.")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.9,  # Higher temperature for more natural, varied responses
        max_tokens: Optional[int] = 50,  # Limit tokens for short, natural responses
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using OpenAI API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: OpenAI model to use (defaults to gpt-3.5-turbo)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API call
            
        Returns:
            Dictionary containing the chat completion response
        """
        try:
            if not self.client or self.demo_mode:
                # Return demo response
                print("[DEMO] Using demo mode response")
                return self._get_demo_response(messages)
            
            print("[API] Using real OpenAI API")
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
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
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with conversation history context
        
        Args:
            conversation_history: Previous messages in the conversation
            user_message: The new user message
            system_prompt: Optional system prompt to set context
            
        Returns:
            Dictionary containing the chat response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            print(f"[PROMPT] System prompt added to OpenAI messages (length: {len(system_prompt)} chars)")
            print(f"[PROMPT] System prompt preview: {system_prompt[:150]}...")
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
            presence_penalty=0.6,  # Reduce repetition
            frequency_penalty=0.6  # Reduce repetition
        )
    
    def _get_demo_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate demo responses for testing without OpenAI API
        
        Args:
            messages: List of message dictionaries
            
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
        
        # Prevent repetition by checking conversation history
        if response.lower() in conversation_history:
            # If we've said this before, try a different response
            alternative_responses = [
                "Yeah", "Right", "Cool", "Nice", "Sure", "Okay", "Hmm", "Interesting", 
                "Really?", "Wow", "Awesome", "Great", "Good", "Bad", "Sad", "Happy", 
                "Tired", "Bored", "Excited", "Nervous", "Scared", "Confused", "Surprised", 
                "Disappointed", "Proud", "Jealous", "Lonely", "Stressed", "Relaxed", 
                "Motivated", "Demotivated", "Inspired", "Creative", "Artistic", "Musical", 
                "Sporty", "Academic", "Professional", "Casual", "Formal", "Informal", 
                "Friendly", "Polite", "Rude", "Mean", "Kind", "Generous", "Selfish", 
                "Honest", "Dishonest", "Trustworthy", "Suspicious", "Confident", "Shy", 
                "Outgoing", "Introverted", "Extroverted", "Social", "Antisocial", "Funny", 
                "Serious", "Silly", "Mature", "Immature", "Wise", "Foolish", "Smart", 
                "Stupid", "Clever", "Dumb", "Genius", "Average", "Special", "Normal", 
                "Weird", "Strange", "Different", "Unique", "Common", "Rare", "Popular", 
                "Unpopular", "Famous", "Unknown", "Successful", "Unsuccessful", "Rich", 
                "Poor", "Wealthy", "Broke", "Expensive", "Cheap", "Free", "Paid", "Worth", 
                "Value", "Price", "Cost", "Money", "Cash", "Card", "Bank", "Account", 
                "Balance", "Debt", "Credit", "Loan", "Mortgage", "Rent", "Bills", "Salary", 
                "Wage", "Income", "Profit", "Loss", "Gain", "Win", "Lose", "Tie", "Draw", 
                "Match", "Game", "Play", "Fun", "Boring", "Interesting", "Exciting", 
                "Amazing", "Incredible", "Fantastic", "Terrible", "Awful", "Horrible", 
                "Disgusting", "Gross", "Nasty", "Clean", "Dirty", "Fresh", "Old", "New", 
                "Young", "Big", "Small", "Huge", "Tiny", "Large", "Little", "Massive", 
                "Mini", "Giant", "Micro", "Macro", "Mega", "Super", "Ultra", "Hyper", 
                "Giga", "Tera", "Peta", "Exa", "Zetta", "Yotta", "Sup", "Nm", "Hbu", 
                "Same", "Right", "Exactly", "Totally", "Definitely", "Absolutely", 
                "Probably", "Maybe", "Possibly", "Definitely not", "No way", "Yes way", 
                "Really", "Seriously", "Honestly", "Tbh", "Fr", "No cap", "Facts", 
                "True", "False", "Lie", "Truth", "Real", "Fake", "Genuine", "Authentic", 
                "Legit", "Illegitimate", "Valid", "Invalid", "Correct", "Incorrect", 
                "Right", "Wrong", "Accurate", "Inaccurate", "Precise", "Imprecise", 
                "Exact", "Approximate", "Close", "Far", "Near", "Distant", "Close by", 
                "Far away", "Nearby", "Local", "Remote", "Downtown", "Uptown", "Suburban", 
                "Rural", "Urban", "City", "Town", "Village", "Hamlet", "Metropolis", 
                "Megalopolis", "Conurbation", "Agglomeration", "Settlement", "Community", 
                "Neighborhood", "District", "Ward", "Precinct", "Zone", "Area", "Region", 
                "Territory", "Province", "State", "Country", "Nation", "Continent", 
                "Hemisphere", "Globe", "World", "Earth", "Planet", "Universe", "Cosmos", 
                "Galaxy", "Solar system", "Star", "Sun", "Moon", "Planet", "Asteroid", 
                "Comet", "Meteor", "Meteorite", "Meteoroid", "Satellite", "Spacecraft", 
                "Rocket", "Shuttle", "Station", "Base", "Facility", "Building", "Structure", 
                "Construction", "Architecture", "Design", "Plan", "Blueprint", "Sketch", 
                "Drawing", "Painting", "Sculpture", "Art", "Artwork", "Masterpiece", 
                "Creation", "Work", "Piece", "Item", "Object", "Thing", "Stuff", 
                "Material", "Substance", "Matter", "Element", "Compound", "Mixture", 
                "Solution", "Suspension", "Colloid", "Emulsion", "Foam", "Bubble", "Drop", 
                "Drip", "Spill", "Leak", "Flow", "Stream", "River", "Lake", "Ocean", 
                "Sea", "Pond", "Pool", "Puddle", "Water", "Liquid", "Fluid", "Gas", 
                "Vapor", "Steam", "Smoke", "Fog", "Mist", "Haze", "Cloud", "Sky", "Air", 
                "Atmosphere", "Weather", "Climate", "Temperature", "Heat", "Cold", "Warm", 
                "Cool", "Hot", "Freezing", "Boiling", "Melting", "Freezing", "Solid", 
                "Liquid", "Gas", "Plasma", "Crystal", "Ice", "Snow", "Rain", "Storm", 
                "Wind", "Breeze", "Gust", "Hurricane", "Tornado", "Cyclone", "Typhoon", 
                "Monsoon", "Drought", "Flood", "Earthquake", "Volcano", "Tsunami", 
                "Avalanche", "Landslide", "Mudslide", "Rockslide", "Snowslide", 
                "Ice slide", "Glacier", "Iceberg", "Frozen", "Thawed", "Melted", 
                "Solidified", "Liquefied", "Vaporized", "Condensed", "Evaporated", 
                "Sublimated", "Deposited", "Precipitated", "Crystallized", "Dissolved", 
                "Saturated", "Unsaturated", "Supersaturated", "Concentrated", "Diluted", 
                "Pure", "Impure", "Clean", "Dirty", "Contaminated", "Polluted", "Toxic", 
                "Poisonous", "Harmful", "Dangerous", "Safe", "Secure", "Protected", 
                "Exposed", "Vulnerable", "Defenseless", "Helpless", "Powerless", "Weak", 
                "Strong", "Powerful", "Mighty", "Forceful", "Intense", "Mild", "Gentle", 
                "Soft", "Hard", "Tough", "Rough", "Smooth", "Coarse", "Fine", "Thick", 
                "Thin", "Wide", "Narrow", "Broad", "Deep", "Shallow", "High", "Low", 
                "Tall", "Short", "Long", "Brief", "Quick", "Slow", "Fast", "Rapid", 
                "Swift", "Speedy"
            ]
            
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


# Create singleton instance
openai_service = OpenAIService()
