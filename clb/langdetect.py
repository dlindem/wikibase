from lingua import Language, LanguageDetectorBuilder
languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH, Language.CZECH, Language.POLISH]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

wikilang = {
None: None,
Language.ENGLISH: 'en',
Language.FRENCH: 'fr',
Language.GERMAN: 'de',
Language.SPANISH: 'de',
Language.CZECH: 'cs',
Language.POLISH: 'pl'
}

def langdetect(text):
	return wikilang[detector.detect_language_of(text)]
