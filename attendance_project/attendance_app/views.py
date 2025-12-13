from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from .models import Teacher, Student, Subject, Attendance

def home(request):
    return render(request,'home.html')

def student_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                student = Student.objects.get(user=user)
                login(request, user)
                return redirect('student_profile', student_id=student.id)
            except Student.DoesNotExist:
                return render(request, 'student_login.html', {
                    'error': 'This account is not a student'
                })
        else:
            return render(request, 'student_login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'student_login.html')



# ✅ Teacher Login
def teacher_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                teacher = Teacher.objects.get(user=user)
                login(request, user)
                return redirect('dashboard')
            except Teacher.DoesNotExist:
                return render(request, 'login.html', {'error': 'Not a registered teacher'})
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def student_logout(request):
    logout(request)
    return redirect('student_login')

# ✅ Logout
def teacher_logout(request):
    logout(request)
    return redirect('login')


# ✅ Dashboard
@login_required
def dashboard(request):
    teacher = Teacher.objects.get(user=request.user)
    return render(request, 'dashboard.html', {'teacher': teacher})


# ✅ Mark Attendance
@login_required
def mark_attendance(request):
    teacher = Teacher.objects.get(user=request.user)
    students = Student.objects.all()

    if request.method == 'POST':
        date = request.POST.get('date')
        if not date:
                messages.error(request, "Please select a date.")
                return redirect('mark_attendance')
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            Attendance.objects.update_or_create(
                student=student,
                subject=teacher.subject,
                date=date,
                defaults={'status': status}
            )
        messages.success(request, "Attendance successfully saved!")
        return redirect('mark_attendance')

    today = timezone.now().date()
    return render(request, 'mark_attendance.html', {
        'students': students,
        'today': today,
    })


# ✅ View Attendance Summary (Teacher)
@login_required
def view_attendance(request):
    teacher = Teacher.objects.get(user=request.user)
    subject = teacher.subject
    students = Student.objects.all()

    attendance_data = []
    for student in students:
        total = Attendance.objects.filter(subject=subject, student=student).count()
        present = Attendance.objects.filter(subject=subject, student=student, status='Present').count()
        percentage = round((present / total) * 100, 2) if total > 0 else 0

        attendance_data.append({
            'student': student,
            'total': total,
            'present': present,
            'percentage': percentage,
        })

    return render(request, 'view_attendance.html', {'data': attendance_data, 'subject': subject})





@login_required
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Get date filters from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    subjects = Subject.objects.all()
    data = []

    for subject in subjects:
        attendance_qs = Attendance.objects.filter(student=student, subject=subject)

        # Apply date filter if selected
        if from_date and to_date:
            attendance_qs = attendance_qs.filter(
                date__range=[from_date, to_date]
            )

        total = attendance_qs.count()
        present = attendance_qs.filter(status='Present').count()
        percentage = round((present / total) * 100, 2) if total > 0 else 0

        data.append({
            'subject': subject,
            'present': present,
            'total': total,
            'percentage': percentage,
        })

    context = {
        'student': student,
        'data': data,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, 'student_profile.html', context)
