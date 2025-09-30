# AI Personality Management System

## Overview

This system allows you to create, read, update, and delete (CRUD) AI personalities through the web UI. Each personality has a unique system prompt that defines how the AI behaves in conversations.

## Features

### Backend API (FastAPI)

The backend provides RESTful API endpoints for managing personalities:

- **GET** `/api/v1/personalities/` - List all personalities
- **GET** `/api/v1/personalities/{id}` - Get a specific personality
- **POST** `/api/v1/personalities/` - Create a new personality
- **PUT** `/api/v1/personalities/{id}` - Update a personality
- **DELETE** `/api/v1/personalities/{id}` - Delete a personality

### Frontend UI (React)

The frontend provides an intuitive interface with:

- **Tab Navigation**: Switch between Chat and Personality Management
- **Personality List**: View all existing personalities with their details
- **Create Form**: Add new personalities with custom prompts
- **Edit Form**: Modify existing personalities
- **Delete Function**: Remove personalities (except defaults)

## Personality Schema

Each personality includes:

| Field            | Type    | Description                                                               |
| ---------------- | ------- | ------------------------------------------------------------------------- |
| `name`           | string  | Unique identifier (e.g., "friendly-assistant")                            |
| `title`          | string  | Display name (e.g., "Friendly Assistant")                                 |
| `description`    | string  | Brief description of the personality                                      |
| `category`       | string  | Category: general, dating, support, creative, professional, entertainment |
| `systemPrompt`   | string  | **Core prompt that defines AI behavior**                                  |
| `welcomeMessage` | string  | Initial greeting message                                                  |
| `model`          | string  | AI model: gpt-4o-mini, gpt-4o, gpt-3.5-turbo                              |
| `temperature`    | float   | Creativity level (0.0-2.0)                                                |
| `maxTokens`      | int     | Response length limit (10-4000)                                           |
| `tags`           | array   | Searchable tags                                                           |
| `isPublic`       | boolean | Visibility to all users                                                   |
| `isDefault`      | boolean | Protected from deletion                                                   |

## How to Use

### Creating a New Personality

1. Click the **"Manage Personalities"** tab
2. Click **"+ New Personality"**
3. Fill in the form:
   - **Name**: Use lowercase with dashes (e.g., `tech-expert`)
   - **Title**: Display name (e.g., "Tech Expert")
   - **Description**: Brief overview
   - **System Prompt**: Define how the AI should behave (this is the most important field!)
   - Configure model settings, temperature, etc.
4. Click **"Create Personality"**

### Editing a Personality

1. Find the personality card in the list
2. Click **"Edit"**
3. Modify any fields (except name/ID)
4. Click **"Update Personality"**

### Deleting a Personality

1. Find the personality card
2. Click **"Delete"**
3. Confirm the deletion
   - **Note**: Default personalities cannot be deleted

### Using a Personality in Chat

1. Switch to the **"Chat"** tab
2. When creating a new session, select your personality from the dropdown
3. Start chatting!

## System Prompt Examples

### Friendly Assistant

```
You are a helpful and friendly AI assistant. Keep responses concise and helpful.
Be warm, approachable, and supportive in all interactions.
```

### Technical Expert

```
You are a technical expert with deep knowledge of programming and technology.
Provide accurate, detailed explanations with code examples when relevant.
Use technical terminology appropriately.
```

### Creative Writer

```
You are a creative writing assistant with a flair for storytelling.
Help users brainstorm ideas, develop characters, and craft engaging narratives.
Be imaginative and encourage creativity.
```

### Dating Coach

```
You are a dating and relationship coach on a dating app.
Keep responses short (1-9 words max, like real texting).
Use casual language and be flirty but respectful.
```

## Data Storage

- **Backend**: Python/FastAPI with Pydantic validation
- **Database**: Firebase Realtime Database at `/templates/{personality_id}`
- **Format**: JSON with camelCase field names

## File Structure

### Backend

```
app/
├── schemas/
│   └── personality.py          # Pydantic models for validation
├── api/v1/endpoints/
│   └── personality.py          # CRUD endpoints
└── api/v1/
    └── api.py                  # Router registration
```

### Frontend

```
chatify-frontend/src/
├── components/
│   ├── PersonalityManager.jsx  # Main component
│   └── PersonalityManager.css  # Styles
├── services/
│   └── api.js                  # API integration
└── App.jsx                     # Tab integration
```

## Security Features

- **Validation**: All inputs validated with Pydantic schemas
- **Protected Defaults**: Default personalities cannot be deleted
- **Unique Names**: Prevents duplicate personality names
- **Error Handling**: Comprehensive error messages

## Tips for Writing System Prompts

1. **Be Specific**: Clearly define the AI's role and behavior
2. **Set Boundaries**: Specify what the AI should and shouldn't do
3. **Include Examples**: Show the type of responses you want
4. **Define Tone**: Specify if it should be formal, casual, funny, etc.
5. **Set Constraints**: Mention response length, style, formatting, etc.

## Troubleshooting

### "Failed to create personality"

- Check that the name is unique
- Ensure all required fields are filled
- Verify Firebase is properly configured

### "Personality not found"

- Check that the personality ID is correct
- Ensure Firebase connection is active

### "Cannot delete personality"

- This personality is marked as default
- Edit the personality to remove default status first

## Future Enhancements

Potential improvements:

- Import/Export personalities as JSON
- Personality templates marketplace
- A/B testing different prompts
- Usage analytics per personality
- Version control for prompts
- Personality cloning feature
- Bulk operations

## API Documentation

Full API documentation available at:

- Local: `http://localhost:8000/docs`
- Interactive Swagger UI with try-it-out functionality

## Support

For issues or questions:

1. Check Firebase connection
2. Verify API is running (`/health` endpoint)
3. Check browser console for errors
4. Review FastAPI logs for backend errors
