# Auto-Apply Feature Documentation

## Overview
The Auto-Apply feature uses an AI agent to automatically apply for jobs based on user preferences and profile data. It includes intelligent validation, missing information detection, and an interactive chatbot to gather required information.

## Features

### 1. **AI-Powered Auto-Apply Agent**
- Validates user profile completeness before applying
- Automatically fills job application forms with user data
- Tracks application status and provides feedback
- Simulates real job applications (ready for production integration)

### 2. **Interactive Chatbot**
- **Location**: Bottom-right corner with a black star icon
- **Purpose**: Gather missing profile information
- **Features**:
  - Real-time conversation
  - Smart field detection
  - Profile completion tracking
  - Beautiful UI with bubble design

### 3. **Auto-Apply Button**
- Appears on every job card
- One-click application process
- Visual status feedback (applying, success, error)
- Automatic validation before applying

## How It Works

### User Flow

1. **User clicks "Auto Apply" button** on a job card
2. **System validates profile**:
   - Checks for required fields: name, email, location, skills, experience, education
   - If complete → Proceeds with application
   - If incomplete → Shows missing fields and opens chatbot

3. **Chatbot interaction** (if needed):
   - Chatbot asks for missing information
   - User provides information via chat
   - System updates profile automatically
   - Once complete, user can retry auto-apply

4. **Application submission**:
   - System prepares application data
   - Submits to job platform (simulated)
   - Shows success/error status
   - Tracks application history

### Required Profile Fields

**Basic Information:**
- Full Name
- Email
- Location

**Professional Information:**
- Experience Level
- Skills (at least one)
- Education (at least one entry)
- Work Experience (at least one entry)
- Job Preferences (at least one)

**Optional but Recommended:**
- LinkedIn URL
- GitHub URL
- Portfolio URL
- Projects

## API Endpoints

### Backend Endpoints

#### 1. Validate Auto-Apply
```
GET /auto-apply/validate
Authorization: Bearer <token>

Response:
{
  "can_auto_apply": boolean,
  "missing_fields": string[],
  "prompts": [
    {
      "field": "field_name",
      "question": "User-friendly question",
      "type": "text|list|structured"
    }
  ]
}
```

#### 2. Execute Auto-Apply
```
POST /auto-apply/execute
Authorization: Bearer <token>
Body: {
  "job_ids": ["job1", "job2", ...]
}

Response:
{
  "success": boolean,
  "summary": {
    "total_applications": number,
    "successful": number,
    "failed": number
  },
  "results": [...]
}
```

#### 3. Chatbot Message
```
POST /chatbot/message
Authorization: Bearer <token>
Body: {
  "message": "user message",
  "field": "field_name" (optional)
}

Response:
{
  "success": boolean,
  "message": "bot response",
  "next_field": {...} (if more info needed),
  "completed": boolean
}
```

## Frontend Components

### 1. ChatbotButton Component
**File**: `frontend/src/components/ChatbotButton.tsx`

Features:
- Floating button with star icon
- Bubble effect background
- Glow animation on hover
- Notification badge

### 2. Chatbot Component
**File**: `frontend/src/components/Chatbot.tsx`

Features:
- Full chat interface
- Message history
- Typing indicators
- Profile completion checker
- Auto-scrolling messages

### 3. AutoApplyButton Component
**File**: `frontend/src/components/AutoApplyButton.tsx`

Features:
- One-click auto-apply
- Status indicators (loading, success, error)
- Missing info detection
- Visual feedback

## Customization

### Styling
All components use Tailwind CSS and support dark mode. Colors and animations can be customized in the component files.

### Chatbot Icon
The chatbot uses a **Sparkles** icon (star) with a black background and yellow color. To change:
```tsx
// In ChatbotButton.tsx
<Sparkles className="w-7 h-7 text-yellow-400" fill="currentColor" />
```

### Required Fields
To modify required fields for auto-apply, edit:
```python
# In backend/auto_apply_agent.py
REQUIRED_FIELDS = {
    "basic_info": ["full_name", "email", "location"],
    "professional": ["experience_level", "skills"],
    ...
}
```

## Production Integration

### Job Platform Integration
The current implementation simulates job applications. For production:

1. **Integrate with job platforms**:
   - LinkedIn API
   - Indeed API
   - Glassdoor API
   - Custom scrapers

2. **Update `auto_apply_agent.py`**:
   ```python
   def simulate_application(self, job: Dict) -> Dict:
       # Replace with actual API calls
       # Example: linkedin_api.apply(job, self.user_data)
   ```

3. **Add error handling**:
   - Rate limiting
   - CAPTCHA solving
   - Session management
   - Retry logic

### Database Storage
Consider storing:
- Application history
- Success/failure rates
- User preferences
- Chat conversations

## Testing

### Test Auto-Apply Flow
1. Login to the application
2. Ensure profile is incomplete
3. Click "Auto Apply" on a job
4. Verify chatbot opens with missing fields
5. Provide information via chat
6. Verify profile updates
7. Retry auto-apply
8. Verify success message

### Test Chatbot
1. Click the star icon in bottom-right
2. Type "Check my profile completeness"
3. Verify missing fields are shown
4. Provide information
5. Verify profile completion

## Troubleshooting

### Auto-Apply Not Working
- Check if user is logged in
- Verify backend is running on port 8000
- Check browser console for errors
- Verify profile has all required fields

### Chatbot Not Responding
- Check network tab for API errors
- Verify token is valid
- Check backend logs
- Ensure CORS is configured

### Missing Fields Not Detected
- Check `auto_apply_agent.py` validation logic
- Verify user profile in database
- Check API response format

## Future Enhancements

1. **Bulk Auto-Apply**: Apply to multiple jobs at once
2. **Smart Matching**: AI suggests best-fit jobs
3. **Cover Letter Generation**: Auto-generate personalized cover letters
4. **Application Tracking**: Dashboard for all applications
5. **Interview Scheduling**: Integrate calendar for interviews
6. **Success Analytics**: Track application success rates
7. **A/B Testing**: Test different application strategies

## Security Considerations

1. **Rate Limiting**: Prevent abuse of auto-apply
2. **Data Privacy**: Encrypt sensitive user data
3. **Token Management**: Secure JWT tokens
4. **Input Validation**: Sanitize all user inputs
5. **CAPTCHA**: Add CAPTCHA for bot detection

## Support

For issues or questions:
- Check backend logs: `backend/backend.log`
- Check browser console
- Review API responses
- Test with minimal profile data

---

**Built with ❤️ using FastAPI, Next.js, and AI**
