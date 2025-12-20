from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.core.management import call_command
from django.conf import settings
import os
import subprocess
from datetime import datetime

@login_required
def backup_list(request):
    if request.user.user_type != 'admin':
        messages.error(request, "Only admins can access backup management.")
        return redirect('dashboard')
    
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    backups = []
    for filename in os.listdir(backup_dir):
        if filename.endswith('.sql') or filename.endswith('.dump'):
            filepath = os.path.join(backup_dir, filename)
            size = os.path.getsize(filepath) / (1024 * 1024)
            modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            backups.append({
                'filename': filename,
                'size': f'{size:.2f} MB',
                'date': modified.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    backups.sort(key=lambda x: x['date'], reverse=True)
    
    context = {
        'backups': backups,
        'title': 'Database Backups'
    }
    return render(request, 'system/backup_list.html', context)

@login_required
def create_backup(request):
    if request.user.user_type != 'admin':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        db_config = settings.DATABASES['default']
        filename = f'backup_{timestamp}.sql'
        destination = os.path.join(backup_dir, filename)
        
        # PostgreSQL complete backup (schema + data with column-inserts)
        cmd = [
            'pg_dump',
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '--clean',
            '--if-exists',
            '--column-inserts',
            '-f', destination
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            return JsonResponse({'success': False, 'error': f'Backup failed: {result.stderr}'})
        
        backup_size = os.path.getsize(destination)
        
        return JsonResponse({
            'success': True,
            'message': f'Backup created successfully! Size: {backup_size / (1024*1024):.2f} MB',
            'filename': filename
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def restore_backup(request):
    if request.user.user_type != 'admin':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    try:
        from django.db import connection
        
        filename = request.POST.get('filename')
        backup_path = os.path.join('backups', filename)
        
        if not os.path.exists(backup_path):
            return JsonResponse({'success': False, 'error': 'Backup file not found'})
        
        connection.close()
        
        db_config = settings.DATABASES['default']
        
        # PostgreSQL restore using psql (for plain SQL)
        cmd = [
            'psql',
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', backup_path
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            return JsonResponse({'success': False, 'error': f'Restore failed: {result.stderr}'})
        
        return JsonResponse({
            'success': True,
            'message': 'Database restored successfully! Please restart the server.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def create_backup_file():
    """Create backup file and return filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    db_config = settings.DATABASES['default']
    filename = f'backup_{timestamp}.sql'
    destination = os.path.join(backup_dir, filename)
    
    cmd = [
        'pg_dump',
        '-h', db_config['HOST'],
        '-p', str(db_config['PORT']),
        '-U', db_config['USER'],
        '-d', db_config['NAME'],
        '--clean',
        '--if-exists',
        '--column-inserts',
        '-f', destination
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = db_config['PASSWORD']
    
    subprocess.run(cmd, env=env, check=True)
    
    return filename

@login_required
def download_backup(request, filename):
    if request.user.user_type != 'admin':
        messages.error(request, "Permission denied")
        return redirect('backup_list')
    
    filepath = os.path.join('backups', filename)
    if os.path.exists(filepath):
        response = FileResponse(open(filepath, 'rb'), as_attachment=True)
        response['Content-Type'] = 'application/sql'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = os.path.getsize(filepath)
        return response
    else:
        messages.error(request, "Backup file not found")
        return redirect('backup_list')

@login_required
def delete_backup(request):
    if request.user.user_type != 'admin':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    try:
        filename = request.POST.get('filename')
        filepath = os.path.join('backups', filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return JsonResponse({'success': True, 'message': 'Backup deleted successfully'})
        else:
            return JsonResponse({'success': False, 'error': 'Backup file not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
