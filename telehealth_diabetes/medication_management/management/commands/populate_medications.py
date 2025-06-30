from django.core.management.base import BaseCommand
from medication_management.models import Medication, DrugInteraction

class Command(BaseCommand):
    help = 'Populate database with common diabetes medications and interactions'

    def handle(self, *args, **options):
        self.stdout.write('Creating common diabetes medications...')
        
        medications_data = [
            # Insulin
            {
                'name': 'Insulin Glargine (Lantus)',
                'generic_name': 'Insulin Glargine',
                'medication_type': 'insulin',
                'description': 'Long-acting insulin for basal coverage',
                'common_side_effects': 'Hypoglycemia, injection site reactions, weight gain',
                'warnings': 'Monitor blood glucose levels regularly. Do not mix with other insulins.'
            },
            {
                'name': 'Insulin Lispro (Humalog)',
                'generic_name': 'Insulin Lispro',
                'medication_type': 'insulin',
                'description': 'Rapid-acting insulin for mealtime coverage',
                'common_side_effects': 'Hypoglycemia, injection site reactions',
                'warnings': 'Take 15 minutes before meals. Monitor for hypoglycemia.'
            },
            {
                'name': 'Insulin NPH (Humulin N)',
                'generic_name': 'NPH Insulin',
                'medication_type': 'insulin',
                'description': 'Intermediate-acting insulin',
                'common_side_effects': 'Hypoglycemia, injection site reactions, weight gain',
                'warnings': 'Shake gently before use. Monitor blood glucose levels.'
            },
            
            # Metformin
            {
                'name': 'Metformin',
                'generic_name': 'Metformin Hydrochloride',
                'medication_type': 'metformin',
                'description': 'First-line treatment for Type 2 diabetes',
                'common_side_effects': 'Nausea, diarrhea, stomach upset, metallic taste',
                'warnings': 'Take with food. Stop before contrast procedures. Monitor kidney function.'
            },
            {
                'name': 'Metformin XR',
                'generic_name': 'Metformin Extended Release',
                'medication_type': 'metformin',
                'description': 'Extended-release formulation of metformin',
                'common_side_effects': 'Nausea, diarrhea, stomach upset',
                'warnings': 'Take with evening meal. Do not crush or chew tablets.'
            },
            
            # Sulfonylureas
            {
                'name': 'Glipizide',
                'generic_name': 'Glipizide',
                'medication_type': 'sulfonylurea',
                'description': 'Stimulates insulin production from pancreas',
                'common_side_effects': 'Hypoglycemia, weight gain, nausea',
                'warnings': 'Take 30 minutes before meals. Monitor for hypoglycemia.'
            },
            {
                'name': 'Glyburide',
                'generic_name': 'Glyburide',
                'medication_type': 'sulfonylurea',
                'description': 'Stimulates insulin production from pancreas',
                'common_side_effects': 'Hypoglycemia, weight gain, skin reactions',
                'warnings': 'Take with breakfast. Higher risk of hypoglycemia than other sulfonylureas.'
            },
            
            # DPP-4 Inhibitors
            {
                'name': 'Sitagliptin (Januvia)',
                'generic_name': 'Sitagliptin',
                'medication_type': 'dpp4',
                'description': 'Helps regulate blood sugar by increasing insulin when needed',
                'common_side_effects': 'Upper respiratory infection, headache, sore throat',
                'warnings': 'Adjust dose for kidney problems. Monitor for pancreatitis.'
            },
            {
                'name': 'Linagliptin (Tradjenta)',
                'generic_name': 'Linagliptin',
                'medication_type': 'dpp4',
                'description': 'DPP-4 inhibitor for Type 2 diabetes',
                'common_side_effects': 'Nasopharyngitis, hypoglycemia when combined with insulin',
                'warnings': 'No dose adjustment needed for kidney or liver problems.'
            },
            
            # SGLT-2 Inhibitors
            {
                'name': 'Empagliflozin (Jardiance)',
                'generic_name': 'Empagliflozin',
                'medication_type': 'sglt2',
                'description': 'Helps kidneys remove glucose through urine',
                'common_side_effects': 'Urinary tract infections, genital infections, increased urination',
                'warnings': 'Monitor for ketoacidosis. Increase fluid intake. Check for genital infections.'
            },
            
            # GLP-1 Agonists
            {
                'name': 'Liraglutide (Victoza)',
                'generic_name': 'Liraglutide',
                'medication_type': 'glp1',
                'description': 'Injectable medication that helps control blood sugar',
                'common_side_effects': 'Nausea, vomiting, diarrhea, injection site reactions',
                'warnings': 'Start with low dose. Monitor for pancreatitis and thyroid tumors.'
            },
        ]
        
        created_count = 0
        for med_data in medications_data:
            medication, created = Medication.objects.get_or_create(
                name=med_data['name'],
                defaults=med_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {medication.name}')
        
        self.stdout.write(f'Created {created_count} new medications')
        
        # Create some common drug interactions
        self.stdout.write('Creating drug interactions...')
        
        interactions_data = [
            {
                'med1_name': 'Metformin',
                'med2_name': 'Insulin Glargine (Lantus)',
                'severity': 'minor',
                'description': 'May increase risk of hypoglycemia when used together',
                'recommendation': 'Monitor blood glucose levels more frequently when starting combination therapy'
            },
            {
                'med1_name': 'Glipizide',
                'med2_name': 'Insulin Lispro (Humalog)',
                'severity': 'moderate',
                'description': 'Increased risk of severe hypoglycemia',
                'recommendation': 'Consider reducing doses and monitor blood glucose closely'
            },
            {
                'med1_name': 'Sitagliptin (Januvia)',
                'med2_name': 'Metformin',
                'severity': 'minor',
                'description': 'Generally safe combination, commonly prescribed together',
                'recommendation': 'Standard monitoring for both medications'
            },
        ]
        
        interaction_count = 0
        for interaction_data in interactions_data:
            try:
                med1 = Medication.objects.get(name=interaction_data['med1_name'])
                med2 = Medication.objects.get(name=interaction_data['med2_name'])
                
                interaction, created = DrugInteraction.objects.get_or_create(
                    medication1=med1,
                    medication2=med2,
                    defaults={
                        'severity': interaction_data['severity'],
                        'description': interaction_data['description'],
                        'recommendation': interaction_data['recommendation']
                    }
                )
                if created:
                    interaction_count += 1
                    self.stdout.write(f'Created interaction: {med1.name} + {med2.name}')
            except Medication.DoesNotExist:
                continue
        
        self.stdout.write(f'Created {interaction_count} drug interactions')
        self.stdout.write(self.style.SUCCESS('Successfully populated medications database'))
