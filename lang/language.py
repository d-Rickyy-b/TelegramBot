__author__ = 'Rico'
import codecs
import configparser

translations = configparser.ConfigParser()
translations.read_file(codecs.open("lang/translations.ini", "r", "UTF-8"))


# translation returns the translation for a specific string
def translation(string, language):
    if language in translations and string in translations[language]:
        return translations[language][string]
    elif language == "br":
        # TODO remove this part. New users should have pt_BR as lang_id
        return translations["pt_BR"][string]
    elif "en" in translations and string in translations["en"]:
        return translations["en"][string]
    return string
