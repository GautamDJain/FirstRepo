"""Beginner Plan Generator LLM Agent - Generate foundation-focused learning plans"""

from typing import Dict, Any, Optional
from agents.base_llm_agent import BaseLLMAgent
from utils import GeminiClient


# TODO: IMPLEMENTATION REQUIRED
# Implement BeginnerPlanGeneratorLLMAgent class inheriting BaseLLMAgent with __init__(client) calling super().__init__(client).

# TODO: IMPLEMENTATION REQUIRED
# Implement create_beginner_plan(analyzed_profile) building LLM prompt with profile and beginner requirements (1.5x timeline, free resources, foundation focus).
# Call generate_response() temp=0.3, max_tokens=2000. Extract JSON validating plan_type, duration_weeks, hours_per_week, intensity, topics, resources, milestones. Returns: Dict with beginner plan.
class BeginnerPlanGeneratorLLMAgent(BaseLLMAgent):

    
    def __init__(self, client: Optional[GeminiClient] = None):
        super().__init__(client)
    
    def create_beginner_plan(self, analyzed_profile: Dict[str, Any]) -> Dict[str, Any]:

        goals = analyzed_profile.get('goals', {})
        constraints = analyzed_profile.get('constraints', {})
        identified_gaps = analyzed_profile.get('identified_gaps', [])
        current_proficiency = analyzed_profile.get('current_proficiency', {})
        
        # Get specific learner information
        domain = current_proficiency.get('domain', 'Technology')
        topic = analyzed_profile.get('learning_characteristics', {}).get('topic', 'General Skills')
        career_aspiration = goals.get('career_aspiration', 'Professional')
        primary_goal = goals.get('primary_goal', 'Learn fundamentals')
        
        # Calculate extended timeline for beginners
        base_timeline = goals.get('target_timeline_months', 6)
        beginner_timeline = base_timeline * 1.5
        
        prompt = f"""You are an expert curriculum designer specializing in personalized learning paths. Create a beginner-focused learning plan.

SPECIFIC LEARNER INFORMATION:
- Learning Topic: {topic}
- Domain: {domain}
- Career Goal: Become a {career_aspiration}
- Primary Goal: {primary_goal}
- Current Level: Beginner
- Identified Gaps: {', '.join(identified_gaps) if identified_gaps else 'Foundation, Basic Concepts'}
- Budget: ${constraints.get('budget_limit_usd', 100)}
- Target Timeline: {beginner_timeline:.0f} months (extended for beginners)
- Available Hours/Week: {analyzed_profile.get('learning_characteristics', {}).get('hours_available_per_week', 5)}
- Learning Style: {analyzed_profile.get('learning_characteristics', {}).get('learning_style', 'mixed')}

IMPORTANT: Generate content SPECIFICALLY for {domain} and {topic}. NOT generic templates.
- Topics must be real, specific concepts related to {topic} in {domain}
- Resources must be actual, named courses, tutorials, books (eg: "Python for Everybody course on freeCodeCamp", "MIT OpenCourseWare 6.0001")
- Milestones must be concrete, measurable achievements
- Do NOT use placeholders like [Topic 1] or [Resource 1]

Create a BEGINNER plan emphasizing:
1. Foundation and fundamentals of {topic}
2. Free or low-cost resources for {domain}
3. Slower pace (1.5x normal duration)
4. Regular breaks and review cycles

Provide response as ONLY valid JSON with these exact fields and NO other text:
{{
  "plan_type": "Beginner Foundation Plan for {topic}",
  "duration_weeks": {int(beginner_timeline * 4)},
  "hours_per_week": 5,
  "intensity": "Low",
  "topics": [specific topic 1 for {topic}, specific topic 2, specific topic 3, specific topic 4, specific topic 5],
  "resources": [specific resource 1 for {domain}, specific resource 2, specific resource 3, specific resource 4],
  "milestones": [concrete milestone 1, concrete milestone 2, concrete milestone 3, concrete milestone 4],
  "focus_areas": ["Foundation of {topic}", "Core Concepts of {domain}", "Building learning habits", "Hands-on practice"]
}}"""

        response = self.generate_response(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        try:
            plan = self.extract_json(response)
            
            # Validate required fields
            required_fields = ['plan_type', 'duration_weeks', 'hours_per_week', 'intensity', 'topics', 'resources', 'milestones']
            for field in required_fields:
                if field not in plan:
                    # Use defaults if missing
                    if field == 'plan_type':
                        plan[field] = 'Beginner Foundation Plan'
                    elif field == 'duration_weeks':
                        plan[field] = int(beginner_timeline * 4)
                    elif field == 'hours_per_week':
                        plan[field] = 5
                    elif field == 'intensity':
                        plan[field] = 'Low'
                    elif field in ['topics', 'resources', 'milestones']:
                        plan[field] = []
            
            return plan
        except Exception as e:
            print(f"Warning: Error parsing plan: {e}")
            # Return default beginner plan
            return {
                'plan_type': 'Beginner Foundation Plan',
                'duration_weeks': int(beginner_timeline * 4),
                'hours_per_week': 5,
                'intensity': 'Low',
                'topics': ['Fundamentals', 'Core Concepts', 'Practical Basics'],
                'resources': ['Free online tutorials', 'Documentation', 'Community forums'],
                'milestones': ['Complete foundational module', 'First practical project'],
                'focus_areas': ['Foundation', 'Core Concepts']
            }
