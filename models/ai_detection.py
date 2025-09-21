import re
import numpy as np
import random
from datetime import datetime

# Optional dependency: TextBlob. Provide a safe fallback if unavailable.
try:
    from textblob import TextBlob  # type: ignore
    _TEXTBLOB_AVAILABLE = True
except Exception:  # pragma: no cover - environment-specific
    TextBlob = None  # type: ignore
    _TEXTBLOB_AVAILABLE = False

class AIDetector:
    def __init__(self):
        # AI-generated text patterns and characteristics
        self.ai_patterns = {
            'ai_introductions': [
                'sure! here\'s', 'certainly! here\'s', 'of course! here\'s', 'absolutely! here\'s',
                'here\'s a', 'here\'s an', 'i\'ll provide', 'let me provide', 'i can help',
                'i\'d be happy to', 'i\'ll create', 'let me create', 'here\'s what'
            ],
            'ai_disclaimers': [
                'ai language model', 'generated using ai', 'ai-generated', 'language model',
                'for educational purposes only', 'not financial advice', 'consult with.*advisor',
                'this.*generated.*ai', 'ai.*model', 'artificial intelligence',
                'please note that this', 'disclaimer.*ai', 'automated.*analysis'
            ],
            'ai_hedging_strong': [
                'based on available data', 'according to current information', 'as of.*date',
                'information available as of', 'data suggests', 'analysis indicates',
                'trends suggest', 'patterns indicate', 'evidence points to'
            ],
            'repetitive_phrases': [
                'it is important to note', 'it should be noted', 'furthermore', 'moreover',
                'in conclusion', 'to summarize', 'in summary', 'overall', 'additionally',
                'however', 'nevertheless', 'on the other hand', 'consequently'
            ],
            'formal_transitions': [
                'firstly', 'secondly', 'thirdly', 'finally', 'in addition',
                'as a result', 'therefore', 'thus', 'hence', 'accordingly'
            ],
            'generic_statements': [
                'comprehensive analysis', 'thorough examination', 'detailed assessment',
                'careful consideration', 'extensive research', 'in-depth analysis',
                'significant impact', 'substantial growth', 'considerable potential'
            ],
            'ai_hedging': [
                'may potentially', 'could possibly', 'might suggest', 'appears to indicate',
                'seems to suggest', 'potentially indicates', 'may imply', 'could imply'
            ],
            'ai_formatting': [
                'here are.*key points', 'key takeaways', 'main highlights',
                'summary of findings', 'executive summary', 'key insights',
                'important considerations', 'notable observations'
            ]
        }
        
        # Emoji detection regex (common emoji Unicode ranges)
        self.emoji_pattern = re.compile(
            "[" 
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & pictographs
            "\U0001F680-\U0001F6FF"  # Transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # Flags
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # Enclosed characters
            "]",
            flags=re.UNICODE,
        )
        
        # Human writing characteristics
        self.human_patterns = {
            'personal_opinions': [
                'i believe', 'in my opinion', 'i think', 'personally', 'from my experience',
                'i would argue', 'my view is', 'i suspect', 'i feel', 'i recommend'
            ],
            'informal_language': [
                'quite frankly', 'to be honest', 'let\'s face it', 'bottom line',
                'at the end of the day', 'the reality is', 'frankly speaking'
            ],
            'specific_examples': [
                'for instance', 'for example', 'take the case of', 'consider',
                'look at', 'remember when', 'recall that'
            ],
            'contractions': [
                'don\'t', 'won\'t', 'can\'t', 'shouldn\'t', 'wouldn\'t', 'isn\'t',
                'aren\'t', 'hasn\'t', 'haven\'t', 'didn\'t', 'couldn\'t'
            ]
        }

    def detect_ai_content(self, text):
        """
        Analyze text to determine if it's AI-generated or human-written
        Returns a score between 0 (definitely human) and 1 (definitely AI)
        """
        if not text or len(text.strip()) < 50:
            return {
                'ai_probability': 0.5,
                'confidence': 0.1,
                'classification': 'Insufficient Data',
                'detailed_analysis': {},
                'explanation': 'Text too short for reliable analysis'
            }
        
        # Hard rule requested: If emojis are present, classify as AI-generated
        try:
            if self._contains_emojis(text):
                return {
                    'ai_probability': 0.9,
                    'human_probability': 0.1,
                    'confidence': 0.85,
                    'classification': 'Likely AI-Generated',
                    'detailed_analysis': {'emojis_detected': True},
                    'explanation': 'Emojis were detected in the report text, which this system treats as an AI-generated indicator.',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception:
            # Fail open to normal pipeline if emoji check has any unicode issues
            pass
        
        # Quick check for obvious AI indicators
        obvious_ai_score = self._check_obvious_ai_indicators(text)
        if obvious_ai_score > 0.8:
            return {
                'ai_probability': obvious_ai_score,
                'human_probability': 1 - obvious_ai_score,
                'confidence': 0.9,
                'classification': 'Likely AI-Generated',
                'detailed_analysis': {'obvious_ai_detected': True},
                'explanation': 'Contains obvious AI-generated content indicators like AI disclaimers or typical AI introduction phrases.',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Perform various analyses
        linguistic_analysis = self._analyze_linguistic_patterns(text)
        structural_analysis = self._analyze_text_structure(text)
        vocabulary_analysis = self._analyze_vocabulary_complexity(text)
        pattern_analysis = self._analyze_ai_human_patterns(text)
        consistency_analysis = self._analyze_writing_consistency(text)
        
        # Calculate weighted AI probability
        ai_probability = self._calculate_ai_probability(
            linguistic_analysis, structural_analysis, vocabulary_analysis,
            pattern_analysis, consistency_analysis
        )
        
        # Determine confidence level
        confidence = self._calculate_confidence(
            linguistic_analysis, structural_analysis, vocabulary_analysis,
            pattern_analysis, consistency_analysis
        )
        
        # Classification
        classification = self._classify_content(ai_probability, confidence)
        
        # Generate explanation
        explanation = self._generate_explanation(
            ai_probability, linguistic_analysis, structural_analysis,
            pattern_analysis, consistency_analysis
        )
        
        return {
            'ai_probability': round(ai_probability, 3),
            'human_probability': round(1 - ai_probability, 3),
            'confidence': round(confidence, 3),
            'classification': classification,
            'detailed_analysis': {
                'linguistic_analysis': linguistic_analysis,
                'structural_analysis': structural_analysis,
                'vocabulary_analysis': vocabulary_analysis,
                'pattern_analysis': pattern_analysis,
                'consistency_analysis': consistency_analysis
            },
            'explanation': explanation,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _analyze_linguistic_patterns(self, text):
        """Analyze linguistic patterns that may indicate AI generation"""
        if not _TEXTBLOB_AVAILABLE or TextBlob is None:
            # Fallback: naive splitting into sentences/words without sentiment
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            words = [w.lower() for w in re.findall(r"[A-Za-z']+", text)]
            if not sentences:
                return {'error': 'No sentences found'}
            # Compute approximations without sentiment
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_sentence_length = float(np.mean(sentence_lengths)) if sentence_lengths else 0.0
            sentence_length_variance = float(np.var(sentence_lengths)) if sentence_lengths else 0.0
            unique_words = set(words)
            ttr = len(unique_words) / len(words) if words else 0
            sentiment_variance = 0.0
            total_words = len(words)
            total_sentences = len(sentences)
            avg_words_per_sentence = total_words / total_sentences if total_sentences > 0 else 0
            ai_indicators = {
                'consistent_sentence_length': sentence_length_variance < 20,
                'moderate_vocabulary_diversity': 0.3 < ttr < 0.7,
                'consistent_sentiment': True,
                'optimal_readability': 15 < avg_words_per_sentence < 25
            }
            ai_score = sum(ai_indicators.values()) / len(ai_indicators)
            return {
                'avg_sentence_length': round(avg_sentence_length, 2),
                'sentence_length_variance': round(sentence_length_variance, 2),
                'type_token_ratio': round(ttr, 3),
                'sentiment_variance': round(sentiment_variance, 3),
                'avg_words_per_sentence': round(avg_words_per_sentence, 2),
                'ai_indicators': ai_indicators,
                'linguistic_ai_score': round(ai_score, 3)
            }

        blob = TextBlob(text)
        sentences = blob.sentences
        
        if not sentences:
            return {'error': 'No sentences found'}
        
        # Sentence length analysis
        sentence_lengths = [len(str(sentence).split()) for sentence in sentences]
        avg_sentence_length = np.mean(sentence_lengths)
        sentence_length_variance = np.var(sentence_lengths)
        
        # Vocabulary diversity (Type-Token Ratio)
        words = [word.lower() for word in blob.words if word.isalpha()]
        unique_words = set(words)
        ttr = len(unique_words) / len(words) if words else 0
        
        # Sentiment consistency
        sentence_sentiments = [sentence.sentiment.polarity for sentence in sentences]
        sentiment_variance = np.var(sentence_sentiments) if sentence_sentiments else 0
        
        # Readability approximation (Flesch-like)
        total_words = len(words)
        total_sentences = len(sentences)
        avg_words_per_sentence = total_words / total_sentences if total_sentences > 0 else 0
        
        # AI tends to have more consistent sentence lengths and moderate TTR
        ai_indicators = {
            'consistent_sentence_length': sentence_length_variance < 20,  # Low variance
            'moderate_vocabulary_diversity': 0.3 < ttr < 0.7,  # Moderate TTR
            'consistent_sentiment': sentiment_variance < 0.1,  # Consistent sentiment
            'optimal_readability': 15 < avg_words_per_sentence < 25  # Optimal range
        }
        
        ai_score = sum(ai_indicators.values()) / len(ai_indicators)
        
        return {
            'avg_sentence_length': round(avg_sentence_length, 2),
            'sentence_length_variance': round(sentence_length_variance, 2),
            'type_token_ratio': round(ttr, 3),
            'sentiment_variance': round(sentiment_variance, 3),
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'ai_indicators': ai_indicators,
            'linguistic_ai_score': round(ai_score, 3)
        }

    def _analyze_text_structure(self, text):
        """Analyze text structure patterns"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Paragraph analysis
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = np.mean(paragraph_lengths) if paragraph_lengths else 0
        paragraph_variance = np.var(paragraph_lengths) if len(paragraph_lengths) > 1 else 0
        
        # Transition word usage
        transition_count = 0
        for pattern_list in self.ai_patterns.values():
            for pattern in pattern_list:
                transition_count += len(re.findall(pattern, text.lower()))
        
        transition_density = transition_count / len(sentences) if sentences else 0
        
        # Structure consistency (AI tends to be more structured)
        structure_indicators = {
            'consistent_paragraphs': paragraph_variance < 100,  # Consistent paragraph lengths
            'high_transition_usage': transition_density > 0.3,  # High transition word usage
            'balanced_structure': 50 < avg_paragraph_length < 150,  # Balanced paragraphs
            'formal_organization': len(paragraphs) >= 3  # Multiple paragraphs
        }
        
        structure_ai_score = sum(structure_indicators.values()) / len(structure_indicators)
        
        return {
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': round(avg_paragraph_length, 2),
            'paragraph_variance': round(paragraph_variance, 2),
            'transition_density': round(transition_density, 3),
            'structure_indicators': structure_indicators,
            'structure_ai_score': round(structure_ai_score, 3)
        }

    def _analyze_vocabulary_complexity(self, text):
        """Analyze vocabulary complexity and sophistication"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        if not words:
            return {'error': 'No words found'}
        
        # Word length analysis
        word_lengths = [len(word) for word in words]
        avg_word_length = np.mean(word_lengths)
        
        # Complex word count (words with 3+ syllables approximation)
        complex_words = [word for word in words if len(word) > 6]
        complex_word_ratio = len(complex_words) / len(words)
        
        # Repetition analysis
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        repeated_words = sum(1 for freq in word_freq.values() if freq > 2)
        repetition_ratio = repeated_words / len(set(words)) if words else 0
        
        # AI tends to use moderate complexity and some repetition
        vocabulary_indicators = {
            'moderate_word_length': 4 < avg_word_length < 6,  # Moderate complexity
            'balanced_complexity': 0.1 < complex_word_ratio < 0.3,  # Balanced complexity
            'some_repetition': 0.1 < repetition_ratio < 0.4,  # Some repetition
            'varied_vocabulary': len(set(words)) / len(words) > 0.4  # Reasonable variety
        }
        
        vocabulary_ai_score = sum(vocabulary_indicators.values()) / len(vocabulary_indicators)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'avg_word_length': round(avg_word_length, 2),
            'complex_word_ratio': round(complex_word_ratio, 3),
            'repetition_ratio': round(repetition_ratio, 3),
            'vocabulary_indicators': vocabulary_indicators,
            'vocabulary_ai_score': round(vocabulary_ai_score, 3)
        }

    def _analyze_ai_human_patterns(self, text):
        """Analyze specific AI vs Human writing patterns"""
        text_lower = text.lower()
        
        # Count AI patterns with weighted scoring
        ai_pattern_counts = {}
        total_ai_patterns = 0
        ai_weighted_score = 0
        
        # Define weights for different AI pattern categories (higher = more indicative of AI)
        pattern_weights = {
            'ai_introductions': 10,      # Very strong AI indicator
            'ai_disclaimers': 15,        # Extremely strong AI indicator
            'ai_hedging_strong': 8,      # Strong AI indicator
            'ai_formatting': 6,          # Moderate AI indicator
            'repetitive_phrases': 3,     # Weak AI indicator
            'formal_transitions': 2,     # Very weak AI indicator
            'generic_statements': 4,     # Moderate AI indicator
            'ai_hedging': 5              # Moderate AI indicator
        }
        
        for category, patterns in self.ai_patterns.items():
            count = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                count += matches
                # Add weighted score for this category
                weight = pattern_weights.get(category, 1)
                ai_weighted_score += matches * weight
            
            ai_pattern_counts[category] = count
            total_ai_patterns += count
        
        # Count Human patterns
        human_pattern_counts = {}
        total_human_patterns = 0
        
        for category, patterns in self.human_patterns.items():
            count = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
            human_pattern_counts[category] = count
            total_human_patterns += count
        
        # Calculate pattern ratios
        total_words = len(text.split())
        ai_pattern_density = total_ai_patterns / total_words if total_words > 0 else 0
        human_pattern_density = total_human_patterns / total_words if total_words > 0 else 0
        
        # Enhanced pattern-based AI probability using weighted scoring
        # Check for critical AI indicators first
        critical_ai_score = 0
        if ai_pattern_counts.get('ai_introductions', 0) > 0:
            critical_ai_score += 0.4  # Strong boost for AI introductions
        if ai_pattern_counts.get('ai_disclaimers', 0) > 0:
            critical_ai_score += 0.5  # Very strong boost for AI disclaimers
        if ai_pattern_counts.get('ai_hedging_strong', 0) > 0:
            critical_ai_score += 0.3  # Moderate boost for strong hedging
        
        # Base pattern score
        if ai_pattern_density + human_pattern_density > 0:
            base_pattern_score = ai_pattern_density / (ai_pattern_density + human_pattern_density)
        else:
            base_pattern_score = 0.5
        
        # Combine critical indicators with base pattern score
        pattern_ai_score = min(0.95, base_pattern_score + critical_ai_score)
        
        # If we found critical AI patterns, ensure minimum AI probability
        if critical_ai_score > 0.3:
            pattern_ai_score = max(0.75, pattern_ai_score)
        
        return {
            'ai_pattern_counts': ai_pattern_counts,
            'human_pattern_counts': human_pattern_counts,
            'total_ai_patterns': total_ai_patterns,
            'total_human_patterns': total_human_patterns,
            'ai_pattern_density': round(ai_pattern_density, 4),
            'human_pattern_density': round(human_pattern_density, 4),
            'ai_weighted_score': ai_weighted_score,
            'critical_ai_score': round(critical_ai_score, 3),
            'pattern_ai_score': round(pattern_ai_score, 3)
        }

    def _analyze_writing_consistency(self, text):
        """Analyze writing consistency patterns"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return {'error': 'Too few sentences for consistency analysis'}
        
        # Sentence structure consistency
        sentence_structures = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 0:
                # Simple structure analysis: starts with capital, has verbs, etc.
                structure = {
                    'starts_capital': sentence[0].isupper() if sentence else False,
                    'has_comma': ',' in sentence,
                    'has_conjunction': any(conj in sentence.lower() for conj in ['and', 'but', 'or', 'however']),
                    'word_count_range': 'short' if len(words) < 10 else 'medium' if len(words) < 20 else 'long'
                }
                sentence_structures.append(structure)
        
        # Calculate consistency metrics
        if sentence_structures:
            capital_consistency = sum(s['starts_capital'] for s in sentence_structures) / len(sentence_structures)
            comma_usage_consistency = abs(0.5 - sum(s['has_comma'] for s in sentence_structures) / len(sentence_structures))
            
            # Word count range distribution
            range_counts = {'short': 0, 'medium': 0, 'long': 0}
            for s in sentence_structures:
                range_counts[s['word_count_range']] += 1
            
            # AI tends to be more consistent
            consistency_indicators = {
                'high_capital_consistency': capital_consistency > 0.8,
                'moderate_comma_usage': comma_usage_consistency < 0.3,
                'balanced_sentence_lengths': max(range_counts.values()) / len(sentence_structures) < 0.7
            }
            
            consistency_ai_score = sum(consistency_indicators.values()) / len(consistency_indicators)
        else:
            consistency_ai_score = 0.5
            consistency_indicators = {}
        
        return {
            'sentence_count': len(sentences),
            'capital_consistency': round(capital_consistency, 3) if sentence_structures else 0,
            'comma_usage_consistency': round(comma_usage_consistency, 3) if sentence_structures else 0,
            'consistency_indicators': consistency_indicators,
            'consistency_ai_score': round(consistency_ai_score, 3)
        }

    def _calculate_ai_probability(self, linguistic, structural, vocabulary, pattern, consistency):
        """Calculate overall AI probability with weighted factors"""
        
        # Check for critical AI indicators first
        critical_ai_detected = False
        critical_ai_score = pattern.get('critical_ai_score', 0)
        
        if critical_ai_score > 0.3:  # Strong AI indicators found
            critical_ai_detected = True
        
        # Extract scores from each analysis
        scores = []
        weights = []
        
        # Pattern analysis gets higher weight if critical AI detected
        pattern_weight = 0.50 if critical_ai_detected else 0.25
        
        # Linguistic analysis (reduced weight if critical AI detected)
        if 'linguistic_ai_score' in linguistic:
            scores.append(linguistic['linguistic_ai_score'])
            weights.append(0.15 if critical_ai_detected else 0.25)
        
        # Structural analysis (reduced weight if critical AI detected)
        if 'structure_ai_score' in structural:
            scores.append(structural['structure_ai_score'])
            weights.append(0.10 if critical_ai_detected else 0.20)
        
        # Vocabulary analysis (reduced weight if critical AI detected)
        if 'vocabulary_ai_score' in vocabulary:
            scores.append(vocabulary['vocabulary_ai_score'])
            weights.append(0.15 if critical_ai_detected else 0.20)
        
        # Pattern analysis (increased weight if critical AI detected)
        if 'pattern_ai_score' in pattern:
            scores.append(pattern['pattern_ai_score'])
            weights.append(pattern_weight)
        
        # Consistency analysis (reduced weight if critical AI detected)
        if 'consistency_ai_score' in consistency:
            scores.append(consistency['consistency_ai_score'])
            weights.append(0.10 if critical_ai_detected else 0.10)
        
        # Calculate weighted average
        if scores and weights:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            ai_probability = sum(score * weight for score, weight in zip(scores, normalized_weights))
        else:
            ai_probability = 0.5  # Default neutral score
        
        # Apply minimum threshold if critical AI patterns detected
        if critical_ai_detected:
            ai_probability = max(0.70, ai_probability)
        
        return max(0.0, min(1.0, ai_probability))

    def _calculate_confidence(self, linguistic, structural, vocabulary, pattern, consistency):
        """Calculate confidence level in the AI detection"""
        
        # Factors that increase confidence
        confidence_factors = []
        
        # Text length factor
        if 'total_words' in vocabulary:
            word_count = vocabulary['total_words']
            if word_count > 500:
                confidence_factors.append(0.9)
            elif word_count > 200:
                confidence_factors.append(0.7)
            elif word_count > 100:
                confidence_factors.append(0.5)
            else:
                confidence_factors.append(0.3)
        
        # Pattern clarity factor
        if 'total_ai_patterns' in pattern and 'total_human_patterns' in pattern:
            total_patterns = pattern['total_ai_patterns'] + pattern['total_human_patterns']
            if total_patterns > 10:
                confidence_factors.append(0.8)
            elif total_patterns > 5:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.4)
        
        # Analysis completeness factor
        successful_analyses = sum(1 for analysis in [linguistic, structural, vocabulary, pattern, consistency] 
                                if not analysis.get('error'))
        completeness_factor = successful_analyses / 5
        confidence_factors.append(completeness_factor)
        
        # Calculate overall confidence
        if confidence_factors:
            confidence = np.mean(confidence_factors)
        else:
            confidence = 0.5
        
        return max(0.1, min(0.95, confidence))
    
    def _check_obvious_ai_indicators(self, text):
        """Check for obvious AI indicators that immediately classify content as AI-generated"""
        text_lower = text.lower()
        ai_score = 0.0
        
        # Emoji presence strongly contributes to AI score (in addition to early return above)
        try:
            if self._contains_emojis(text):
                ai_score += 0.5  # Strong boost
        except Exception:
            pass
        
        # Critical AI phrases that are dead giveaways
        critical_phrases = [
            'sure! here\'s',
            'certainly! here\'s', 
            'ai language model',
            'generated using ai',
            'this report has been generated using an ai',
            'language model based on',
            'ai-generated',
            'generated by artificial intelligence',
            'created by ai',
            'produced using ai'
        ]
        
        for phrase in critical_phrases:
            if phrase in text_lower:
                ai_score += 0.3  # Each critical phrase adds significant AI probability
        
        # AI disclaimer patterns
        disclaimer_patterns = [
            r'this.*generated.*ai.*model',
            r'information.*educational.*purposes.*only',
            r'should not be considered.*financial advice',
            r'consult.*sebi.*registered.*advisor',
            r'ai.*language.*model.*based on',
            r'generated using.*ai.*language.*model'
        ]
        
        for pattern in disclaimer_patterns:
            if re.search(pattern, text_lower):
                ai_score += 0.25
        
        # AI introduction patterns
        intro_patterns = [
            r'^\s*sure!\s*here',
            r'^\s*certainly!\s*here',
            r'^\s*of course!\s*here',
            r'i\'ll provide.*analysis',
            r'let me provide.*report',
            r'here\'s.*comprehensive.*analysis'
        ]
        
        for pattern in intro_patterns:
            if re.search(pattern, text_lower):
                ai_score += 0.2
        
        # Cap the score at 0.95
        return min(0.95, ai_score)

    def _contains_emojis(self, text: str) -> bool:
        """Return True if any emoji characters are present in the text."""
        if not text:
            return False
        return bool(self.emoji_pattern.search(text))

    def _classify_content(self, ai_probability, confidence):
        """Classify content based on AI probability and confidence"""
        
        if confidence < 0.3:
            return "Low Confidence - Insufficient Data"
        
        if ai_probability >= 0.75:
            return "Likely AI-Generated" if confidence >= 0.6 else "Possibly AI-Generated"
        elif ai_probability >= 0.55:
            return "Possibly AI-Generated" if confidence >= 0.5 else "Uncertain - Leaning AI"
        elif ai_probability >= 0.45:
            return "Uncertain - Mixed Signals"
        elif ai_probability >= 0.25:
            return "Possibly Human-Written" if confidence >= 0.5 else "Uncertain - Leaning Human"
        else:
            return "Likely Human-Written" if confidence >= 0.6 else "Possibly Human-Written"

    def _generate_explanation(self, ai_probability, linguistic, structural, pattern, consistency):
        """Generate human-readable explanation of the detection results"""
        
        explanations = []
        
        # Check for critical AI indicators first
        critical_ai_score = pattern.get('critical_ai_score', 0)
        ai_pattern_counts = pattern.get('ai_pattern_counts', {})
        
        # Critical AI pattern explanations
        if ai_pattern_counts.get('ai_disclaimers', 0) > 0:
            explanations.append("Contains AI-generated disclaimers or mentions of AI/language models.")
        
        if ai_pattern_counts.get('ai_introductions', 0) > 0:
            explanations.append("Uses typical AI introduction phrases like 'Sure! Here's' or 'I'll provide'.")
        
        if ai_pattern_counts.get('ai_hedging_strong', 0) > 0:
            explanations.append("Shows strong AI hedging patterns with phrases like 'based on available data'.")
        
        # AI probability interpretation
        if ai_probability >= 0.8:
            explanations.append("Strong indicators of AI generation detected.")
        elif ai_probability >= 0.6:
            explanations.append("Moderate indicators of AI generation present.")
        elif ai_probability >= 0.4:
            explanations.append("Mixed signals - could be either AI or human.")
        elif ai_probability >= 0.2:
            explanations.append("Moderate indicators of human writing present.")
        else:
            explanations.append("Strong indicators of human writing detected.")
        
        # Specific pattern explanations
        if 'pattern_ai_score' in pattern:
            if pattern['pattern_ai_score'] > 0.7:
                explanations.append("High usage of AI-typical phrases and transitions.")
            elif pattern['total_human_patterns'] > pattern['total_ai_patterns']:
                explanations.append("Contains more human-like expressions and personal language.")
        
        # Weighted score explanation
        if pattern.get('ai_weighted_score', 0) > 20:
            explanations.append("High weighted AI pattern score indicates strong AI characteristics.")
        
        # Linguistic explanations
        if 'linguistic_ai_score' in linguistic:
            if linguistic['linguistic_ai_score'] > 0.7:
                explanations.append("Writing shows consistent structure typical of AI generation.")
            elif linguistic.get('type_token_ratio', 0) > 0.7:
                explanations.append("High vocabulary diversity suggests human creativity.")
        
        # Structural explanations
        if 'structure_ai_score' in structural:
            if structural['structure_ai_score'] > 0.7:
                explanations.append("Text structure is highly organized and formal.")
            elif structural.get('transition_density', 0) < 0.2:
                explanations.append("Natural flow with fewer formal transitions suggests human writing.")
        
        return " ".join(explanations) if explanations else "Analysis completed with mixed results."

    def batch_analyze(self, texts):
        """Analyze multiple texts and return batch results"""
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.detect_ai_content(text)
                result['text_id'] = i
                result['text_preview'] = text[:100] + "..." if len(text) > 100 else text
                results.append(result)
            except Exception as e:
                results.append({
                    'text_id': i,
                    'error': str(e),
                    'ai_probability': 0.5,
                    'confidence': 0.1,
                    'classification': 'Analysis Failed'
                })
        
        # Batch summary
        successful_analyses = [r for r in results if 'error' not in r]
        if successful_analyses:
            avg_ai_probability = np.mean([r['ai_probability'] for r in successful_analyses])
            avg_confidence = np.mean([r['confidence'] for r in successful_analyses])
            
            batch_summary = {
                'total_texts': len(texts),
                'successful_analyses': len(successful_analyses),
                'failed_analyses': len(results) - len(successful_analyses),
                'average_ai_probability': round(avg_ai_probability, 3),
                'average_confidence': round(avg_confidence, 3),
                'likely_ai_count': sum(1 for r in successful_analyses if r['ai_probability'] >= 0.6),
                'likely_human_count': sum(1 for r in successful_analyses if r['ai_probability'] <= 0.4),
                'uncertain_count': sum(1 for r in successful_analyses if 0.4 < r['ai_probability'] < 0.6)
            }
        else:
            batch_summary = {
                'total_texts': len(texts),
                'successful_analyses': 0,
                'failed_analyses': len(texts),
                'error': 'All analyses failed'
            }
        
        return {
            'results': results,
            'batch_summary': batch_summary,
            'timestamp': datetime.utcnow().isoformat()
        }