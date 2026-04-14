"""Advanced Plan Generator LLM Agent - Generate challenge-focused learning plans"""

from typing import Dict, Any, Optional
from agents.base_llm_agent import BaseLLMAgent
from utils import GeminiClient


# TODO: IMPLEMENTATION REQUIRED
# Implement AdvancedPlanGeneratorLLMAgent class inheriting BaseLLMAgent with __init__(client) calling super().__init__(client).

# TODO: IMPLEMENTATION REQUIRED
# Implement create_advanced_plan(analyzed_profile) building LLM prompt with profile and advanced requirements (0.7x timeline, premium resources, high intensity).
# Call generate_response() temp=0.3, max_tokens=2000. Extract JSON validating plan fields. Returns: Dict with advanced plan.
class AdvancedPlanGeneratorLLMAgent(BaseLLMAgent):
  
    def __init__(self, client: Optional[GeminiClient] = None):
        super().__init__(client)
    
    def create_advanced_plan(self, analyzed_profile: Dict[str, Any]) -> Dict[str, Any]:

        goals = analyzed_profile.get('goals', {})
        constraints = analyzed_profile.get('constraints', {})
        identified_gaps = analyzed_profile.get('identified_gaps', [])
        current_proficiency = analyzed_profile.get('current_proficiency', {})
        
        # Get specific learner information
        domain = current_proficiency.get('domain', 'Technology')
        topic = analyzed_profile.get('learning_characteristics', {}).get('topic', 'General Skills')
        career_aspiration = goals.get('career_aspiration', 'Professional')
        primary_goal = goals.get('primary_goal', 'Specialize and innovate')
        
        # Calculate compressed timeline for advanced learners
        base_timeline = goals.get('target_timeline_months', 6)
        advanced_timeline = max(1, base_timeline * 0.7)
        
        prompt = f"""You are an expert curriculum designer specializing in advanced, specialized programs. Create an advanced, challenge-focused learning plan.

SPECIFIC LEARNER INFORMATION:
- Learning Topic: {topic}
- Domain: {domain}
- Career Goal: Become a leading {career_aspiration}
- Primary Goal: {primary_goal}
- Current Level: Advanced/Expert
- Identified Gaps: {', '.join(identified_gaps) if identified_gaps else 'Advanced Concepts, System Design'}
- Budget: ${constraints.get('budget_limit_usd', 1000)}
- Target Timeline: {advanced_timeline:.0f} months (accelerated for advanced learners)
- Available Hours/Week: {analyzed_profile.get('learning_characteristics', {}).get('hours_available_per_week', 15)}
- Learning Style: {analyzed_profile.get('learning_characteristics', {}).get('learning_style', 'mixed')}

IMPORTANT: Generate content SPECIFICALLY for advanced practitioners in {domain} pursuing {topic}. NOT generic templates.
- Topics must be expert-level, specialized concepts in {topic} and {domain}
- Resources must include: premium courses, research papers, expert resources (eg: "MIT Advanced Algorithms course", "ACM Research Papers", "Specialized certifications")
- Milestones must involve research, innovation, and expert-level projects
- Do NOT use placeholders like [Topic 1] or [Resource 1]

Create an ADVANCED plan emphasizing:
1. Advanced and specialized concepts in {topic}
2. Premium, research-oriented, and specialized resources for {domain}
3. Accelerated pace (0.7x normal duration) for skilled learners
4. Research, innovation, and mastery focus

Provide response as ONLY valid JSON with these exact fields and NO other text:
{{
  "plan_type": "Advanced Specialization Plan for {topic}",
  "duration_weeks": {int(advanced_timeline * 4)},
  "hours_per_week": 15,
  "intensity": "High",
  "topics": [expert topic 1 for {topic}, expert topic 2, advanced specialization 1, advanced specialization 2, research topic],
  "resources": [premium resource 1 for {domain}, research paper collection, expert mentorship resource, specialized certification],
  "milestones": [research project 1, expert-level implementation, specialization achievement, innovation project],
  "focus_areas": ["Advanced {topic} concepts", "System Design in {domain}", "Innovation and research", "Expert specialization"]
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
                        plan[field] = 'Advanced Specialization Plan'
                    elif field == 'duration_weeks':
                        plan[field] = int(advanced_timeline * 4)
                    elif field == 'hours_per_week':
                        plan[field] = 15
                    elif field == 'intensity':
                        plan[field] = 'High'
                    elif field in ['topics', 'resources', 'milestones']:
                        plan[field] = []
            
            return plan
        except Exception as e:
            print(f"Warning: Error parsing plan: {e}")
            # Return default advanced plan
            return {
                'plan_type': 'Advanced Specialization Plan',
                'duration_weeks': int(advanced_timeline * 4),
                'hours_per_week': 15,
                'intensity': 'High',
                'topics': ['Advanced Theory', 'System Design', 'Specialized Concepts', 'Research Methods'],
                'resources': ['Premium platforms', 'Research papers', 'Expert guidance', 'Cutting-edge tools'],
                'milestones': ['Advanced project completion', 'Research paper', 'Specialization certification'],
                'focus_areas': ['Advanced Concepts', 'System Design', 'innovation', 'Specialization']
            }
