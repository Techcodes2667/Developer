from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from education.models import EducationCategory, EducationContent, Recipe, ExerciseRoutine
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate database with education content'

    def handle(self, *args, **options):
        self.stdout.write('Creating education categories...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Diabetes Basics',
                'description': 'Fundamental information about diabetes types, symptoms, and management',
                'icon': 'fas fa-info-circle',
                'order': 1
            },
            {
                'name': 'Blood Sugar Management',
                'description': 'Learn how to monitor and control your blood glucose levels',
                'icon': 'fas fa-tint',
                'order': 2
            },
            {
                'name': 'Nutrition & Diet',
                'description': 'Healthy eating strategies and meal planning for diabetes',
                'icon': 'fas fa-apple-alt',
                'order': 3
            },
            {
                'name': 'Exercise & Fitness',
                'description': 'Safe and effective exercise routines for people with diabetes',
                'icon': 'fas fa-dumbbell',
                'order': 4
            },
            {
                'name': 'Medication Management',
                'description': 'Understanding diabetes medications and proper usage',
                'icon': 'fas fa-pills',
                'order': 5
            },
            {
                'name': 'Complications Prevention',
                'description': 'Preventing and managing diabetes-related complications',
                'icon': 'fas fa-shield-alt',
                'order': 6
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = EducationCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Get or create admin user for content authoring
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@diabetescare.co.ke', 'is_staff': True, 'is_superuser': True}
        )
        
        self.stdout.write('Creating education content...')
        
        # Create education content
        content_data = [
            {
                'title': 'Understanding Type 1 Diabetes',
                'category': 'Diabetes Basics',
                'content_type': 'article',
                'difficulty_level': 'beginner',
                'summary': 'Learn about Type 1 diabetes, its causes, symptoms, and how it differs from Type 2 diabetes.',
                'content': '''Type 1 diabetes is an autoimmune condition where the body's immune system attacks and destroys the insulin-producing beta cells in the pancreas. This results in little to no insulin production, requiring people with Type 1 diabetes to take insulin injections or use an insulin pump to survive.

**Key Characteristics:**
- Usually diagnosed in children, teenagers, or young adults
- Accounts for about 5-10% of all diabetes cases
- Requires lifelong insulin therapy
- Cannot be prevented or cured currently

**Symptoms:**
- Increased thirst and frequent urination
- Extreme hunger
- Unexplained weight loss
- Fatigue and weakness
- Blurred vision
- Irritability and mood changes

**Management:**
Type 1 diabetes management involves:
1. Insulin therapy (multiple daily injections or insulin pump)
2. Blood glucose monitoring
3. Carbohydrate counting
4. Regular physical activity
5. Regular medical check-ups''',
                'estimated_read_time': 5,
                'is_featured': True,
                'tags': 'type1, diabetes, insulin, autoimmune'
            },
            {
                'title': 'Blood Glucose Monitoring: When and How',
                'category': 'Blood Sugar Management',
                'content_type': 'article',
                'difficulty_level': 'beginner',
                'summary': 'Master the art of blood glucose monitoring with proper timing and technique.',
                'content': '''Regular blood glucose monitoring is crucial for effective diabetes management. It helps you understand how food, exercise, stress, and medications affect your blood sugar levels.

**When to Test:**
- Before meals (fasting)
- 2 hours after meals (postprandial)
- Before bedtime
- Before and after exercise
- When feeling unwell
- Before driving (if on insulin)

**Target Ranges (for most adults):**
- Before meals: 4.0-7.0 mmol/L (72-126 mg/dL)
- 2 hours after meals: Less than 10.0 mmol/L (180 mg/dL)
- Bedtime: 5.0-8.3 mmol/L (90-150 mg/dL)

**Proper Testing Technique:**
1. Wash hands with soap and warm water
2. Insert test strip into meter
3. Use lancet to prick side of fingertip
4. Apply blood drop to test strip
5. Record result with date and time
6. Note any relevant factors (meals, exercise, stress)

**Tips for Success:**
- Rotate finger prick sites
- Use fresh lancets
- Keep meter and strips at room temperature
- Check meter accuracy regularly''',
                'estimated_read_time': 7,
                'is_featured': True,
                'tags': 'monitoring, blood glucose, testing, meter'
            },
            {
                'title': 'Carbohydrate Counting for Diabetes',
                'category': 'Nutrition & Diet',
                'content_type': 'article',
                'difficulty_level': 'intermediate',
                'summary': 'Learn how to count carbohydrates to better manage your blood sugar levels.',
                'content': '''Carbohydrate counting is a meal planning technique that helps people with diabetes manage their blood glucose levels by tracking the amount of carbohydrates consumed.

**Why Count Carbs?**
Carbohydrates have the most significant impact on blood glucose levels. By counting carbs, you can:
- Better predict blood sugar responses
- Adjust insulin doses more accurately
- Maintain more stable glucose levels
- Have more flexibility in food choices

**What Counts as a Carb?**
- Grains (rice, bread, pasta, cereals)
- Fruits and fruit juices
- Milk and yogurt
- Starchy vegetables (potatoes, corn, peas)
- Sweets and desserts
- Legumes (beans, lentils)

**How to Count:**
1. Read nutrition labels for total carbohydrates
2. Use measuring cups and food scales
3. Learn standard portion sizes
4. Use carb counting apps or books
5. Keep a food diary

**Practical Tips:**
- One carb serving = 15 grams of carbohydrates
- Focus on total carbs, not just sugar
- Include fiber-rich carbs for better blood sugar control
- Spread carbs evenly throughout the day
- Work with a dietitian to develop your plan''',
                'estimated_read_time': 8,
                'is_featured': False,
                'tags': 'carbohydrates, nutrition, meal planning, insulin'
            },
            {
                'title': 'Safe Exercise Guidelines for Diabetes',
                'category': 'Exercise & Fitness',
                'content_type': 'article',
                'difficulty_level': 'beginner',
                'summary': 'Discover how to exercise safely and effectively when you have diabetes.',
                'content': '''Regular physical activity is one of the most important things you can do to manage diabetes. Exercise helps lower blood glucose, improves insulin sensitivity, and provides numerous health benefits.

**Benefits of Exercise:**
- Lowers blood glucose levels
- Improves insulin sensitivity
- Helps with weight management
- Reduces cardiovascular risk
- Improves mood and energy
- Strengthens bones and muscles

**Types of Exercise:**
1. **Aerobic Exercise:** Walking, swimming, cycling, dancing
2. **Resistance Training:** Weight lifting, resistance bands, bodyweight exercises
3. **Flexibility:** Stretching, yoga, tai chi

**Safety Guidelines:**
- Check blood glucose before, during, and after exercise
- Carry fast-acting carbs for hypoglycemia
- Stay hydrated
- Wear proper footwear
- Start slowly and gradually increase intensity
- Exercise with a buddy when possible

**Blood Sugar Considerations:**
- If glucose is below 5.6 mmol/L (100 mg/dL), eat a snack before exercising
- If above 13.9 mmol/L (250 mg/dL), check for ketones and avoid exercise if present
- Monitor for delayed hypoglycemia up to 24 hours post-exercise

**Getting Started:**
- Aim for 150 minutes of moderate aerobic activity per week
- Include 2-3 resistance training sessions
- Start with 10-15 minute sessions if you're new to exercise
- Consult your healthcare team before starting a new program''',
                'estimated_read_time': 6,
                'is_featured': True,
                'tags': 'exercise, fitness, safety, blood sugar, physical activity'
            }
        ]
        
        content_count = 0
        for content_info in content_data:
            category = categories[content_info['category']]
            
            content, created = EducationContent.objects.get_or_create(
                title=content_info['title'],
                defaults={
                    'slug': slugify(content_info['title']),
                    'category': category,
                    'content_type': content_info['content_type'],
                    'difficulty_level': content_info['difficulty_level'],
                    'summary': content_info['summary'],
                    'content': content_info['content'],
                    'estimated_read_time': content_info['estimated_read_time'],
                    'is_featured': content_info['is_featured'],
                    'is_published': True,
                    'tags': content_info['tags'],
                    'author': admin_user
                }
            )
            
            if created:
                content_count += 1
                self.stdout.write(f'Created content: {content.title}')
        
        self.stdout.write('Creating sample recipes...')
        
        # Create sample recipes
        recipes_data = [
            {
                'title': 'Diabetes-Friendly Vegetable Stir Fry',
                'meal_type': 'lunch',
                'difficulty_level': 'easy',
                'servings': 4,
                'prep_time_minutes': 15,
                'cook_time_minutes': 10,
                'ingredients': '''2 cups mixed vegetables (broccoli, bell peppers, carrots)
1 cup brown rice (cooked)
2 tbsp olive oil
2 cloves garlic, minced
1 tbsp low-sodium soy sauce
1 tsp ginger, grated
1/4 cup chopped green onions
Salt and pepper to taste''',
                'instructions': '''1. Heat olive oil in a large pan or wok over medium-high heat.
2. Add garlic and ginger, stir-fry for 30 seconds.
3. Add mixed vegetables and stir-fry for 5-7 minutes until tender-crisp.
4. Add cooked brown rice and soy sauce.
5. Stir everything together for 2-3 minutes.
6. Garnish with green onions and serve hot.''',
                'description': 'High in fiber and low in simple carbs. The brown rice provides complex carbohydrates for steady blood sugar.',
                'calories_per_serving': 180,
                'carbs_per_serving': 28.0,
                'protein_per_serving': 5.0,
                'fat_per_serving': 7.0,
                'fiber_per_serving': 4.0
            },
            {
                'title': 'Grilled Chicken with Herbs',
                'meal_type': 'dinner',
                'difficulty_level': 'easy',
                'servings': 4,
                'prep_time_minutes': 10,
                'cook_time_minutes': 20,
                'ingredients': '''4 chicken breasts (boneless, skinless)
2 tbsp olive oil
2 tsp dried herbs (rosemary, thyme, oregano)
1 lemon (juiced)
2 cloves garlic, minced
Salt and pepper to taste
Mixed green salad for serving''',
                'instructions': '''1. Preheat grill to medium-high heat.
2. Mix olive oil, herbs, lemon juice, and garlic in a bowl.
3. Season chicken with salt and pepper, then coat with herb mixture.
4. Grill chicken for 6-8 minutes per side until internal temperature reaches 165°F.
5. Let rest for 5 minutes before slicing.
6. Serve with mixed green salad.''',
                'description': 'Excellent lean protein source with minimal carbohydrates. Perfect for blood sugar control.',
                'calories_per_serving': 220,
                'carbs_per_serving': 2.0,
                'protein_per_serving': 35.0,
                'fat_per_serving': 8.0,
                'fiber_per_serving': 0.0
            }
        ]
        
        recipe_count = 0
        for recipe_info in recipes_data:
            recipe, created = Recipe.objects.get_or_create(
                title=recipe_info['title'],
                defaults={
                    'slug': slugify(recipe_info['title']),
                    'meal_type': recipe_info['meal_type'],
                    'difficulty_level': recipe_info['difficulty_level'],
                    'servings': recipe_info['servings'],
                    'prep_time_minutes': recipe_info['prep_time_minutes'],
                    'cook_time_minutes': recipe_info['cook_time_minutes'],
                    'ingredients': recipe_info['ingredients'],
                    'instructions': recipe_info['instructions'],
                    'description': recipe_info['description'],
                    'calories_per_serving': recipe_info['calories_per_serving'],
                    'carbs_per_serving': recipe_info['carbs_per_serving'],
                    'protein_per_serving': recipe_info['protein_per_serving'],
                    'fat_per_serving': recipe_info['fat_per_serving'],
                    'fiber_per_serving': recipe_info['fiber_per_serving'],
                    'is_published': True,
                    'author': admin_user
                }
            )
            
            if created:
                recipe_count += 1
                self.stdout.write(f'Created recipe: {recipe.title}')
        
        self.stdout.write('Creating sample exercise routines...')
        
        # Create sample exercise routines
        exercises_data = [
            {
                'title': 'Beginner Walking Program',
                'intensity_level': 'low',
                'duration_minutes': 30,
                'suitable_for_beginners': True,
                'requires_supervision': False,
                'description': 'A gentle walking program perfect for those starting their fitness journey with diabetes.',
                'instructions': '''**Week 1-2: Building the Habit**
- Walk for 10 minutes at a comfortable pace
- Do this 3 times per week
- Focus on consistency rather than speed

**Week 3-4: Increasing Duration**
- Extend walks to 15 minutes
- Continue 3 times per week
- Add gentle arm swings while walking

**Week 5-6: Building Endurance**
- Walk for 20 minutes
- Increase to 4 times per week
- Include some gentle hills if available

**Week 7-8: Reaching the Goal**
- Walk for 30 minutes
- Maintain 4-5 times per week
- Vary your routes to stay motivated

**Safety Tips:**
- Always check blood glucose before walking
- Carry glucose tablets or snacks
- Wear comfortable, supportive shoes
- Stay hydrated
- Walk with a friend when possible''',
                'equipment_needed': 'Comfortable walking shoes, water bottle, glucose meter',
                'contraindications': 'Avoid if experiencing severe hypoglycemia or diabetic ketoacidosis. Stop if you feel dizzy or unwell.'
            }
        ]
        
        exercise_count = 0
        for exercise_info in exercises_data:
            exercise, created = ExerciseRoutine.objects.get_or_create(
                title=exercise_info['title'],
                defaults={
                    'slug': slugify(exercise_info['title']),
                    'intensity_level': exercise_info['intensity_level'],
                    'duration_minutes': exercise_info['duration_minutes'],
                    'suitable_for_beginners': exercise_info['suitable_for_beginners'],
                    'requires_supervision': exercise_info['requires_supervision'],
                    'description': exercise_info['description'],
                    'instructions': exercise_info['instructions'],
                    'equipment_needed': exercise_info['equipment_needed'],
                    'contraindications': exercise_info['contraindications'],
                    'is_published': True,
                    'author': admin_user
                }
            )
            
            if created:
                exercise_count += 1
                self.stdout.write(f'Created exercise: {exercise.title}')
        
        self.stdout.write(f'Created {len(categories_data)} categories, {content_count} articles, {recipe_count} recipes, and {exercise_count} exercises')
        self.stdout.write(self.style.SUCCESS('Successfully populated education database'))
