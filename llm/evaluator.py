import os
import json
import openai
import google.generativeai as genai
from typing import Dict, List, Tuple
from datetime import datetime
from models.interview_models import Answer, Question, Feedback, Candidate

class InterviewEvaluator:
    """LLM-based interview answer evaluator with Google Gemini and OpenAI support"""
    
    def __init__(self):
        # Initialize OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "demo_key_placeholder":
            self.openai_client = openai.OpenAI(api_key=openai_key)
            self.use_openai = True
        else:
            self.openai_client = None
            self.use_openai = False
        
        # Initialize Google Gemini
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            genai.configure(api_key=google_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_gemini = True
        else:
            self.gemini_model = None
            self.use_gemini = False
        
        # Set primary LLM preference
        self.use_llm = self.use_openai or self.use_gemini
        
        if not self.use_llm:
            print("Warning: No LLM API keys configured. Using fallback evaluation.")
        else:
            primary = "OpenAI" if self.use_openai else "Google Gemini"
            print(f"LLM Evaluator initialized with {primary}")
        
    def generate_evaluation_prompt(self, question: Question, answer: Answer, candidate: Candidate) -> str:
        """Generate evaluation prompt for LLM"""
        return f"""
You are a professional interview evaluator. Please evaluate the following interview answer:

CANDIDATE PROFILE:
- Name: {candidate.name}
- Position: {candidate.position}
- Experience Level: {candidate.experience_level}

QUESTION:
Type: {question.question_type}
Difficulty: {question.difficulty_level}/5
Question: {question.question_text}

CANDIDATE'S ANSWER:
{answer.answer_text}

EVALUATION CRITERIA:
Please score the answer on a scale of 1-5 for each criterion:
1. Technical Accuracy (if applicable)
2. Communication Clarity
3. Problem-Solving Approach
4. Depth of Knowledge
5. Relevance to Question

RESPONSE FORMAT:
Please respond with a JSON object containing:
{{
    "overall_score": <1-5 integer>,
    "criteria_scores": {{
        "technical_accuracy": <1-5 integer>,
        "communication": <1-5 integer>,
        "problem_solving": <1-5 integer>,
        "knowledge_depth": <1-5 integer>,
        "relevance": <1-5 integer>
    }},
    "feedback_text": "<detailed constructive feedback>",
    "strengths": ["<strength1>", "<strength2>"],
    "improvements": ["<improvement1>", "<improvement2>"],
    "reasoning": "<brief explanation of the scoring>"
}}

Be constructive, specific, and helpful in your feedback. Consider the candidate's experience level when evaluating.
"""

    async def evaluate_answer(self, question: Question, answer: Answer, candidate: Candidate) -> Feedback:
        """Evaluate an interview answer using LLM"""
        try:
            if not self.use_llm:
                return self._fallback_evaluation(answer, question)
                
            prompt = self.generate_evaluation_prompt(question, answer, candidate)
            
            # Try OpenAI first, then Gemini as fallback
            if self.use_openai:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert interview evaluator with years of experience in technical and behavioral interviews."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=1000
                    )
                    evaluation_text = response.choices[0].message.content
                    
                except Exception as e:
                    print(f"OpenAI evaluation failed: {e}")
                    if self.use_gemini:
                        evaluation_text = await self._evaluate_with_gemini(prompt)
                    else:
                        return self._fallback_evaluation(answer, question)
            
            elif self.use_gemini:
                evaluation_text = await self._evaluate_with_gemini(prompt)
            
            else:
                return self._fallback_evaluation(answer, question)
            
            # Parse evaluation result
            try:
                evaluation_data = json.loads(evaluation_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = evaluation_text.find('{')
                end = evaluation_text.rfind('}') + 1
                if start >= 0 and end > start:
                    evaluation_data = json.loads(evaluation_text[start:end])
                else:
                    return self._fallback_evaluation(answer, question)
            
            # Create Feedback object
            feedback = Feedback(
                answer_id=answer.id,
                session_id=answer.session_id,
                score=evaluation_data["overall_score"],
                feedback_text=evaluation_data["feedback_text"],
                criteria_scores=evaluation_data["criteria_scores"],
                strengths=evaluation_data["strengths"],
                improvements=evaluation_data["improvements"],
                evaluated_at=datetime.now()
            )
            
            return feedback
            
        except Exception as e:
            # Fallback evaluation in case of LLM failure
            print(f"LLM evaluation failed: {e}")
            return self._fallback_evaluation(answer, question)
    
    async def _evaluate_with_gemini(self, prompt: str) -> str:
        """Evaluate using Google Gemini"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini evaluation failed: {e}")
            raise e
    
    def _fallback_evaluation(self, answer: Answer, question: Question) -> Feedback:
        """Fallback evaluation when LLM fails"""
        # Simple rule-based fallback
        answer_length = len(answer.answer_text.split())
        
        if answer_length < 10:
            score = 2
            feedback = "Answer is too brief. Please provide more detailed responses."
        elif answer_length < 50:
            score = 3
            feedback = "Good start, but could benefit from more elaboration and specific examples."
        elif answer_length < 100:
            score = 4
            feedback = "Well-structured answer with good detail. Consider adding specific examples."
        else:
            score = 4
            feedback = "Comprehensive answer with good detail and structure."
        
        return Feedback(
            answer_id=answer.id,
            session_id=answer.session_id,
            score=score,
            feedback_text=feedback,
            criteria_scores={
                "technical_accuracy": score,
                "communication": score,
                "problem_solving": score,
                "knowledge_depth": score,
                "relevance": score
            },
            strengths=["Provided a response"],
            improvements=["Could provide more specific examples"],
            evaluated_at=datetime.now()
        )

class QuestionGenerator:
    """Generate tailored interview questions based on role and experience"""
    
    def __init__(self):
        # Initialize OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "demo_key_placeholder":
            self.openai_client = openai.OpenAI(api_key=openai_key)
            self.use_openai = True
        else:
            self.openai_client = None
            self.use_openai = False
        
        # Initialize Google Gemini
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            genai.configure(api_key=google_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_gemini = True
        else:
            self.gemini_model = None
            self.use_gemini = False
        
        # Set primary LLM preference
        self.use_llm = self.use_openai or self.use_gemini
        
        if not self.use_llm:
            print("Warning: No LLM API keys configured. Using fallback questions.")
        else:
            primary = "OpenAI" if self.use_openai else "Google Gemini"
            print(f"Question Generator initialized with {primary}")
        
    def generate_questions_prompt(self, candidate: Candidate, num_questions: int = 5) -> str:
        """Generate prompt for question generation"""
        return f"""
Generate {num_questions} interview questions for the following candidate profile:

CANDIDATE PROFILE:
- Position: {candidate.position}
- Experience Level: {candidate.experience_level}
- Skills: {', '.join(candidate.skills) if candidate.skills else 'Not specified'}

REQUIREMENTS:
- Mix of technical and behavioral questions appropriate for the role
- Questions should match the candidate's experience level
- Include 1-2 situational questions
- Vary difficulty levels appropriately

RESPONSE FORMAT:
Please respond with a JSON array of questions:
[
    {{
        "question_text": "<question text>",
        "question_type": "technical|behavioral|situational",
        "difficulty_level": <1-5 integer>,
        "expected_duration": <seconds>,
        "rationale": "<why this question is relevant>"
    }}
]

Make questions engaging, relevant, and fair for the candidate's level.
"""
    
    async def generate_questions(self, candidate: Candidate, num_questions: int = 5) -> List[Question]:
        """Generate tailored questions for a candidate"""
        try:
            if not self.use_llm:
                return self._fallback_questions(candidate, num_questions)
                
            prompt = self.generate_questions_prompt(candidate, num_questions)
            
            # Try OpenAI first, then Gemini as fallback
            if self.use_openai:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert interview question designer with deep knowledge of various technical roles and interview best practices."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )
                    questions_text = response.choices[0].message.content
                    
                except Exception as e:
                    print(f"OpenAI question generation failed: {e}")
                    if self.use_gemini:
                        questions_text = await self._generate_with_gemini(prompt)
                    else:
                        return self._fallback_questions(candidate, num_questions)
            
            elif self.use_gemini:
                questions_text = await self._generate_with_gemini(prompt)
            
            else:
                return self._fallback_questions(candidate, num_questions)
            
            # Parse questions result
            try:
                questions_data = json.loads(questions_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = questions_text.find('[')
                end = questions_text.rfind(']') + 1
                if start >= 0 and end > start:
                    questions_data = json.loads(questions_text[start:end])
                else:
                    return self._fallback_questions(candidate, num_questions)
            
            questions = []
            for i, q_data in enumerate(questions_data):
                question = Question(
                    session_id="",  # Will be set when creating session
                    question_text=q_data["question_text"],
                    question_type=q_data["question_type"],
                    difficulty_level=q_data["difficulty_level"],
                    expected_duration=q_data["expected_duration"],
                    order_index=i + 1
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            print(f"Question generation failed: {e}")
            return self._fallback_questions(candidate, num_questions)
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate questions using Google Gemini"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini question generation failed: {e}")
            raise e
    
    def _fallback_questions(self, candidate: Candidate, num_questions: int) -> List[Question]:
        """Fallback questions when LLM fails"""
        fallback_questions = [
            {
                "text": f"Tell me about your experience with {candidate.position} roles.",
                "type": "behavioral",
                "difficulty": 2,
                "duration": 120
            },
            {
                "text": "Describe a challenging project you worked on and how you overcame obstacles.",
                "type": "behavioral", 
                "difficulty": 3,
                "duration": 180
            },
            {
                "text": f"What technical skills do you think are most important for a {candidate.position}?",
                "type": "technical",
                "difficulty": 3,
                "duration": 150
            },
            {
                "text": "How do you stay updated with the latest technologies in your field?",
                "type": "behavioral",
                "difficulty": 2,
                "duration": 120
            },
            {
                "text": "Describe a time when you had to work under pressure to meet a deadline.",
                "type": "situational",
                "difficulty": 3,
                "duration": 150
            }
        ]
        
        questions = []
        for i, q in enumerate(fallback_questions[:num_questions]):
            question = Question(
                session_id="",
                question_text=q["text"],
                question_type=q["type"],
                difficulty_level=q["difficulty"],
                expected_duration=q["duration"],
                order_index=i + 1
            )
            questions.append(question)
        
        return questions
