"""Standard Plan Generator LLM Agent - Generate balanced learning plans"""

from typing import Dict, Any, Optional
from agents.base_llm_agent import BaseLLMAgent
from utils import GeminiClient


# TODO: IMPLEMENTATION REQUIRED
# Implement StandardPlanGeneratorLLMAgent class inheriting BaseLLMAgent with __init__(client) calling super().__init__(client).

# TODO: IMPLEMENTATION REQUIRED
# Implement create_standard_plan(analyzed_profile) building LLM prompt with profile and standard requirements (1.0x timeline, balanced resources, moderate intensity).
# Call generate_response() temp=0.3, max_tokens=2000. Extract JSON validating plan fields. Returns: Dict with standard plan.
class StandardPlanGeneratorLLMAgent(BaseLLMAgent):
    """Agent for generating standard-level learning plans"""
    
    def __init__(self, client: Optional[GeminiClient] = None):
        """initialize with optional Gemini client"""
        super().__init__(client)
    
    def create_standard_plan(self, analyzed_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standard-balanced learning plan.
        
        Args:
            analyzed_profile: Analyzed learner profile
            
        Returns:
            Dictionary with standard learning plan
        """
        goals = analyzed_profile.get('goals', {})
        constraints = analyzed_profile.get('constraints', {})
        identified_gaps = analyzed_profile.get('identified_gaps', [])
        current_proficiency = analyzed_profile.get('current_proficiency', {})
        
        # Get specific learner information
        domain = current_proficiency.get('domain', 'Technology')
        topic = analyzed_profile.get('learning_characteristics', {}).get('topic', 'General Skills')
        career_aspiration = goals.get('career_aspiration', 'Professional')
        primary_goal = goals.get('primary_goal', 'Advance skills')
        
        timeline = goals.get('target_timeline_months', 6)
        
        prompt = f"""You are an expert curriculum designer specializing in personalized learning paths. Create a standard, balanced learning plan.

SPECIFIC LEARNER INFORMATION:
- Learning Topic: {topic}
- Domain: {domain}
- Career Goal: Become a {career_aspiration}
- Primary Goal: {primary_goal}
- Current Level: Intermediate
- Identified Gaps: {', '.join(identified_gaps) if identified_gaps else 'intermediate Concepts, Practical implementation'}
- Budget: ${constraints.get('budget_limit_usd', 500)}
- Target Timeline: {timeline} months
- Available Hours/Week: {analyzed_profile.get('learning_characteristics', {}).get('hours_available_per_week', 10)}
- Learning Style: {analyzed_profile.get('learning_characteristics', {}).get('learning_style', 'mixed')}

IMPORTANT: Generate content SPECIFICALLY for {domain} and {topic}. NOT generic templates.
- Topics must be real, specific concepts related to {topic} in {domain}
- Resources must be actual, named courses, tutorials, platforms (eg: "Coursera Machine Learning course", "LinkedIn Learning")
- Milestones must be concrete, measurable achievements
- Do NOT use placeholders like [Topic 1] or [Resource 1]

Create a STANDARD plan emphasizing:
1. Balanced mix of theory and practical implementation for {topic}
2. Moderate-quality resources (mix of free and paid) for {domain}
3. Normal pace with regular progression
4. Consistent progress with real-world projects

Provide response as ONLY valid JSON with these exact fields and NO other text:
{{
  "plan_type": "Standard Learning Plan for {topic}",
  "duration_weeks": {int(timeline * 4)},
  "hours_per_week": 10,
  "intensity": "Moderate",
  "topics": [specific topic 1 for {topic}, specific topic 2, specific topic 3, specific topic 4, specific topic 5],
  "resources": [specific resource 1 for {domain}, specific resource 2, specific resource 3, specific resource 4],
  "milestones": [concrete milestone 1, concrete milestone 2, concrete milestone 3, concrete milestone 4],
  "focus_areas": ["Core Concepts of {topic}", "Practical application in {domain}", "Problem solving", "Industry best practices"]
}}"""

        response = self.generate_response(prompt=prompt,temperature=0.3,max_tokens=2000)     
        try:
            plan = self.extract_json(response)
            
            # Validate required fields
            required_fields = ['plan_type', 'duration_weeks', 'hours_per_week', 'intensity', 'topics', 'resources', 'milestones']
            for field in required_fields:
                if field not in plan:
                    # Use defaults if missing
                    if field == 'plan_type':
                        plan[field] = 'Standard Learning Plan'
                    elif field == 'duration_weeks':
                        plan[field] = int(timeline * 4)
                    elif field == 'hours_per_week':
                        plan[field] = 10
                    elif field == 'intensity':
                        plan[field] = 'Moderate'
                    elif field in ['topics', 'resources', 'milestones']:
                        plan[field] = []
            
            return plan
        except Exception as e:
            print(f"Warning: Error parsing plan: {e}")
            # Return default standard plan
            return {
                'plan_type': 'Standard Learning Plan',
                'duration_weeks': int(timeline * 4),
                'hours_per_week': 10,
                'intensity': 'Moderate',
                'topics': ['Core Concepts', 'intermediate Theory', 'Practical Application', 'Advanced Topics'],
                'resources': ['Online courses', 'Documentation', 'Tutorials', 'Practice problems'],
                'milestones': ['Module 1 completion', 'Mid-course project', 'Final capstone'],
                'focus_areas': ['Concepts', 'Practical implementation', 'Problem Solving']
            }
