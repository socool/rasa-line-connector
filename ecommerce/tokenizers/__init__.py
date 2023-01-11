from ecommerce.common import NotInstalled


try:
    from ecommerce.tokenizers.thai_tokenizer import ThaiTokenizer
except ImportError:
    ThaiTokenizer = NotInstalled("ThaiTokenizer", "thai")

try:
    from ecommerce.tokenizers.blankspacy import BlankSpacyTokenizer
except ImportError:
    BlankSpacyTokenizer = NotInstalled("BlankSpacyTokenizer", "rasa[spacy]")


__all__ = ["ThaiTokenizer", "BlankSpacyTokenizer"]