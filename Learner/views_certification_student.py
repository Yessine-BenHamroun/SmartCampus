"""
Student Certification Views
Handles certification enrollment, progress tracking, and badge earning for students
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from Learner.api_auth import api_login_required, get_access_token, get_current_user
import requests


@api_login_required
def enroll_in_certification(request, certification_id):
    """Enroll student in a certification"""
    access_token = get_access_token(request)
    
    try:
        response = requests.post(
            f'http://localhost:8001/api/certifications/{certification_id}/enroll/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            messages.success(request, data.get('message', 'Successfully enrolled in certification!'))
            # Redirect to certification steps page
            return redirect('certification_steps', certification_id=certification_id)
        else:
            error_data = response.json()
            messages.error(request, error_data.get('error', 'Failed to enroll in certification'))
    except Exception as e:
        messages.error(request, f'Error enrolling in certification: {str(e)}')
        print(f"❌ Enrollment error: {str(e)}")
    
    # Redirect back to referrer or course list
    return redirect(request.META.get('HTTP_REFERER', 'my_courses'))


@api_login_required
def certification_steps_view(request, certification_id):
    """View certification steps and progress (Student)"""
    access_token = get_access_token(request)
    user = get_current_user(request)
    
    certification = None
    steps = []
    progress = None
    course = None
    
    try:
        # Fetch certification details and steps
        steps_response = requests.get(
            f'http://localhost:8001/api/certifications/{certification_id}/steps/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if steps_response.status_code == 200:
            data = steps_response.json()
            certification = data.get('certification', {})
            steps = data.get('steps', [])
        
        # Fetch student progress
        progress_response = requests.get(
            'http://localhost:8001/api/certifications/my-progress/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if progress_response.status_code == 200:
            progress_data = progress_response.json()
            all_progress = progress_data.get('progress', [])
            # Find progress for this certification
            progress = next((p for p in all_progress if p.get('certification_id') == certification_id), None)
        
        # Fetch course details
        if certification:
            course_id = certification.get('course_id')
            course_response = requests.get(
                f'http://localhost:8001/api/courses/{course_id}/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            if course_response.status_code == 200:
                course = course_response.json().get('course', {})
    
    except Exception as e:
        messages.error(request, f'Error loading certification: {str(e)}')
        print(f"❌ Error in certification_steps_view: {str(e)}")
    
    # Filter out exam steps (exams are not regular steps)
    # Exam is shown separately in the "Final Exam" section
    regular_steps = [s for s in steps if s.get('step_type') != 'exam']
    
    # Sort steps by step_number
    regular_steps.sort(key=lambda x: x.get('step_number', 0))
    
    # Check if all regular steps are completed
    all_steps_completed = False
    if progress and regular_steps:
        completed_step_ids = progress.get('completed_steps', [])
        regular_step_ids = [s.get('id') for s in regular_steps]
        all_steps_completed = all(step_id in completed_step_ids for step_id in regular_step_ids)
    
    # Update certification total_steps to reflect only regular steps (excluding exam)
    if certification:
        certification['total_steps'] = len(regular_steps)
    
    context = {
        'certification': certification,
        'steps': regular_steps,
        'progress': progress,
        'course': course,
        'all_steps_completed': all_steps_completed,
        'page_title': f"{certification.get('title', 'Certification')} - Steps" if certification else 'Certification Steps'
    }
    
    return render(request, 'learner/certification_steps.html', context)


@api_login_required
def complete_certification_step(request, step_id):
    """Mark a certification step as completed"""
    if request.method != 'POST':
        return redirect('my_courses')
    
    access_token = get_access_token(request)
    
    try:
        # Get score from form if it's a quiz/exam
        score = request.POST.get('score')
        
        payload = {'step_id': step_id}
        if score:
            payload['score'] = float(score)
        
        response = requests.post(
            'http://localhost:8001/api/certifications/steps/complete/',
            json=payload,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            messages.success(request, data.get('message', 'Step completed successfully!'))
            
            # Check if badge was earned
            progress = data.get('progress', {})
            if progress.get('badge_earned'):
                messages.success(request, '🎉 Congratulations! You earned a badge!')
        else:
            error_data = response.json()
            messages.error(request, error_data.get('error', 'Failed to complete step'))
    
    except Exception as e:
        messages.error(request, f'Error completing step: {str(e)}')
        print(f"❌ Error completing step: {str(e)}")
    
    # Redirect back to referrer
    return redirect(request.META.get('HTTP_REFERER', 'my_courses'))


@api_login_required
def submit_certification_exam(request, certification_id):
    """Submit final exam for certification"""
    if request.method != 'POST':
        return redirect('certification_steps', certification_id=certification_id)
    
    access_token = get_access_token(request)
    
    try:
        # Get answers from form
        import json
        answers = request.POST.get('answers')
        
        if answers:
            answers = json.loads(answers)
        else:
            # Collect answers from individual form fields
            answers = {}
            for key in request.POST:
                if key.startswith('answer_'):
                    question_id = key.replace('answer_', '')
                    answers[question_id] = request.POST[key]
        
        payload = {'answers': answers}
        
        response = requests.post(
            f'http://localhost:8001/api/certifications/{certification_id}/exam/submit/',
            json=payload,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            score = data.get('score', 0)
            passed = data.get('passed', False)
            
            if passed:
                messages.success(request, f'🎉 Congratulations! You passed with {score}%!')
                if data.get('badge_earned'):
                    messages.success(request, '🏆 You earned a certification badge!')
                return redirect('my_badges')
            else:
                attempts_left = data.get('attempts_left', 0)
                if attempts_left > 0:
                    messages.warning(request, f'You scored {score}%. You have {attempts_left} attempts remaining.')
                else:
                    messages.error(request, f'You scored {score}%. No attempts remaining.')
        else:
            error_data = response.json()
            messages.error(request, error_data.get('error', 'Failed to submit exam'))
    
    except Exception as e:
        messages.error(request, f'Error submitting exam: {str(e)}')
        print(f"❌ Error submitting exam: {str(e)}")
    
    return redirect('certification_steps', certification_id=certification_id)


@api_login_required
def my_certification_progress_view(request):
    """View all certification progress for the current student"""
    access_token = get_access_token(request)
    user = get_current_user(request)
    
    progress_list = []
    certifications_data = {}
    
    try:
        # Fetch all progress
        progress_response = requests.get(
            'http://localhost:8001/api/certifications/my-progress/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if progress_response.status_code == 200:
            data = progress_response.json()
            progress_list = data.get('progress', [])
            
            # Fetch certification details for each progress and add to progress item
            for prog in progress_list:
                cert_id = prog.get('certification_id')
                if cert_id:
                    cert_response = requests.get(
                        f'http://localhost:8001/api/certifications/{cert_id}/steps/',
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    if cert_response.status_code == 200:
                        cert_data = cert_response.json()
                        # Add certification data directly to progress item
                        prog['certification'] = cert_data.get('certification', {})
                    else:
                        prog['certification'] = {'title': 'Unknown Certification', 'total_steps': 0}
    
    except Exception as e:
        messages.error(request, f'Error loading progress: {str(e)}')
        print(f"❌ Error in my_certification_progress_view: {str(e)}")
    
    context = {
        'progress_list': progress_list,
        'page_title': 'My Certification Progress'
    }
    
    return render(request, 'learner/my_certification_progress.html', context)


def verify_badge_view(request, verification_code):
    """Public view to verify a badge by its verification code"""
    import requests
    
    badge = None
    error = None
    
    try:
        # Call backend API to verify badge
        response = requests.get(
            f'http://localhost:8001/api/certifications/verify/{verification_code}/'
        )
        
        if response.status_code == 200:
            badge = response.json().get('badge', {})
        else:
            error = "Badge not found or verification code is invalid."
    
    except Exception as e:
        error = f"Error verifying badge: {str(e)}"
        print(f"❌ Error in verify_badge_view: {str(e)}")
    
    context = {
        'badge': badge,
        'error': error,
        'verification_code': verification_code,
        'page_title': 'Verify Badge'
    }
    
    return render(request, 'learner/verify_badge.html', context)
