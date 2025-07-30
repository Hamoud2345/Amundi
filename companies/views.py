from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from .models import Company, ChatHistory
from .serializers import CompanySerializer

# Create your views here.
# companies/views.py
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    authentication_classes = []
    permission_classes = []


from rest_framework.decorators import api_view
from rest_framework.response import Response
from agent.langgraph_agent import run_chat
import uuid

# Web Interface Views
def chat_interface(request):
    """Main chat interface"""
    return render(request, 'chat.html')

def companies_interface(request):
    """Companies list interface"""
    companies = Company.objects.all()
    sectors = Company.objects.values_list('sector', flat=True).distinct()
    return render(request, 'companies.html', {
        'companies': companies,
        'sectors': sectors
    })

def upload_interface(request):
    """CSV upload interface"""
    return render(request, 'upload.html')

def history_interface(request):
    """Chat history interface"""
    recent_chats = ChatHistory.objects.all()[:50]
    return render(request, 'history.html', {
        'chats': recent_chats
    })

# API Endpoints
@csrf_exempt
@api_view(["POST"])
def chat(request):
    user_msg = request.data.get("message", "")
    session_id = request.data.get("session_id", str(uuid.uuid4()))
    
    # Get bot response
    answer = run_chat(user_msg)
    
    # Save to chat history
    ChatHistory.objects.create(
        user_message=user_msg,
        bot_response=answer,
        session_id=session_id
    )
    
    return Response({
        "answer": answer,
        "session_id": session_id
    })

@csrf_exempt
@api_view(["POST"])
def upload_companies_csv(request):
    """Upload companies from CSV file"""
    import csv
    import io
    
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=400)
    
    csv_file = request.FILES['file']
    
    if not csv_file.name.endswith('.csv'):
        return Response({"error": "File must be CSV format"}, status=400)
    
    try:
        # Read CSV file
        decoded_file = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(decoded_file))
        
        created_count = 0
        errors = []
        
        for row in csv_data:
            try:
                # Expected CSV columns: name, description, sector, financials
                company, created = Company.objects.get_or_create(
                    name=row.get('name', '').strip(),
                    defaults={
                        'description': row.get('description', ''),
                        'sector': row.get('sector', ''),
                        'financials': eval(row.get('financials', '{}')) if row.get('financials') else {}
                    }
                )
                if created:
                    created_count += 1
            except Exception as e:
                errors.append(f"Row {row}: {str(e)}")
        
        return Response({
            "message": f"Successfully imported {created_count} companies",
            "errors": errors if errors else None
        })
        
    except Exception as e:
        return Response({"error": f"Error processing CSV: {str(e)}"}, status=400)

@api_view(["GET"])
def chat_history(request):
    """Get recent chat history"""
    session_id = request.GET.get('session_id')
    
    if session_id:
        chats = ChatHistory.objects.filter(session_id=session_id)[:20]
    else:
        chats = ChatHistory.objects.all()[:20]
    
    chat_data = [
        {
            "user_message": chat.user_message,
            "bot_response": chat.bot_response,
            "timestamp": chat.timestamp,
            "session_id": chat.session_id
        }
        for chat in chats
    ]
    
    return Response({"chats": chat_data})