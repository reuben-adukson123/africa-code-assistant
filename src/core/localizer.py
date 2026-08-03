"""
African Language Support Module
"""

import json
from pathlib import Path

# Use absolute import
from utils.logger import get_logger

logger = get_logger(__name__)


class Localizer:
    """Handles localization for African languages."""
    
    # Language codes
    LANGUAGES = {
        'en': 'English',
        'ha': 'Hausa',
        'yo': 'Yoruba',
        'ig': 'Igbo'
    }
    
    # Common translations
    TRANSLATIONS = {
        'en': {
            'welcome': "Welcome to Africa Code Assistant! How can I help you?",
            'generate': "Generate Code",
            'explain': "Explain Code",
            'debug': "Debug Code",
            'optimize': "Optimize Code",
            'translate': "Translate Code",
            'error': "Error",
            'success': "Success",
            'loading': "Loading...",
            'ready': "Ready",
            'processing': "Processing...",
            'no_code': "Please enter some code first.",
            'language_switch': "Language switched to English."
        },
        'ha': {
            'welcome': "Barka da zuwa Africa Code Assistant! Ta yaya zan taimake ku?",
            'generate': "Ƙirƙiri Code",
            'explain': "Bayyana Code",
            'debug': "Gyara Code",
            'optimize': "Inganta Code",
            'translate': "Fassara Code",
            'error': "Kuskure",
            'success': "Nasara",
            'loading': "Ana lodi...",
            'ready': "A shirye",
            'processing': "Ana aiki...",
            'no_code': "Da fatan za a shigar da wasu code da farko.",
            'language_switch': "An canza harshe zuwa Hausa."
        },
        'yo': {
            'welcome': "Kaabọ si Africa Code Assistant! Bawo ni mo ṣe le ran ọ lọwọ?",
            'generate': "Ṣe Code",
            'explain': "Ṣalaye Code",
            'debug': "Ṣatunṣe Code",
            'optimize': "Muu dara",
            'translate': "Tumọ Code",
            'error': "Aṣiṣe",
            'success': "Aṣeyọri",
            'loading': "N gbe...",
            'ready': "Ṣetan",
            'processing': "Nṣiṣẹ...",
            'no_code': "Jọwọ tẹ koodu diẹ sii.",
            'language_switch': "Ede ti yipada si Yoruba."
        },
        'ig': {
            'welcome': "Nnọọ na Africa Code Assistant! Kedu ka m ga-enyere gị aka?",
            'generate': "Mepụta Code",
            'explain': "Kọwaa Code",
            'debug': "Dozie Code",
            'optimize': "Mee ka ọ dị mma",
            'translate': "Sụgharịa Code",
            'error': "Njehie",
            'success': "Ihe ịga nke ọma",
            'loading': "Na-ebu...",
            'ready': "Ọ dị njikere",
            'processing': "Na-arụ...",
            'no_code': "Biko tinye koodu mbụ.",
            'language_switch': "Ederede agbanweela gaa Igbo."
        }
    }
    
    def __init__(self, config):
        """Initialize the localizer."""
        self.config = config
        self.current_language = config.get('language', 'en')
        
        # Load additional translations if available
        self.extra_translations = self._load_extra_translations()
    
    def _load_extra_translations(self) -> Dict:
        """Load extra translations from file."""
        translations_path = Path(__file__).parent.parent / "resources" / "translations.json"
        if translations_path.exists():
            try:
                with open(translations_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load extra translations: {e}")
        return {}
    
    def get_text(self, key: str, language: Optional[str] = None) -> str:
        """Get translated text."""
        lang = language or self.current_language
        
        # Check extra translations first
        if lang in self.extra_translations and key in self.extra_translations[lang]:
            return self.extra_translations[lang][key]
        
        # Check base translations
        if lang in self.TRANSLATIONS and key in self.TRANSLATIONS[lang]:
            return self.TRANSLATIONS[lang][key]
        
        # Fallback to English
        if key in self.TRANSLATIONS['en']:
            return self.TRANSLATIONS['en'][key]
        
        # Return key if translation not found
        return key
    
    def get_welcome_message(self, language: Optional[str] = None) -> str:
        """Get welcome message."""
        return self.get_text('welcome', language)
    
    def get_prompt(self, action: str, code: str, language: str, ui_lang: str = 'en') -> str:
        """Get localized prompt for LLM."""
        # Base prompt in English (for model)
        prompts = {
            'generate': f"Generate {language} code for: {code}",
            'explain': f"Explain this {language} code: {code}",
            'debug': f"Debug this {language} code: {code}",
            'optimize': f"Optimize this {language} code: {code}",
            'translate': f"Translate this code to {language}: {code}"
        }
        
        base_prompt = prompts.get(action, f"Process this code: {code}")
        
        # Add UI language context if not English
        if ui_lang != 'en':
            ui_context = f"Please respond in {self.LANGUAGES.get(ui_lang, 'English')}."
            return f"{base_prompt}\n\n{ui_context}"
        
        return base_prompt
    
    def detect_language(self, text: str) -> str:
        """Detect if text contains African language markers."""
        # Simple detection based on common words
        hausa_words = ['ina', 'ka', 'ki', 'mu', 'ku', 'su', 'wane', 'wata']
        yoruba_words = ['mo', 'o', 'a', 'e', 'won', 'ni', 'ti', 'si']
        igbo_words = ['m', 'i', 'a', 'unu', 'ha', 'na', 'ka', 'ma']
        
        words = text.lower().split()
        
        hausa_count = sum(1 for w in words if w in hausa_words)
        yoruba_count = sum(1 for w in words if w in yoruba_words)
        igbo_count = sum(1 for w in words if w in igbo_words)
        
        # Detect based on highest count
        max_count = max(hausa_count, yoruba_count, igbo_count)
        if max_count > 2:
            if hausa_count == max_count:
                return 'ha'
            elif yoruba_count == max_count:
                return 'yo'
            elif igbo_count == max_count:
                return 'ig'
        
        return 'en'
    
    def set_language(self, language: str):
        """Set the current language."""
        if language in self.LANGUAGES:
            self.current_language = language
            logger.info(f"Language set to {self.LANGUAGES[language]}")
            return True
        return False
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        return list(self.LANGUAGES.keys())
    
    def get_language_name(self, code: str) -> str:
        """Get language name from code."""
        return self.LANGUAGES.get(code, code)
