# AI Quiz Generation - How It Works

## ✅ YES, the AI Uses Lesson Content!

The Gemini AI **absolutely** uses the lesson content when generating quizzes. Here's exactly how:

---

## What Gets Sent to Gemini AI

### 1. Lesson Information Extracted
```python
lesson_content = {
    'title': lesson.title,                    # e.g., "Introduction to Python"
    'description': lesson.description,         # e.g., "Learn Python basics"
    'content': lesson.content,                 # The actual lesson text (up to 3000 chars)
    'content_type': lesson.content_type,       # e.g., "text", "video", "quiz"
    'duration': lesson.duration_minutes        # e.g., 30
}
```

### 2. Content Extraction Logic
The system intelligently extracts content based on lesson type:

**For Text Lessons:**
```python
if 'text_content' in lesson.content:
    content_text = lesson.content.get('text_content', '')
```

**For Video Lessons:**
```python
elif 'video_url' in lesson.content:
    content_text = f"Video lesson: {lesson.content.get('video_url', '')}"
```

**For Other Types:**
```python
else:
    content_text = str(lesson.content)
```

---

## The AI Prompt Sent to Gemini

Here's the **exact prompt** that gets sent:

```
You are an expert educator creating quiz questions. Generate 5 multiple-choice quiz questions based on the following lesson.

LESSON INFORMATION:
Title: Introduction to Python
Description: Learn the fundamentals of Python programming
Content Type: text
Difficulty Level: medium

LESSON CONTENT:
[First 3000 characters of your lesson content goes here]
Python is a high-level programming language...
Variables are used to store data...
Functions help organize code...
[etc.]

IMPORTANT INSTRUCTIONS:
- Questions MUST be directly based on the lesson content above
- Test understanding of key concepts from this specific lesson
- Each question should assess different aspects of the lesson
- For medium difficulty: medium questions test understanding and application
- Ensure questions are clear and unambiguous
- Make sure the correct answer is definitively correct based on the lesson content
- Make distractors (wrong answers) plausible but clearly incorrect

Generate questions in the following JSON format:
[
  {
    "question_text": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "points": 1
  }
]

Requirements:
- Each question should test understanding of the lesson content
- Provide 4 options for each question
- correct_answer should be the index (0-3) of the correct option
- For medium difficulty, make questions appropriately challenging
- Return ONLY valid JSON array, no additional text

Generate exactly 5 questions.
```

---

## Recent Improvements Made

### ✅ Enhanced Content Extraction
- Now handles different lesson content formats (text, video, etc.)
- Extracts `text_content` from dictionary-based content
- Handles video lessons appropriately

### ✅ Increased Content Limit
- **Before:** Only 1000 characters of lesson content
- **After:** Now sends 3000 characters of lesson content
- More context = Better, more relevant questions

### ✅ Improved AI Instructions
- Added role: "You are an expert educator"
- Explicit instruction: "Questions MUST be directly based on the lesson content above"
- Clear difficulty guidelines
- Better formatting with sections

### ✅ Better Validation
- Ensures content is properly extracted
- Handles missing fields gracefully
- Validates question format

---

## Example Flow

### Step 1: Instructor Creates Lesson
```
Title: "Python Variables"
Description: "Understanding variables in Python"
Content: "Variables in Python are containers for storing data values. 
          Unlike other programming languages, Python has no command for 
          declaring a variable. A variable is created the moment you 
          first assign a value to it. Example: x = 5, name = 'John'..."
```

### Step 2: Instructor Clicks "Generate Quiz with AI"
```javascript
POST /api/courses/instructor/lesson/123/quiz/generate/
{
  "num_questions": 5,
  "difficulty": "medium"
}
```

### Step 3: System Extracts Lesson Content
```python
lesson_content = {
    'title': 'Python Variables',
    'description': 'Understanding variables in Python',
    'content': 'Variables in Python are containers for storing data values...',
    'content_type': 'text',
    'duration': 15
}
```

### Step 4: Gemini AI Analyzes Content
The AI reads the lesson content and generates relevant questions like:

```json
[
  {
    "question_text": "What is a variable in Python?",
    "options": [
      "A container for storing data values",
      "A type of loop",
      "A function declaration",
      "A class definition"
    ],
    "correct_answer": 0,
    "points": 1
  },
  {
    "question_text": "How do you create a variable in Python?",
    "options": [
      "Using the var keyword",
      "Using the let keyword",
      "By assigning a value to it",
      "Using the define keyword"
    ],
    "correct_answer": 2,
    "points": 1
  }
]
```

### Step 5: Instructor Reviews & Edits
- Questions are returned to the instructor
- Can edit any question before creating the quiz
- Can regenerate if not satisfied

---

## How to Ensure Best Results

### 1. Write Detailed Lesson Content
✅ **Good:**
```
Variables in Python are containers for storing data values. Python has no 
command for declaring a variable. A variable is created when you assign a 
value to it. For example: x = 5 creates a variable x with value 5.
```

❌ **Bad:**
```
Learn about variables.
```

### 2. Include Key Concepts
Make sure your lesson content includes:
- Definitions
- Examples
- Explanations
- Important points
- Common mistakes

### 3. Use Clear Structure
```
Title: Clear, descriptive title
Description: Brief overview of what students will learn
Content: 
  - Introduction
  - Main concepts
  - Examples
  - Summary
```

---

## Troubleshooting

### Issue: Questions Not Relevant to Lesson
**Cause:** Lesson content is too short or vague  
**Solution:** Add more detailed content to the lesson (aim for 500+ characters)

### Issue: Questions Too Easy/Hard
**Cause:** Wrong difficulty level selected  
**Solution:** Adjust difficulty parameter (easy/medium/hard)

### Issue: AI Returns Generic Questions
**Cause:** Lesson content is missing or empty  
**Solution:** Ensure lesson has actual content before generating quiz

---

## Content Limits

| Parameter | Limit | Reason |
|-----------|-------|--------|
| Lesson Content | 3000 characters | Balance between context and API limits |
| Number of Questions | 1-10 | Practical quiz size |
| Prompt Length | ~4000 characters | Gemini API limit |

---

## API Call Example

```python
# What actually gets called
response = call_gemini_api(prompt="""
You are an expert educator creating quiz questions. Generate 5 multiple-choice quiz questions based on the following lesson.

LESSON INFORMATION:
Title: Introduction to Python
Description: Learn Python basics
Content Type: text
Difficulty Level: medium

LESSON CONTENT:
[Your actual lesson content here - up to 3000 characters]

IMPORTANT INSTRUCTIONS:
- Questions MUST be directly based on the lesson content above
- Test understanding of key concepts from this specific lesson
...
""")
```

---

## Verification Checklist

To verify the AI is using your lesson content:

1. ✅ Create a lesson with specific, unique content
2. ✅ Generate quiz using AI
3. ✅ Check if questions reference concepts from your lesson
4. ✅ Verify questions aren't generic
5. ✅ Confirm correct answers match your lesson content

---

## Summary

**YES!** The AI **definitely** uses your lesson content:

✅ Extracts lesson title, description, and content  
✅ Sends up to 3000 characters of lesson content to Gemini  
✅ Explicitly instructs AI to base questions on the content  
✅ Validates that questions are relevant  
✅ Allows instructor review before publishing  

The more detailed and comprehensive your lesson content, the better and more relevant the AI-generated questions will be!
