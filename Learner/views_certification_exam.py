"""
Certification Final Exam Views
Handles creation, management, and taking of certification final exams
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from Learner.api_auth import api_login_required, get_access_token, get_current_user
import requests
import json


@api_login_required
def create_certification_exam_view(request, certification_id):
    """Create final exam for certification (Instructor only)"""
    user = get_current_user(request)
    user_role = user.get('role', 'student')
    
    if user_role not in ['instructor', 'admin']:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('index')
    
    access_token = get_access_token(request)
    certification = None
    
    try:
        # Fetch certification details
        cert_response = requests.get(
            f'http://localhost:8001/api/certifications/{certification_id}/steps/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if cert_response.status_code == 200:
            data = cert_response.json()
            certification = data.get('certification', {})
    except Exception as e:
        messages.error(request, f'Error loading certification: {str(e)}')
    
    if request.method == 'POST':
        try:
            # Get form data
            exam_title = request.POST.get('exam_title')
            exam_description = request.POST.get('exam_description')
            passing_score = int(request.POST.get('passing_score', 70))
            time_limit = int(request.POST.get('time_limit', 60))
            max_attempts = int(request.POST.get('max_attempts', 3))
            shuffle_questions = request.POST.get('shuffle_questions') == 'on'
            show_correct_answers = request.POST.get('show_correct_answers') == 'on'
            
            # Get questions from form
            questions = []
            question_count = int(request.POST.get('question_count', 0))
            
            for i in range(question_count):
                question_text = request.POST.get(f'question_{i}_text')
                question_type = request.POST.get(f'question_{i}_type', 'multiple_choice')
                question_points = int(request.POST.get(f'question_{i}_points', 1))
                
                if not question_text:
                    continue
                
                question = {
                    'question_text': question_text,
                    'question_type': question_type,
                    'points': question_points,
                    'options': [],
                    'correct_answer': None
                }
                
                if question_type == 'multiple_choice':
                    # Get options
                    options = []
                    for j in range(4):  # 4 options
                        option_text = request.POST.get(f'question_{i}_option_{j}')
                        if option_text:
                            options.append(option_text)
                    
                    question['options'] = options
                    question['correct_answer'] = int(request.POST.get(f'question_{i}_correct', 0))
                
                elif question_type == 'true_false':
                    question['options'] = ['True', 'False']
                    question['correct_answer'] = 0 if request.POST.get(f'question_{i}_correct') == 'true' else 1
                
                questions.append(question)
            
            # Create exam step
            step_data = {
                'certification_id': certification_id,
                'step_number': 999,  # Last step
                'step_type': 'exam',
                'title': exam_title,
                'description': exam_description,
                'is_mandatory': True,
                'duration_minutes': time_limit,
                'content': {
                    'questions': questions,
                    'passing_score': passing_score,
                    'time_limit_minutes': time_limit,
                    'max_attempts': max_attempts,
                    'shuffle_questions': shuffle_questions,
                    'show_correct_answers': show_correct_answers
                }
            }
            
            print(f"📤 Sending exam data to backend: {json.dumps(step_data, indent=2)}")
            
            response = requests.post(
                f'http://localhost:8001/api/certifications/{certification_id}/steps/add/',
                json=step_data,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            print(f"📥 Backend response status: {response.status_code}")
            print(f"📥 Backend response body: {response.text}")
            
            if response.status_code in [200, 201]:
                messages.success(request, 'Final exam created successfully!')
                return redirect('manage_certification_steps', certification_id=certification_id)
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', str(error_data))
                except:
                    error_message = response.text
                messages.error(request, f'Failed to create exam: {error_message}')
                print(f"❌ Error from backend: {error_message}")
        
        except Exception as e:
            messages.error(request, f'Error creating exam: {str(e)}')
            print(f"❌ Error: {str(e)}")
    
    context = {
        'certification': certification,
        'certification_id': certification_id,
        'page_title': 'Create Final Exam'
    }
    
    return render(request, 'learner/create_certification_exam.html', context)


@api_login_required
def take_certification_exam_view(request, certification_id):
    """Take certification final exam (Student)"""
    access_token = get_access_token(request)
    user = get_current_user(request)
    
    certification = None
    exam_step = None
    progress = None
    can_take_exam = False
    attempts_remaining = 0
    
    try:
        # Fetch certification and steps
        steps_response = requests.get(
            f'http://localhost:8001/api/certifications/{certification_id}/steps/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if steps_response.status_code == 200:
            data = steps_response.json()
            certification = data.get('certification', {})
            steps = data.get('steps', [])
            
            # Find exam step
            exam_step = next((s for s in steps if s.get('step_type') == 'exam'), None)
        
        # Fetch student progress
        progress_response = requests.get(
            'http://localhost:8001/api/certifications/my-progress/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if progress_response.status_code == 200:
            progress_data = progress_response.json()
            all_progress = progress_data.get('progress', [])
            progress = next((p for p in all_progress if p.get('certification_id') == certification_id), None)
            
            if progress and exam_step:
                # Check if all steps are completed
                total_steps = certification.get('total_steps', 0)
                current_step = progress.get('current_step', 0)
                exam_attempts = progress.get('exam_attempts', 0)
                max_attempts = exam_step.get('content', {}).get('max_attempts', 3)
                
                can_take_exam = (current_step >= total_steps - 1) and (exam_attempts < max_attempts)
                attempts_remaining = max_attempts - exam_attempts
    
    except Exception as e:
        messages.error(request, f'Error loading exam: {str(e)}')
        print(f"❌ Error: {str(e)}")
    
    if request.method == 'POST':
        if not can_take_exam:
            messages.error(request, 'You cannot take the exam at this time.')
            return redirect('certification_steps', certification_id=certification_id)
        
        try:
            # Collect answers
            answers = {}
            questions = exam_step.get('content', {}).get('questions', [])
            
            for i, question in enumerate(questions):
                answer_key = f'question_{i}'
                answer_value = request.POST.get(answer_key)
                
                if answer_value is not None:
                    # Convert to int for MCQ/True-False
                    try:
                        answers[str(i)] = int(answer_value)
                    except:
                        answers[str(i)] = answer_value
            
            # Submit exam
            # Calculate time taken (you can track this with JavaScript if needed)
            # For now, we'll use the time limit or a default value
            time_limit = exam_step.get('content', {}).get('time_limit_minutes', 60)
            time_taken = time_limit if time_limit > 0 else 30  # Default to 30 minutes if no limit
            
            print(f"📤 Submitting exam answers: {answers}")
            print(f"⏱️ Time taken: {time_taken} minutes")
            
            response = requests.post(
                f'http://localhost:8001/api/certifications/{certification_id}/exam/submit/',
                json={
                    'answers': answers,
                    'time_taken_minutes': time_taken
                },
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            print(f"📥 Backend response status: {response.status_code}")
            print(f"📥 Backend response body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                score = result.get('score', 0)
                passed = result.get('passed', False)
                
                print(f"✅ Exam results - Score: {score}%, Passed: {passed}")
                
                if passed:
                    messages.success(request, f'🎉 Congratulations! You passed with {score:.1f}%! Badge earned!')
                    return redirect('my_badges')
                else:
                    attempts_left = result.get('attempts_left', 0)
                    if attempts_left > 0:
                        messages.warning(request, f'Score: {score:.1f}%. You have {attempts_left} attempt(s) remaining.')
                    else:
                        messages.error(request, f'Score: {score:.1f}%. No attempts remaining.')
                    return redirect('certification_steps', certification_id=certification_id)
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', str(error_data))
                except:
                    error_message = response.text
                messages.error(request, f'Failed to submit exam: {error_message}')
                print(f"❌ Backend error: {error_message}")
        
        except Exception as e:
            messages.error(request, f'Error submitting exam: {str(e)}')
            print(f"❌ Submission error: {str(e)}")
        
        return redirect('certification_steps', certification_id=certification_id)
    
    context = {
        'certification': certification,
        'exam_step': exam_step,
        'progress': progress,
        'can_take_exam': can_take_exam,
        'attempts_remaining': attempts_remaining,
        'page_title': f'Final Exam - {certification.get("title", "Certification") if certification else "Certification"}'
    }
    
    return render(request, 'learner/take_certification_exam.html', context)
