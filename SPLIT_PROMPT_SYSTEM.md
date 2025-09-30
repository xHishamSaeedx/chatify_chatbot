# Split Prompt System Documentation

## Overview

The Split Prompt System separates AI behavior control into two distinct, manageable parts:

1. **Universal Rules** - Critical rules that apply to ALL personalities
2. **Personality Prompts** - Unique descriptions specific to each personality

This architecture allows you to update global behavior rules without modifying individual personalities, making management more efficient and consistent.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Session Created                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Session Service (_get_system_prompt)            │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌───────────────────────────┐  ┌──────────────────────────────┐
│   Firebase: Universal     │  │  Firebase: Personality       │
│   /settings/universalRules│  │  /templates/{personality_id} │
│                           │  │                              │
│  • rules                  │  │  • personalityPrompt         │
│  • version                │  │  • name, title, etc.         │
│  • enabled                │  │                              │
└───────────────────────────┘  └──────────────────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
                ┌───────────────────────┐
                │  Combined System      │
                │  Prompt = Rules +     │
                │  Personality          │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  OpenAI ChatGPT API   │
                └───────────────────────┘
```

## Firebase Structure

### Before (Old System)

```json
{
  "templates": {
    "baddie": {
      "systemPrompt": "RULES + PERSONALITY ALL MIXED TOGETHER..."
    }
  }
}
```

**Problem:** To change a single rule, you had to edit every single personality.

### After (New System)

```json
{
  "settings": {
    "universalRules": {
      "rules": "CRITICAL RULES:\n- Keep responses short\n- Use casual language\n...",
      "version": "1.0",
      "enabled": true,
      "updatedAt": "2024-01-15T10:30:00Z"
    }
  },
  "templates": {
    "baddie": {
      "personalityPrompt": "You are confident, sassy baddie...",
      "name": "baddie",
      "title": "Confident Baddie",
      ...
    },
    "friendly": {
      "personalityPrompt": "You are a warm, friendly person...",
      "name": "friendly",
      "title": "Friendly Companion",
      ...
    }
  }
}
```

**Benefit:** Update rules once, apply to all personalities automatically!

## Backend Implementation

### Schemas

**`app/schemas/personality.py`**

```python
class PersonalityBase(BaseModel):
    personality_prompt: str  # Changed from system_prompt
    # ... other fields
```

**`app/schemas/settings.py`**

```python
class UniversalRulesBase(BaseModel):
    rules: str
    version: str
    enabled: bool
```

### API Endpoints

**Universal Rules Management**

- `GET /api/v1/settings/universal-rules` - Get current universal rules
- `PUT /api/v1/settings/universal-rules` - Update universal rules

**Personality Management** (Updated)

- `GET /api/v1/personalities/` - List all (returns `personalityPrompt`)
- `POST /api/v1/personalities/` - Create (uses `personalityPrompt`)
- `PUT /api/v1/personalities/{id}` - Update (uses `personalityPrompt`)

### Session Service Logic

**`app/services/session_service.py`** - `_get_system_prompt()`

```python
async def _get_system_prompt(self, template_id: str) -> str:
    # 1. Load universal rules
    universal_rules = get_from_firebase("/settings/universalRules")

    # 2. Load personality-specific prompt
    personality_prompt = get_from_firebase(f"/templates/{template_id}")

    # 3. Combine them
    combined = f"{universal_rules}\n\n{personality_prompt}"

    return combined
```

## Frontend Implementation

### Components

**1. UniversalRules Component**

- Located at `chatify-frontend/src/components/UniversalRules.jsx`
- Features:
  - View current universal rules
  - Edit rules with live preview
  - Toggle enable/disable
  - Version management
  - Informational guide

**2. PersonalityManager Component (Updated)**

- Changed field: `systemPrompt` → `personalityPrompt`
- Updated labels: "System Prompt" → "Personality Description"
- Added helper text explaining universal rules apply automatically

### Tab Navigation

```
┌─────────┬──────────────────┬──────────────────┐
│ 💬 Chat │ 🎭 Personalities │ 📋 Universal Rules│
└─────────┴──────────────────┴──────────────────┘
```

## Usage Guide

### Managing Universal Rules

1. Click **"📋 Universal Rules"** tab
2. Click **"✏️ Edit Rules"**
3. Modify the rules text
4. (Optional) Update version number
5. (Optional) Toggle enable/disable
6. Click **"💾 Save Rules"**

**Example Universal Rules:**

```text
CRITICAL RULES:
- Keep initial response short only 'Hi' or 'Heyy'
- Keep responses VERY short (1-9 words max, like real texting)
- Use casual language and shortforms (wyd, hru, lol, tbh, fr, etc.)
- NEVER repeat the same response twice in a conversation
- Use emojis very rarely where required (😂, 😔, 🤔)
- Don't mention being an AI or assistant
- Respond naturally to what the person actually said
- Vary your responses - never use the same phrase twice
- Keep it human and natural like real texting
```

### Creating a Personality

1. Click **"🎭 Personalities"** tab
2. Click **"+ New Personality"**
3. Fill in:
   - **Name**: `tech-expert`
   - **Title**: `Tech Expert`
   - **Description**: `Expert in technology and programming`
   - **Personality Description**: `You are a knowledgeable tech expert who explains complex concepts clearly. Be precise and helpful.`
4. Click **"Create Personality"**

**Note:** The universal rules will automatically be prepended to this personality's prompt!

### How They Combine

**Universal Rules:**

```
CRITICAL RULES:
- Keep responses short
- Use casual language
- Be natural
```

**Personality Prompt (Baddie):**

```
You are a confident, sassy baddie. Be bold and unapologetic.
```

**Final Combined Prompt Sent to AI:**

```
CRITICAL RULES:
- Keep responses short
- Use casual language
- Be natural

You are a confident, sassy baddie. Be bold and unapologetic.
```

## Migration from Old System

The system is **backward compatible**! It automatically handles old format:

```python
# Old format (still works)
{
  "systemPrompt": "Full prompt..."
}

# New format (preferred)
{
  "personalityPrompt": "Just personality description..."
}
```

The API automatically checks for `personalityPrompt` first, then falls back to `systemPrompt` if not found.

## Benefits

### 1. **Centralized Control**

- Update one place, affect all personalities
- Consistent behavior across all AI personalities
- Easy rule versioning

### 2. **Reduced Redundancy**

- Don't repeat the same rules in every personality
- Smaller personality definitions
- Cleaner codebase

### 3. **Easier Maintenance**

- Need to change response length limit? Update once!
- Want to add a new rule? Add it to universal rules!
- No need to hunt through dozens of personalities

### 4. **Better Organization**

- Clear separation of concerns
- Rules are rules, personalities are personalities
- Easier for new developers to understand

### 5. **Flexible Control**

- Toggle universal rules on/off globally
- Override by disabling and using only personality prompts
- Test different rule sets without changing personalities

## Use Cases

### Scenario 1: Changing Response Style

**Before:** Edit 13 personalities, changing each `systemPrompt`
**After:** Edit universal rules once

### Scenario 2: Adding a New Rule

**Before:**

1. Edit all 13 personalities
2. Risk missing some
3. Risk inconsistent wording

**After:**

1. Add to universal rules
2. Automatically applies to all
3. Consistent everywhere

### Scenario 3: A/B Testing

**Before:** Create duplicate personalities with different rules
**After:**

1. Create two universal rule versions
2. Switch between them
3. Keep personalities unchanged

## Troubleshooting

### "Personality not behaving as expected"

1. Check if universal rules are enabled
2. Check the combined prompt (backend logs show this)
3. Verify personality prompt is saved correctly

### "Universal rules not applying"

1. Check `enabled` status in universal rules
2. Verify Firebase connection
3. Check backend logs for "📋 Loaded universal rules"

### "Old personalities not working"

Don't worry! The system handles old `systemPrompt` format automatically.

## Best Practices

1. **Keep Universal Rules Generic**

   - Don't put personality-specific instructions in universal rules
   - Focus on technical constraints (length, format, etc.)

2. **Keep Personality Prompts Specific**

   - Focus on personality traits and tone
   - Don't repeat universal rules
   - Describe the unique character

3. **Version Your Rules**

   - Update version number when making significant changes
   - Track what changed in each version
   - Consider keeping a changelog

4. **Test After Rule Changes**

   - Changes affect ALL personalities
   - Test with different personalities to ensure consistency
   - Monitor for unintended side effects

5. **Use Enable/Disable Strategically**
   - Disable to test personality prompts in isolation
   - Re-enable once satisfied with changes
   - Consider temporary disable during development

## API Examples

### Get Universal Rules

```javascript
const response = await fetch(
  "http://localhost:8000/api/v1/settings/universal-rules"
);
const rules = await response.json();
console.log(rules.rules); // The actual rules text
console.log(rules.version); // e.g., "1.0"
console.log(rules.enabled); // true/false
```

### Update Universal Rules

```javascript
await fetch("http://localhost:8000/api/v1/settings/universal-rules", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    rules: "New rules text...",
    version: "2.0",
    enabled: true,
  }),
});
```

### Create Personality with New System

```javascript
await fetch("http://localhost:8000/api/v1/personalities/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "my-personality",
    title: "My Personality",
    description: "A custom personality",
    personalityPrompt: "You are...", // Note: personalityPrompt, not systemPrompt
    category: "general",
  }),
});
```

## Future Enhancements

Potential improvements:

- **Multiple Rule Sets**: Allow different rule sets for different categories
- **Rule Inheritance**: Parent-child rule relationships
- **Rule Templates**: Pre-made rule sets for different use cases
- **Rule Validation**: Check for conflicts or contradictions
- **A/B Testing UI**: Easy switching between rule versions
- **Rule History**: Track changes over time
- **Conditional Rules**: Apply different rules based on context

## Summary

The Split Prompt System provides a clean, maintainable architecture for managing AI personality behavior:

- **Universal Rules**: One source of truth for global behavior
- **Personality Prompts**: Unique character descriptions
- **Automatic Combination**: Seamlessly merged at runtime
- **Backward Compatible**: Works with old data format
- **Easy to Use**: Simple UI for both components

This system makes managing multiple AI personalities at scale much more practical and efficient! 🚀
