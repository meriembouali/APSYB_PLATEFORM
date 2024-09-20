import json
from django.shortcuts import render
from .utils import *
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from django.utils import timezone



@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def dashboard_inscription(request):
    current_year = timezone.now().year
    monthly_inscriptions = inscriptions_par_mois()
    yearly_inscriptions = inscriptions_par_annee()
    comparison_data = comparaison_mois()
    data_par_annee = taux_inscriptions_par_mois()
    taux_participation = taux_participation_mensuel()

    chart_labels = [entry['year'].year for entry in yearly_inscriptions]
    chart_data = [entry['total'] for entry in yearly_inscriptions]

    chart_labels_participation = [entry['month'].strftime('%B %Y') for entry in taux_participation]
    chart_data_participation = [entry['taux'] for entry in taux_participation]
    total_inscriptions = [entry['total'] for entry in taux_participation]
    total_participants = [entry['participants'] for entry in taux_participation]


    return render(request, 'dashboard/dashboard_inscription.html', {
        'current_year':current_year,
        'monthly_inscriptions': monthly_inscriptions,
        'comparison_data': comparison_data,
        'data_par_annee':json.dumps(data_par_annee),
        'chart_labels': json.dumps(chart_labels),  
        'chart_data': json.dumps(chart_data), 
        'taux_participation':taux_participation,
        'chart_labels_participation': json.dumps(chart_labels_participation),
        'chart_data_participation': json.dumps(chart_data_participation),
        'total_inscriptions': json.dumps(total_inscriptions),
        'total_participants': json.dumps(total_participants),   
    })


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def dashboard_participation(request):
    taux_participation = taux_participation_mensuel()
    chart_labels_mensuel = [entry['month'].strftime('%B %Y') for entry in taux_participation]
    chart_data_mensuel = [entry['taux'] for entry in taux_participation]
    total_inscriptions = [entry['total'] for entry in taux_participation]
    total_participants = [entry['participants'] for entry in taux_participation]

    taux_annuel = taux_participation_annuel()
    chart_labels_annuel = [entry['year'].year for entry in taux_annuel]
    chart_data_annuel = [entry['taux'] for entry in taux_annuel]

    return render(request, 'dashboard/dashboard_participation.html', {
            'taux_participation':taux_participation,
            'chart_labels_mensuel': json.dumps(chart_labels_mensuel),
            'chart_data_mensuel': json.dumps(chart_data_mensuel),
            'total_inscriptions': json.dumps(total_inscriptions),
            'total_participants': json.dumps(total_participants), 
            'chart_labels_annuel': json.dumps(chart_labels_annuel),
            'chart_data_annuel': json.dumps(chart_data_annuel),  
        })


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def generer_rapport_mensuel(request):
    month_name = timezone.now().strftime('%B')
    current_year = timezone.now().year
    total_registrations = total_registrations_month()
    comparison = compare_with_previous_month()
    top_events = top_3_events()
    event_details = event_registration_details()
    top_users = top_participants_month()

    
    html_string = render_to_string('dashboard/rapports/rapport_mensuel.html', {
        'month_name':month_name,
        'year':current_year,
        'total_registrations': total_registrations,
        'comparison': comparison,
        'top_events': top_events,
        'event_details': event_details,
        'top_users': top_users,
    })
    
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    filename = f"rapport_mensuel_{month_name}_{current_year}.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def generer_rapport_annuel(request):
    current_year = timezone.now().year
    total_registrations = total_registrations_year()
    comparison = compare_with_previous_year()
    top_events = top_3_events_year()
    event_details = event_registration_details_year()
    top_users = top_participants_year()

    html_string = render_to_string('dashboard/rapports/rapport_annuel.html', {
        'year':current_year,
        'total_registrations': total_registrations,
        'comparison': comparison,
        'top_events': top_events,
        'event_details': event_details,
        'top_users': top_users,
    })

    html = HTML(string=html_string)
    pdf = html.write_pdf()

    filename = f"rapport_annuel_{current_year}.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response