import os
import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai
from dotenv import load_dotenv

# Import enterprise framework components
from screen import AppiumBase, SecurityContext, PerformanceMetrics

load_dotenv()


class LocatorQuality(Enum):
    """Locator quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


@dataclass
class LocatorAnalysis:
    """Comprehensive locator analysis result."""
    element_name: str
    primary_locator: Dict[str, str]
    fallback_locators: List[Dict[str, str]]
    element_type: str
    suggested_actions: List[str]
    validation_text: Optional[str]
    screen_context: str
    quality_score: LocatorQuality
    accessibility_info: Dict[str, str]
    confidence: float


class AILocatorGenerator(AppiumBase):
    """
    Enterprise AI-powered locator generator with schema validation.
    
    Combines intelligent element detection, AI-powered analysis, and 
    enterprise framework capabilities for robust locator generation.
    """
    
    # Expert mobile automation prompt for comprehensive screen analysis
    LOCATOR_GENERATION_PROMPT = """
    You are an expert mobile automation engineer. Analyze the provided mobile screen content 
    and generate enterprise-grade locators for the target element with comprehensive coverage.
    
    INPUT ANALYSIS:
    • XML may contain multiple <scroll-position> sections - analyze ALL of them
    • Capture every interactive element across all scroll positions
    • Consider user-specific data (usernames, phone numbers) for dynamic content
    
    LOCATOR STRATEGY FOCUS:
    • Stability: Prefer ID > accessibility-id > class > xpath
    • Dynamic Content: Use partial matches for user-specific fields
    • Accessibility: Include content descriptions and roles
    • Performance: Optimize for fast element detection
    • Cross-Device: Ensure locators work on different screen sizes
    
    TARGET ELEMENT: "{target_element}"
    SCREEN CONTEXT: "{screen_context}"
    
    XML PAGE SOURCE:
    {page_source}
    
    CRITICAL JSON FORMATTING RULES:
    • Return ONLY valid JSON - no comments, no trailing commas
    • Do NOT use // comments anywhere in the JSON
    • Ensure all arrays and objects end without trailing commas
    • Use proper JSON syntax throughout
    • For dynamic content (usernames, phone numbers), create robust locators using contains() or partial text matching
    
    Generate ONLY valid JSON matching this exact structure:
    """
    
    def __init__(self, security_context: SecurityContext = SecurityContext.INTERNAL):
        """Initialize enterprise locator generator."""
        super().__init__(security_context=security_context)
        
        # Initialize AI model
        self._setup_ai_model()
        
        # Load locator schema for validation
        self._load_locator_schema()
        
        # Performance tracking
        self._generation_metrics: List[PerformanceMetrics] = []
        
        self.logger.info("Enterprise AI Locator Generator initialized")
    
    def _setup_ai_model(self) -> None:
        """Configure Gemini AI model with enterprise settings."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key.startswith('your_'):
            raise ValueError("GEMINI_API_KEY not configured properly")
        
        # Log only first 2 characters for security [[memory:7700143]]
        masked_key = f"{api_key[:2]}{'*' * (len(api_key) - 2)}"
        self.logger.info(f"Gemini API configured with key: {masked_key}")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'),
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2000,
                temperature=0.1,
                candidate_count=1
            )
        )
        
        self._audit("ai_model_initialization", "SUCCESS")
    
    def _load_locator_schema(self) -> None:
        """Load and validate locator schema."""
        try:
            schema_path = Path("locator_schema.json")
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            # Extract supported strategies and actions for validation
            self.supported_strategies = self.schema['definitions']['locator_strategy']['enum']
            self.supported_actions = self.schema['definitions']['action_type']['enum']
            self.element_types = self.schema['properties']['element_locators']['patternProperties']['^[a-zA-Z_][a-zA-Z0-9_]*$']['properties']['element_type']['enum']
            
            self.logger.info(f"Locator schema loaded: {len(self.supported_strategies)} strategies, {len(self.supported_actions)} actions")
            self._audit("schema_loading", "SUCCESS")
            
        except Exception as e:
            self.logger.error(f"Failed to load locator schema: {e}")
            self._audit("schema_loading", f"FAILED: {e}")
            raise
        
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract and clean JSON from AI response."""
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        
        # Find JSON object
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Fallback: try to find any valid JSON structure
        try:
            # Attempt to parse the entire response
            json.loads(response_text.strip())
            return response_text.strip()
        except json.JSONDecodeError:
            raise ValueError("No valid JSON found in AI response")
    
    def _assess_locator_quality(self, locator: Dict[str, str]) -> LocatorQuality:
        """Assess the quality of a generated locator."""
        strategy = locator.get('strategy', '')
        value = locator.get('value', '')
        
        # Quality assessment based on strategy and characteristics
        if strategy == 'id' and value and not '//' in value:
            return LocatorQuality.EXCELLENT
        elif strategy == 'accessibility_id' and value:
            return LocatorQuality.EXCELLENT
        elif strategy == 'class_name' and value and not '//' in value:
            return LocatorQuality.GOOD
        elif strategy == 'xpath' and value.count('/') <= 3:
            return LocatorQuality.GOOD
        elif strategy == 'xpath' and value.count('/') <= 6:
            return LocatorQuality.ACCEPTABLE
        else:
            return LocatorQuality.POOR
    
    def _validate_generated_locator(self, locator_data: Dict) -> bool:
        """Validate generated locator against schema."""
        try:
            # Check required fields
            required_fields = ['element_name', 'element_type', 'primary_locator']
            for field in required_fields:
                if field not in locator_data:
                    return False
            
            # Validate primary locator
            primary = locator_data['primary_locator']
            if primary['strategy'] not in self.supported_strategies:
                return False
            
            # Validate element type
            if locator_data['element_type'] not in self.element_types:
                return False
            
            # Validate actions if present
            if 'suggested_actions' in locator_data:
                for action in locator_data['suggested_actions']:
                    if action not in self.supported_actions:
                        return False
            
            return True
            
        except (KeyError, TypeError):
            return False
    
    def analyze_complete_screen(self, merged_xml: str, screen_context: str = "complete_screen") -> Dict[str, LocatorAnalysis]:
        """
        Analyze complete stitched screen with merged XML containing multiple scroll positions.
        
        Args:
            merged_xml: XML containing multiple <scroll-position> sections
            screen_context: Screen context for the complete analysis
            
        Returns:
            Dict[str, LocatorAnalysis]: All interactive elements found across scroll positions
        """
        with self._performance_tracking("complete_screen_analysis"):
            # Enhanced prompt for complete screen analysis
            complete_screen_prompt = """
            You are an expert mobile automation engineer. Analyze this COMPLETE mobile screen content 
            with merged XML containing multiple scroll positions.
            
            COMPREHENSIVE ANALYSIS REQUIREMENTS:
            • XML contains multiple <scroll-position> sections - analyze ALL of them
            • Generate locators for EVERY interactive element (buttons, inputs, clickables, text fields)
            • Include scroll position context for each element
            • Handle dynamic content (usernames, phone numbers) with robust locators
            
            LOCATOR STRATEGY:
            • Stability: ID > accessibility-id > class > xpath
            • Dynamic Content: Use contains(), starts-with(), or partial matching
            • Multi-Device: Ensure compatibility across screen sizes
            • Performance: Optimize for fast detection
            
            SCREEN CONTEXT: {screen_context}
            
            MERGED XML WITH SCROLL POSITIONS:
            {merged_xml}
            
            CRITICAL: Return ONLY valid JSON with NO comments, NO trailing commas.
            Generate comprehensive element mapping with this structure:
            {{
                "screen_elements": {{
                    "element_name": {{
                        "element_name": "descriptive_name",
                        "element_type": "button|text_field|text_view|image|checkbox|dropdown|list_item",
    "primary_locator": {{
                            "strategy": "id|accessibility_id|class_name|xpath|android_uiautomator",
                            "value": "locator_value",
                            "timeout": 15
                        }},
                        "description": "Comprehensive description handling dynamic content",
                        "suggested_actions": ["click", "send_keys", "verify_text"],
                        "scroll_position": "top|middle|bottom|position_number",
                        "screen_context": "{screen_context}",
                        "dynamic_content_handling": "strategy for user-specific data",
                        "accessibility_info": {{
                            "content_desc": "accessibility_description",
                            "role": "element_role"
                        }}
                    }}
                }}
            }}
            """
            
            try:
                formatted_prompt = complete_screen_prompt.format(
                    screen_context=screen_context,
                    merged_xml=merged_xml[:8000]  # Limit for API efficiency
                )
                
                response = self.model.generate_content(formatted_prompt)
            except Exception as e:
                self.logger.error(f"Failed to generate content: {e}")
                raise
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            try:
                # Extract and parse JSON
                json_text = self._extract_json_from_response(response.text)
                screen_data = json.loads(json_text)
                
                # Convert to LocatorAnalysis objects
                analyses = {}
                screen_elements = screen_data.get('screen_elements', {})
                
                for element_name, element_data in screen_elements.items():
                    # Assess quality and calculate confidence
                    quality = self._assess_locator_quality(element_data['primary_locator'])
                    confidence = self._calculate_confidence(element_data, merged_xml)
                    
                    analysis = LocatorAnalysis(
                        element_name=element_data['element_name'],
                        primary_locator=element_data['primary_locator'],
                        fallback_locators=element_data.get('fallback_locators', []),
                        element_type=element_data['element_type'],
                        suggested_actions=element_data.get('suggested_actions', []),
                        validation_text=element_data.get('validation_text'),
                        screen_context=f"{screen_context}_{element_data.get('scroll_position', 'unknown')}",
                        quality_score=quality,
                        accessibility_info=element_data.get('accessibility_info', {}),
                        confidence=confidence
                    )
                    
                    analyses[element_name] = analysis
                
                self.logger.info(f"Complete screen analysis generated {len(analyses)} element locators")
                self._audit("complete_screen_analysis", f"SUCCESS: {len(analyses)} elements")
                
                return analyses
                
            except Exception as e:
                self.logger.error(f"Complete screen analysis failed: {e}")
                self._audit("complete_screen_analysis", f"FAILED: {e}")
                raise

    def analyze_element(self, target_element: str, screen_context: str = "unknown", 
                       page_source: Optional[str] = None) -> LocatorAnalysis:
        """
        Analyze element and generate comprehensive locator information.
        
        Args:
            target_element: Name/description of the target element
            screen_context: Screen or page context where element appears
            page_source: XML page source (auto-captured if not provided)
            
        Returns:
            LocatorAnalysis: Comprehensive locator analysis result
        """
        with self._performance_tracking("element_analysis"):
            # Get page source if not provided
            if not page_source:
                if not self.driver:
                    raise ValueError("No page source provided and driver not initialized")
                page_source = self.get_page_source()
            
            # Truncate page source for API efficiency
            truncated_source = page_source[:4000] if len(page_source) > 4000 else page_source
            
            # Build comprehensive schema-compliant template
            schema_template = {
                "element_name": target_element,
                "element_type": "button|text_field|text_view|image|checkbox|radio_button|dropdown|list_item|container",
                "primary_locator": {
                    "strategy": "id|xpath|class_name|accessibility_id|android_uiautomator|name|tag_name",
                    "value": "locator_value",
                    "timeout": 15
                },
                "fallback_locators": [
                    {
                        "strategy": "strategy_type",
                        "value": "fallback_value",
                        "timeout": 15
                    }
                ],
                "description": "Detailed element description",
                "suggested_actions": ["click", "send_keys", "verify_text"],
                "validation_text": "expected_text_content",
                "screen_context": screen_context,
                "accessibility_info": {
                    "content_desc": "accessibility_description",
                    "role": "element_role",
                    "hint": "interaction_hint"
                }
            }
            
            # Generate AI prompt
            prompt = self.LOCATOR_GENERATION_PROMPT.format(
                target_element=target_element,
                screen_context=screen_context,
                page_source=truncated_source
            ) + json.dumps(schema_template, indent=2)
            
            try:
                # Generate content with AI
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    raise Exception("Empty response from Gemini API")
                
                # Extract and parse JSON
                json_text = self._extract_json_from_response(response.text)
                locator_data = json.loads(json_text)
                
                # Validate against schema
                if not self._validate_generated_locator(locator_data):
                    raise ValueError("Generated locator doesn't match schema requirements")
                
                # Assess quality
                quality = self._assess_locator_quality(locator_data['primary_locator'])
                
                # Calculate confidence based on multiple factors
                confidence = self._calculate_confidence(locator_data, page_source)
                
                # Create analysis result
                analysis = LocatorAnalysis(
                    element_name=locator_data['element_name'],
                    primary_locator=locator_data['primary_locator'],
                    fallback_locators=locator_data.get('fallback_locators', []),
                    element_type=locator_data['element_type'],
                    suggested_actions=locator_data.get('suggested_actions', []),
                    validation_text=locator_data.get('validation_text'),
                    screen_context=locator_data.get('screen_context', screen_context),
                    quality_score=quality,
                    accessibility_info=locator_data.get('accessibility_info', {}),
                    confidence=confidence
                )
                
                self.logger.info(f"Generated {quality.value} quality locators for '{target_element}' (confidence: {confidence:.2f})")
                self._audit("locator_generation", f"SUCCESS: {target_element}")
                
                return analysis
                
            except Exception as e:
                self.logger.error(f"Locator generation failed for '{target_element}': {e}")
                self._audit("locator_generation", f"FAILED: {target_element} - {e}")
                raise
    
    def _calculate_confidence(self, locator_data: Dict, page_source: str) -> float:
        """Calculate confidence score for generated locators."""
        confidence = 0.5  # Base confidence
        
        # Strategy reliability boost
        strategy = locator_data['primary_locator']['strategy']
        strategy_scores = {
            'id': 0.4, 'accessibility_id': 0.35, 'class_name': 0.2,
            'android_uiautomator': 0.15, 'xpath': 0.1, 'name': 0.1, 'tag_name': 0.05
        }
        confidence += strategy_scores.get(strategy, 0)
        
        # Fallback locators boost
        fallback_count = len(locator_data.get('fallback_locators', []))
        confidence += min(fallback_count * 0.05, 0.15)
        
        # Accessibility info boost
        if locator_data.get('accessibility_info', {}).get('content_desc'):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def generate_locators_for_test_case(self, test_case: Dict, screen_context: str = "test_screen") -> Dict[str, LocatorAnalysis]:
        """Generate locators for all elements in a test case."""
        locators = {}
        page_source = None
        
        # Get page source once for efficiency
        if self.driver:
            page_source = self.get_page_source()
        
        with self._performance_tracking("test_case_locator_generation"):
            for step in test_case.get('steps', []):
                element_name = step.get('element')
                if element_name and element_name not in locators:
                    try:
                        analysis = self.analyze_element(
                            target_element=element_name,
                            screen_context=screen_context,
                            page_source=page_source
                        )
                        locators[element_name] = analysis
                        
                    except Exception as e:
                        self.logger.error(f"Failed to generate locator for '{element_name}': {e}")
                        # Continue with other elements rather than failing entirely
                        continue
                
        self.logger.info(f"Generated locators for {len(locators)} elements in test case")
        return locators
    
    def save_locators_schema_compliant(self, locators: Dict[str, LocatorAnalysis], 
                                     test_case_name: str) -> str:
        """Save locators in schema-compliant format."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Convert to schema-compliant format
        schema_compliant = {
            "element_locators": {},
            "test_case_structure": {
                "test_name": test_case_name,
                "test_type": "positive",
                "description": f"Auto-generated locators for {test_case_name}",
                "steps": []
            },
            "configuration": {
                "supported_strategies": self.supported_strategies,
                "supported_actions": self.supported_actions,
                "default_timeout": 15,
                "retry_attempts": 3,
                "screenshot_on_failure": True
            }
        }
        
        # Add element locators
        for element_name, analysis in locators.items():
            schema_compliant["element_locators"][element_name] = {
                "element_name": analysis.element_name,
                "element_type": analysis.element_type,
                "primary_locator": analysis.primary_locator,
                "fallback_locators": analysis.fallback_locators,
                "description": f"Auto-generated locator for {analysis.element_name}",
                "suggested_actions": analysis.suggested_actions,
                "validation_text": analysis.validation_text,
                "screen_context": analysis.screen_context,
                "accessibility_info": analysis.accessibility_info
            }
        
        # Save to file
        filename = f"locators_{test_case_name}.json"
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(schema_compliant, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Schema-compliant locators saved: {file_path}")
        self._audit("locator_file_save", f"SUCCESS: {filename}")
        
        return str(file_path)
    
    def get_generation_metrics(self) -> List[PerformanceMetrics]:
        """Get locator generation performance metrics."""
        return self._generation_metrics + self.get_performance_metrics()