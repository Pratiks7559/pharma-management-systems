from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.core.management import call_command
import os
import shutil
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
        if filename.endswith('.sqlite3'):
            filepath = os.path.join(backup_dir, filename)
            size = os.path.getsize(filepath) / (1024 * 1024)  # MB
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
        import sqlite3
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        source = 'db.sqlite3'
        destination = os.path.join(backup_dir, f'backup_{timestamp}.sqlite3')
        
        # Use SQLite backup API for proper database copy
        source_conn = sqlite3.connect(source)
        backup_conn = sqlite3.connect(destination)
        
        # Perform backup
        with backup_conn:
            source_conn.backup(backup_conn)
        
        source_conn.close()
        backup_conn.close()
        
        # Verify backup file size
        source_size = os.path.getsize(source)
        backup_size = os.path.getsize(destination)
        
        if backup_size < source_size * 0.9:  # Backup should be at least 90% of original
            os.remove(destination)
            return JsonResponse({
                'success': False,
                'error': 'Backup verification failed. File size mismatch.'
            })
        
        return JsonResponse({
            'success': True,
            'message': f'Backup created successfully! Size: {backup_size / (1024*1024):.2f} MB',
            'filename': f'backup_{timestamp}.sqlite3'
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
        import sqlite3
        from django.db import connection
        
        filename = request.POST.get('filename')
        backup_path = os.path.join('backups', filename)
        
        if not os.path.exists(backup_path):
            return JsonResponse({'success': False, 'error': 'Backup file not found'})
        
        # Verify backup file integrity
        try:
            test_conn = sqlite3.connect(backup_path)
            test_conn.execute('SELECT 1')
            test_conn.close()
        except:
            return JsonResponse({'success': False, 'error': 'Backup file is corrupted'})
        
        # Close all database connections
        connection.close()
        
        # Create safety backup before restore
        safety_backup = f'backups/before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
        
        # Use SQLite backup API for safety backup
        source_conn = sqlite3.connect('db.sqlite3')
        safety_conn = sqlite3.connect(safety_backup)
        with safety_conn:
            source_conn.backup(safety_conn)
        source_conn.close()
        safety_conn.close()
        
        # Restore from backup
        backup_conn = sqlite3.connect(backup_path)
        restore_conn = sqlite3.connect('db.sqlite3')
        with restore_conn:
            backup_conn.backup(restore_conn)
        backup_conn.close()
        restore_conn.close()
        
        return JsonResponse({
            'success': True,
            'message': 'Database restored successfully! Please restart the server.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def create_backup_file():
    """Create backup file and return filename"""
    import sqlite3
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    source = 'db.sqlite3'
    filename = f'backup_{timestamp}.sqlite3'
    destination = os.path.join(backup_dir, filename)
    
    source_conn = sqlite3.connect(source)
    backup_conn = sqlite3.connect(destination)
    
    with backup_conn:
        source_conn.backup(backup_conn)
    
    source_conn.close()
    backup_conn.close()
    
    return filename

@login_required
def download_backup(request, filename):
    if request.user.user_type != 'admin':
        messages.error(request, "Permission denied")
        return redirect('backup_list')
    
    filepath = os.path.join('backups', filename)
    if os.path.exists(filepath):
        response = FileResponse(open(filepath, 'rb'), as_attachment=True)
        response['Content-Type'] = 'application/x-sqlite3'
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
