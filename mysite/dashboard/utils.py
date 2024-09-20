from Inscription.models import Inscription
from django.db.models.functions import TruncMonth,TruncYear
from django.utils import timezone
from django.db.models import Count,Case,When,FloatField,Sum
import calendar
from main.models import Evenement
from Inscription.models import Inscription
import matplotlib.pyplot as plt
import io
import base64


# Affichage du nombre total d'inscriptions par mois.
def inscriptions_par_mois():
    current_year = timezone.now().year
    inscriptions_by_month = (Inscription.objects.filter(date_inscription__year=current_year)
                             .annotate(month=TruncMonth('date_inscription'))
                             .values('month')
                             .annotate(total=Count('id'))
                             .order_by('month'))

    return inscriptions_by_month



# les inscriptions totales par année.
def inscriptions_par_annee():
    current_year = timezone.now().year
    inscriptions_by_year = (Inscription.objects
                            .filter(date_inscription__year__lte=current_year)
                            .annotate(year=TruncYear('date_inscription'))
                            .values('year')
                            .annotate(total=Count('id'))
                            .order_by('year'))

    return inscriptions_by_year


#Comparaison Mois/Mois 
def comparaison_mois():
    current_year = timezone.now().year
    previous_year = current_year - 1


    current_year_inscriptions =(Inscription.objects.filter(date_inscription__year=current_year)
                                .annotate(month=TruncMonth('date_inscription'))
                                .values('month')
                                .annotate(total=Count('id'))
                                .order_by('month'))
    

    previous_year_inscriptions = (Inscription.objects.filter(date_inscription__year=previous_year)
                                .annotate(month=TruncMonth('date_inscription'))
                                .values('month')
                                .annotate(total=Count('id'))
                                .order_by('month'))
    
    current_year_dict = {entry['month'].strftime("%m"): entry['total'] for entry in current_year_inscriptions}
    previous_year_dict = {entry['month'].strftime("%m"): entry['total'] for entry in previous_year_inscriptions}



    months_with_data = set(current_year_dict.keys()).union(set(previous_year_dict.keys()))


    print('months with data:' , months_with_data)

    comparison_data = []
    for month in months_with_data:
        current_total = current_year_dict.get(month,0)
        previous_total = previous_year_dict.get(month,0)
        difference = current_total - previous_total
        pourcentage_diff = ((difference/previous_total)*100) if previous_total != 0 else 100

        month_name = calendar.month_name[int(month)]

        comparison_data.append({
            'month':month_name,
            'current_total':current_total,
            'previous_total':previous_total,
            'difference':difference,
            'pourcentage_diff':pourcentage_diff,
        })

    return comparison_data

#taux_inscriptions_par_mois
def taux_inscriptions_par_mois():

    inscriptions_par_mois = (Inscription.objects
                             .annotate(month=TruncMonth('date_inscription'))
                             .values('month')
                             .annotate(total=Count('id'))
                             .order_by('month'))

    data_par_annee = {}

    for entry in inscriptions_par_mois:
        year = entry['month'].year
        month = entry['month'].month  
        total = entry['total']

        if year not in data_par_annee:
            data_par_annee[year] = [0] * 12
        
        data_par_annee[year][month - 1] = total  
    return data_par_annee

#taux_participation_mensuel
def taux_participation_mensuel():
    current_year = timezone.now().year

    inscriptions_mensuelles = (Inscription.objects
                               .filter(date_inscription__year=current_year)
                               .annotate(month=TruncMonth('date_inscription'))
                               .values('month')
                               .annotate(
                                   total_inscriptions=Count('id'),
                                   participants=Count(Case(When(participated=True, then=1), output_field=FloatField()))
                               )
                               .order_by('month'))

    taux_mensuels = []
    for entry in inscriptions_mensuelles:
        taux = (entry['participants'] / entry['total_inscriptions'] * 100) if entry['total_inscriptions'] != 0 else 0
        taux_mensuels.append({
            'month': entry['month'],
            'taux': taux,
            'total': entry['total_inscriptions'],
            'participants': entry['participants']
        })

    return taux_mensuels

#taux de participaion annuel
def taux_participation_annuel():
    current_year = timezone.now().year

    inscriptions_annuelles = (Inscription.objects
                              .filter(date_inscription__year__lte=current_year)
                              .annotate(year=TruncYear('date_inscription'))
                              .values('year')
                              .annotate(
                                  total_inscriptions=Count('id'),
                                  participants=Count(Case(When(participated=True, then=1), output_field=FloatField()))
                              )
                              .order_by('year'))
    
    taux_annuels = []
    for entry in inscriptions_annuelles:
        taux = (entry['participants'] / entry['total_inscriptions'] * 100) if entry['total_inscriptions'] != 0 else 0
        taux_annuels.append({
            'year': entry['year'],
            'taux': taux,
            'total': entry['total_inscriptions'],
            'participants': entry['participants']
        })

    return taux_annuels



#Informations rapport mensuel
def total_registrations_month():
    current_year = timezone.now().year
    current_month = timezone.now().month
    
    total_registrations = (Inscription.objects
                           .filter(date_inscription__year=current_year, date_inscription__month=current_month)
                           .count())
    
    return total_registrations


def compare_with_previous_month():
    today = timezone.now()
    current_year = today.year
    current_month = today.month

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    current_month_registrations = (Inscription.objects
                                   .filter(date_inscription__year=current_year, date_inscription__month=current_month)
                                   .count())

    previous_month_registrations = (Inscription.objects
                                    .filter(date_inscription__year=previous_year, date_inscription__month=previous_month)
                                    .count())

    if previous_month_registrations > 0:
        percentage_change = ((current_month_registrations - previous_month_registrations) / previous_month_registrations) * 100
    else:
        percentage_change = 100  

    return {
        'current_month_registrations': current_month_registrations,
        'previous_month_registrations': previous_month_registrations,
        'percentage_change': percentage_change
    }

def top_3_events():
    current_year = timezone.now().year
    current_month = timezone.now().month
    
    top_events = (Inscription.objects
                  .filter(date_inscription__year=current_year, date_inscription__month=current_month)
                  .values('evenement_id', 'evenement__nom')
                  .annotate(total_inscriptions=Count('id'))
                  .order_by('-total_inscriptions')[:3])

    return top_events



def event_registration_details():
    current_month = timezone.now().month
    current_year = timezone.now().year
    return (Evenement.objects.filter(inscription__date_inscription__year=current_year, inscription__date_inscription__month=current_month)
            .annotate(
                total_inscriptions=Count('inscription'),
                total_participants=Count(Case(When(inscription__participated=True, then=1), output_field=FloatField())),
                taux_participation=Case(
                    When(total_inscriptions=0, then=0),
                    default=100.0 * Count(Case(When(inscription__participated=True, then=1), output_field=FloatField())) / Count('inscription'),
                    output_field=FloatField()
                ),
                total_payments=Count(Case(When(inscription__statut_paiement="paye", then=1), output_field=FloatField()))
            )
            .order_by('-total_inscriptions'))


def top_participants_month():
    current_month = timezone.now().month
    current_year = timezone.now().year

    return (Inscription.objects.filter(date_inscription__year=current_year, date_inscription__month=current_month)
            .values('Utilisateur__id', 'Utilisateur__email')
            .annotate(
                total_events=Count('evenement', distinct=True), 
                total_participations=Sum(Case(
                    When(participated=True, then=1),
                    default=0,
                )))
            .order_by('-total_events')[:3])  


#Informations rapport annuel 
def total_registrations_year():
    current_year = timezone.now().year
    
    total_registrations = (Inscription.objects
                           .filter(date_inscription__year=current_year)
                           .count())
    
    return total_registrations


def compare_with_previous_year():
    today = timezone.now()
    current_year = today.year
    previous_year = current_year - 1


    current_year_registrations = (Inscription.objects
                                   .filter(date_inscription__year=current_year)
                                   .count())

    previous_year_registrations = (Inscription.objects
                                    .filter(date_inscription__year=previous_year)
                                    .count())

    if previous_year_registrations > 0:
        percentage_change = ((current_year_registrations - previous_year_registrations) / previous_year_registrations) * 100
    else:
        percentage_change = 100  

    return {
        'current_year_registrations': current_year_registrations,
        'previous_year_registrations': previous_year_registrations,
        'percentage_change': percentage_change
    }

def top_3_events_year():
    current_year = timezone.now().year
    
    top_events = (Inscription.objects
                  .filter(date_inscription__year=current_year)
                  .values('evenement_id', 'evenement__nom')
                  .annotate(total_inscriptions=Count('id'))
                  .order_by('-total_inscriptions')[:3])

    return top_events

def event_registration_details_year():
    current_year = timezone.now().year
    return (Evenement.objects.filter(inscription__date_inscription__year=current_year)
            .annotate(
                total_inscriptions=Count('inscription'),
                total_participants=Count(Case(When(inscription__participated=True, then=1), output_field=FloatField())),
                taux_participation=Case(
                    When(total_inscriptions=0, then=0),
                    default=100.0 * Count(Case(When(inscription__participated=True, then=1), output_field=FloatField())) / Count('inscription'),
                    output_field=FloatField()
                ),
                total_payments=Count(Case(When(inscription__statut_paiement="paye", then=1), output_field=FloatField()))
            )
            .order_by('-total_inscriptions'))   


def top_participants_year():
    current_year = timezone.now().year

    return (Inscription.objects.filter(date_inscription__year=current_year)
            .values('Utilisateur__id', 'Utilisateur__email')
            .annotate(
                total_events=Count('evenement', distinct=True), 
                total_participations=Sum(Case(
                    When(participated=True, then=1),
                    default=0,
                )))
            .order_by('-total_events')[:3])  