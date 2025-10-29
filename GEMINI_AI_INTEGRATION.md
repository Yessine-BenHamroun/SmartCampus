# Gemini AI Integration for Quiz & Assignment Generation

## Overview
Google Gemini AI has been integrated into SmartCampus to automatically generate quiz questions and assignment content based on lesson and course materials.

---

## API Configuration

### API Key
```
AIzaSyACDAQYNC0tBWRcmED1uyHEYq2gVTwj6JI
```

### Model Used
- **Gemini Pro** - Google's latest generative AI model
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`

---

## Features Implemented

### 1. AI-Powered Quiz Generation

**Endpoint:** `POST /api/courses/instructor/lesson/<lesson_id>/quiz/generate/`

**Request Body:**
```json
{
  "num_questions": 5,
  "difficulty": "medium"
}
```

**What it does:**
- Analyzes lesson content (title, description, content)
- Generates multiple-choice questions using Gemini AI
- Returns questions in structured JSON format
- Instructor can review and edit before creating quiz

**Response:**
```json
{
  "lesson_id": "...",
  "generated_questions": [
    {
      "question_text": "What is the main concept...",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "points": 1
    }
  ],
  "message": "Review and edit questions before creating the quiz"
}
```

---

### 2. AI-Powered Assignment Generation

**Endpoint:** `POST /api/courses/instructor/course/<course_id>/assignment/generate/`

**Request Body:**
```json
{
  "assignment_type": "written",
  "num_questions": 5
}
```

**Assignment Types:**
- **written** - Short answer, MCQ, True/False questions
- **coding** - Python coding challenges with test cases
- **mixed** - Combination of written and coding

**What it does:**
- Analyzes course content and category
- Generates relevant assignment questions/problems
- Provides starter code for coding assignments
- Includes test cases and hints

---

## How It Works

### Quiz Question Generation Process

1. **Input:** Lesson content (title, description, content)
2. **AI Prompt:** Structured prompt asking for specific JSON format
3. **Gemini Processing:** AI analyzes content and generates questions
4. **Response Parsing:** Extracts JSON from response (handles markdown wrapping)
5. **Validation:** Ensures correct format and data types
6. **Fallback:** Uses sample questions if AI fails

### Coding Assignment Generation Process

1. **Input:** Course information (title, description, category, difficulty)
2. **AI Prompt:** Requests Python coding problem with test cases
3. **Gemini Processing:** Creates realistic coding challenge
4. **Response Parsing:** Extracts structured problem data
5. **Output:** Problem description, starter code, test cases, hints

---

## AI Prompt Engineering

### Quiz Generation Prompt Structure
```
Generate {num_questions} multiple-choice quiz questions based on the following lesson content.
Difficulty level: {difficulty}

Lesson Title: ...
Lesson Description: ...
Lesson Content: ...

Generate questions in the following JSON format:
[...]

Requirements:
- Each question should test understanding of the lesson content
- Provide 4 options for each question
- correct_answer should be the index (0-3) of the correct option
- For {difficulty} difficulty, make questions appropriately challenging
- Return ONLY valid JSON array, no additional text
```

### Key Prompt Features
- **Structured format specification** - Ensures consistent output
- **Clear requirements** - Guides AI to generate quality content
- **JSON-only response** - Simplifies parsing
- **Context-aware** - Uses actual lesson/course content

---

## Error Handling

### Robust Parsing
```python
# Handles multiple response formats
if '```json' in response:
    json_str = response.split('```json')[1].split('```')[0].strip()
elif '```' in response:
    json_str = response.split('```')[1].split('```')[0].strip()
else:
    json_str = response.strip()
```

### Validation
- Checks for required fields in each question
- Validates data types (correct_answer must be 0-3)
- Ensures maximum 4 options per question
- Limits response to requested number of questions

### Fallback Mechanism
- If Gemini API fails → Uses sample questions
- If JSON parsing fails → Returns fallback content
- Logs errors for debugging
- Never breaks the application

---

## Usage Examples

### For Instructors

#### 1. Generate Quiz Questions
```javascript
// From quiz creation page
const response = await fetch(`/api/courses/instructor/lesson/${lessonId}/quiz/generate/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    num_questions: 5,
    difficulty: 'medium'
  })
});

const data = await response.json();
// Review and edit questions
// Then create quiz with edited questions
```

#### 2. Generate Coding Assignment
```javascript
const response = await fetch(`/api/courses/instructor/course/${courseId}/assignment/generate/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    assignment_type: 'coding',
    num_questions: 1
  })
});

const data = await response.json();
// Review coding problem
// Edit if needed
// Create assignment
```

---

## Benefits

### For Instructors
✅ **Save Time** - Generate questions in seconds instead of hours  
✅ **Quality Content** - AI creates relevant, well-structured questions  
✅ **Customizable** - Review and edit before publishing  
✅ **Variety** - Different question types and difficulty levels  
✅ **Context-Aware** - Questions based on actual lesson content  

### For Students
✅ **Better Assessments** - More diverse and comprehensive questions  
✅ **Relevant Content** - Questions directly related to what they learned  
✅ **Fair Testing** - Consistent quality across all quizzes  

---

## Technical Implementation

### File Structure
```
backend/courses/
├── ai_helpers.py          # Gemini AI integration
├── views_ai.py            # AI generation endpoints
└── urls.py                # API routes

Functions:
- call_gemini_api(prompt)                    # Core API call
- generate_quiz_questions(...)               # Quiz generation
- generate_assignment_questions(...)         # Assignment generation
```

### Dependencies
```
requests==2.31.0  # For API calls
```

---

## API Rate Limits & Best Practices

### Gemini API Limits
- Free tier: 60 requests per minute
- Response time: Usually 2-5 seconds
- Max prompt length: ~30,000 characters

### Best Practices
1. **Cache Results** - Store generated questions to avoid repeated calls
2. **Batch Requests** - Generate multiple questions in one call
3. **Error Handling** - Always have fallback content
4. **Content Limits** - Truncate lesson content to 1000 characters
5. **Review Before Publishing** - Instructor should always review AI-generated content

---

## Security Considerations

### API Key Security
⚠️ **Current Implementation:** API key is hardcoded in `ai_helpers.py`

**Recommended Improvements:**
1. Move API key to environment variables (`.env` file)
2. Use Django settings for configuration
3. Implement key rotation
4. Monitor API usage

### Content Validation
- All AI-generated content is validated before use
- Instructors must review before publishing
- Fallback to safe default content if AI fails

---

## Future Enhancements

### Potential Improvements
1. **Multi-language Support** - Generate questions in different languages
2. **Image Generation** - Include diagrams and visual aids
3. **Adaptive Difficulty** - Adjust based on student performance
4. **Question Bank** - Build library of AI-generated questions
5. **Plagiarism Detection** - Check for duplicate questions
6. **Student Feedback Integration** - Improve questions based on feedback

### Advanced Features
- **Personalized Quizzes** - Tailored to individual student needs
- **Automatic Grading** - AI-assisted grading for written answers
- **Performance Analytics** - Track which AI-generated questions work best
- **Content Suggestions** - Recommend improvements to lesson content

---

## Testing

### Manual Testing Steps
1. Create a lesson with content
2. Call quiz generation API
3. Verify questions are relevant to lesson
4. Check JSON format is correct
5. Test with different difficulty levels
6. Verify fallback works when API fails

### Test Cases
```python
# Test quiz generation
response = generate_quiz_questions(
    lesson_content={'title': 'Python Basics', 'description': 'Learn Python'},
    num_questions=5,
    difficulty='medium'
)
assert len(response) == 5
assert all('question_text' in q for q in response)

# Test coding assignment
response = generate_assignment_questions(
    course_content={'title': 'Web Development'},
    assignment_type='coding',
    num_questions=1
)
assert 'problem_title' in response
assert 'starter_code' in response
```

---

## Troubleshooting

### Common Issues

**Issue:** API returns 400 Bad Request
- **Cause:** Invalid API key or malformed request
- **Solution:** Check API key, verify request format

**Issue:** JSON parsing fails
- **Cause:** Gemini returns text instead of JSON
- **Solution:** Improved prompt engineering, better parsing logic

**Issue:** Questions not relevant to content
- **Cause:** Insufficient lesson content provided
- **Solution:** Ensure lessons have detailed descriptions

**Issue:** API timeout
- **Cause:** Network issues or API overload
- **Solution:** Implement retry logic, use fallback

---

## Monitoring & Logs

### What to Monitor
- API call success rate
- Response times
- Fallback usage frequency
- Question quality (instructor feedback)

### Logging
```python
print(f"Gemini API Error: {response.status_code} - {response.text}")
print(f"Failed to parse Gemini response as JSON: {str(e)}")
print("Using fallback sample questions")
```

---

## Cost Estimation

### Gemini API Pricing (as of 2024)
- **Free Tier:** 60 requests/minute
- **Pay-as-you-go:** $0.00025 per 1K characters

### Estimated Usage
- Average quiz generation: ~500 characters prompt
- Average assignment: ~800 characters prompt
- 100 generations/day = ~$0.02/day
- Monthly cost: ~$0.60

**Conclusion:** Very cost-effective for educational use!

---

## Conclusion

The Gemini AI integration provides a powerful tool for instructors to quickly create high-quality assessments. With proper error handling, fallback mechanisms, and instructor review, it enhances the course creation experience while maintaining quality standards.

**Status:** ✅ Fully Implemented and Ready to Use
