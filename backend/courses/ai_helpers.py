"""
AI helper functions for quiz and assignment generation
Using Google Gemini AI API
"""
import random
import json
import os


# Gemini AI Configuration
GEMINI_API_KEY = "AIzaSyACDAQYNC0tBWRcmED1uyHEYq2gVTwj6JI"


def call_gemini_api(prompt):
    """
    Call Google Gemini AI API
    
    Args:
        prompt: The prompt to send to Gemini
        
    Returns:
        Generated text response
    """
    try:
        import requests
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                return text
        
        print(f"Gemini API Error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return None


def generate_quiz_questions(lesson_content, num_questions=5, difficulty='medium'):
    """
    Generate quiz questions based on lesson content using Gemini AI
    
    Args:
        lesson_content: Dictionary containing lesson information
        num_questions: Number of questions to generate
        difficulty: Difficulty level (easy, medium, hard)
    
    Returns:
        List of question dictionaries
    """
    # Prepare prompt for Gemini
    # Extract and format lesson content
    title = lesson_content.get('title', 'N/A')
    description = lesson_content.get('description', 'N/A')
    content = str(lesson_content.get('content', 'N/A'))[:3000]  # Increased from 1000 to 3000 characters
    content_type = lesson_content.get('content_type', 'text')
    
    prompt = f"""You are an expert educator creating quiz questions. Generate {num_questions} multiple-choice quiz questions based on the following lesson.

LESSON INFORMATION:
Title: {title}
Description: {description}
Content Type: {content_type}
Difficulty Level: {difficulty}

LESSON CONTENT:
{content}

IMPORTANT INSTRUCTIONS:
- Questions MUST be directly based on the lesson content above
- Test understanding of key concepts from this specific lesson
- Each question should assess different aspects of the lesson
- For {difficulty} difficulty: {"easy questions test basic recall" if difficulty == "easy" else "medium questions test understanding and application" if difficulty == "medium" else "hard questions test analysis and synthesis"}
- Ensure questions are clear and unambiguous
- Make sure the correct answer is definitively correct based on the lesson content
- Make distractors (wrong answers) plausible but clearly incorrect

Generate questions in the following JSON format:
[
  {{
    "question_text": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "points": 1
  }}
]

Requirements:
- Each question should test understanding of the lesson content
- Provide 4 options for each question
- correct_answer should be the index (0-3) of the correct option
- For {difficulty} difficulty, make questions appropriately challenging
- Return ONLY valid JSON array, no additional text

Generate exactly {num_questions} questions."""

    # Call Gemini API
    response = call_gemini_api(prompt)
    
    if response:
        try:
            # Try to extract JSON from response
            # Sometimes Gemini wraps JSON in markdown code blocks
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()
            
            questions = json.loads(json_str)
            
            # Validate and ensure correct format
            validated_questions = []
            for q in questions:
                if all(key in q for key in ['question_text', 'options', 'correct_answer']):
                    validated_questions.append({
                        'question_text': q['question_text'],
                        'options': q['options'][:4],  # Ensure max 4 options
                        'correct_answer': int(q['correct_answer']) % 4,  # Ensure 0-3
                        'points': q.get('points', 1)
                    })
            
            if validated_questions:
                return validated_questions[:num_questions]
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            print(f"Error processing Gemini response: {str(e)}")
    
    # Fallback to sample questions if AI fails
    print("Using fallback sample questions")
    sample_questions = [
        {
            'question_text': f'What is the main concept covered in this lesson about {lesson_content.get("title", "the topic")}?',
            'options': [
                'Option A - Basic understanding',
                'Option B - Advanced application',
                'Option C - Theoretical framework',
                'Option D - Practical implementation'
            ],
            'correct_answer': 0,
            'points': 1
        },
        {
            'question_text': 'Which of the following best describes the key principle discussed?',
            'options': [
                'Principle A',
                'Principle B',
                'Principle C',
                'Principle D'
            ],
            'correct_answer': 1,
            'points': 1
        },
        {
            'question_text': 'How would you apply this concept in a real-world scenario?',
            'options': [
                'Approach A - Direct application',
                'Approach B - Modified approach',
                'Approach C - Indirect application',
                'Approach D - Combined strategy'
            ],
            'correct_answer': 2,
            'points': 2
        },
        {
            'question_text': 'What is the most important takeaway from this lesson?',
            'options': [
                'Understanding the basics',
                'Mastering the technique',
                'Applying the knowledge',
                'All of the above'
            ],
            'correct_answer': 3,
            'points': 1
        },
        {
            'question_text': 'Which statement is correct regarding the topic?',
            'options': [
                'Statement A is always true',
                'Statement B depends on context',
                'Statement C is incorrect',
                'Statement D needs verification'
            ],
            'correct_answer': 1,
            'points': 1
        }
    ]
    
    # Adjust difficulty
    if difficulty == 'easy':
        points_multiplier = 1
    elif difficulty == 'hard':
        points_multiplier = 2
    else:
        points_multiplier = 1
    
    # Select random questions up to num_questions
    selected = random.sample(sample_questions, min(num_questions, len(sample_questions)))
    
    for q in selected:
        q['points'] *= points_multiplier
    
    return selected


def generate_assignment_questions(course_content, assignment_type='written', num_questions=5):
    """
    Generate assignment questions based on course content using Gemini AI
    
    Args:
        course_content: Dictionary containing course information
        assignment_type: Type of assignment (written, coding, mixed)
        num_questions: Number of questions to generate
    
    Returns:
        Dictionary with questions or coding problem
    """
    
    if assignment_type == 'coding':
        # Generate coding problem using Gemini
        prompt = f"""Generate a Python coding assignment based on the following course content:

Course Title: {course_content.get('title', 'N/A')}
Course Description: {course_content.get('description', 'N/A')}
Category: {course_content.get('category', 'N/A')}
Difficulty: {course_content.get('difficulty_level', 'medium')}

Generate a coding problem in the following JSON format:
{{
  "problem_title": "Title of the coding challenge",
  "description": "Detailed description of what the student needs to implement",
  "starter_code": "# Python starter code with function signature",
  "test_cases": [
    {{"input": "example input", "expected_output": "expected result"}},
    {{"input": "example input 2", "expected_output": "expected result 2"}}
  ],
  "hints": ["Hint 1", "Hint 2"]
}}

Requirements:
- Create a realistic coding problem related to the course content
- Provide clear problem description
- Include starter code with function signature
- Provide at least 2 test cases
- Include helpful hints
- Return ONLY valid JSON, no additional text"""

        response = call_gemini_api(prompt)
        
        if response:
            try:
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0].strip()
                else:
                    json_str = response.strip()
                
                coding_problem = json.loads(json_str)
                return coding_problem
            except Exception as e:
                print(f"Error parsing Gemini coding response: {str(e)}")
        
        # Fallback
        return {
            'problem_title': f'Coding Challenge: {course_content.get("title", "Course Topic")}',
            'description': 'Implement a solution that demonstrates your understanding of the course concepts.',
            'starter_code': '# Write your solution here\ndef solve_problem():\n    pass',
            'test_cases': [
                {'input': 'test1', 'expected_output': 'result1'},
                {'input': 'test2', 'expected_output': 'result2'}
            ],
            'hints': [
                'Consider the main concepts from the course',
                'Break down the problem into smaller steps'
            ]
        }
    
    elif assignment_type == 'written':
        # Generate written questions using Gemini
        prompt = f"""Generate {num_questions} written assignment questions based on the following course content:

Course Title: {course_content.get('title', 'N/A')}
Course Description: {course_content.get('description', 'N/A')}
Category: {course_content.get('category', 'N/A')}

Generate questions in the following JSON format:
[
  {{
    "question_text": "Question text here",
    "question_type": "short_answer",
    "points": 10
  }},
  {{
    "question_text": "Multiple choice question",
    "question_type": "mcq",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option B",
    "points": 5
  }},
  {{
    "question_text": "True/False statement",
    "question_type": "true_false",
    "correct_answer": "True",
    "points": 3
  }}
]

Requirements:
- Mix of question types: short_answer, mcq, true_false
- Questions should assess deep understanding of course content
- Assign appropriate points based on difficulty
- Return ONLY valid JSON array, no additional text

Generate exactly {num_questions} questions."""

        response = call_gemini_api(prompt)
        
        if response:
            try:
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0].strip()
                else:
                    json_str = response.strip()
                
                questions = json.loads(json_str)
                return questions[:num_questions]
            except Exception as e:
                print(f"Error parsing Gemini written questions: {str(e)}")
        
        # Fallback
        questions = [
            {
                'question_text': f'Explain the main concepts covered in {course_content.get("title", "this course")}.',
                'question_type': 'short_answer',
                'points': 10
            },
            {
                'question_text': 'Which of the following is a key principle?',
                'question_type': 'mcq',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 'Option B',
                'points': 5
            },
            {
                'question_text': 'The fundamental concept is always applicable.',
                'question_type': 'true_false',
                'correct_answer': 'False',
                'points': 3
            },
            {
                'question_text': 'Describe a practical application of what you learned.',
                'question_type': 'short_answer',
                'points': 15
            },
            {
                'question_text': 'What are the limitations of this approach?',
                'question_type': 'short_answer',
                'points': 12
            }
        ]
        
        return random.sample(questions, min(num_questions, len(questions)))
    
    else:  # mixed
        return {
            'written_questions': generate_assignment_questions(course_content, 'written', num_questions // 2),
            'coding_problem': generate_assignment_questions(course_content, 'coding', 1)
        }


def get_grading_assistance(submission, student_quiz_performance):
    """
    Provide AI assistance for grading assignments
    
    Args:
        submission: AssignmentSubmission object
        student_quiz_performance: List of quiz scores
    
    Returns:
        Dictionary with grading suggestions
    """
    # This is a placeholder implementation
    
    avg_quiz_score = sum(student_quiz_performance) / len(student_quiz_performance) if student_quiz_performance else 0
    
    suggestions = {
        'consistency_check': 'Student performance is consistent with quiz scores' if avg_quiz_score > 60 else 'Performance differs from quiz scores - review carefully',
        'recommended_score_range': f'{max(0, avg_quiz_score - 10)}-{min(100, avg_quiz_score + 10)}',
        'notes': []
    }
    
    if submission.warnings_count > 0:
        suggestions['notes'].append(f'Student received {submission.warnings_count} warnings during assignment')
    
    if avg_quiz_score >= 80:
        suggestions['notes'].append('Strong quiz performance suggests good understanding')
    elif avg_quiz_score < 50:
        suggestions['notes'].append('Low quiz scores - student may need additional support')
    
    return suggestions


def analyze_assignment_performance(submissions):
    """
    Analyze overall assignment performance and provide recommendations
    
    Args:
        submissions: List of AssignmentSubmission objects
    
    Returns:
        Dictionary with analysis and recommendations
    """
    if not submissions:
        return {
            'recommendations': ['No submissions yet to analyze'],
            'difficulty_assessment': 'unknown'
        }
    
    graded = [s for s in submissions if s.status == 'graded']
    if not graded:
        return {
            'recommendations': ['Grade submissions to get analysis'],
            'difficulty_assessment': 'unknown'
        }
    
    avg_score = sum(s.percentage for s in graded) / len(graded)
    pass_rate = sum(1 for s in graded if s.passed) / len(graded) * 100
    
    recommendations = []
    
    if avg_score < 40:
        difficulty = 'too_hard'
        recommendations.append('Assignment may be too difficult - consider simplifying or providing more guidance')
        recommendations.append('Review if instructions are clear and requirements are reasonable')
    elif avg_score > 90:
        difficulty = 'too_easy'
        recommendations.append('Assignment may be too easy - consider increasing complexity')
        recommendations.append('Add more challenging questions to better assess understanding')
    else:
        difficulty = 'appropriate'
        recommendations.append('Assignment difficulty appears appropriate')
    
    if pass_rate < 50:
        recommendations.append('Low pass rate - review passing score threshold')
    
    # Analyze time taken
    avg_time = sum(s.time_taken_minutes for s in graded) / len(graded)
    if avg_time < 30:
        recommendations.append('Students completing quickly - may need more content')
    elif avg_time > 120:
        recommendations.append('Students taking long time - consider reducing scope')
    
    return {
        'recommendations': recommendations,
        'difficulty_assessment': difficulty,
        'average_score': round(avg_score, 2),
        'pass_rate': round(pass_rate, 2),
        'average_time_minutes': round(avg_time, 2)
    }
