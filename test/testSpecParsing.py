# vim: set fileencoding=utf-8 :

import sys
sys.path.append('..')

from SomethingToLookup import SpecParser
import unittest;

class SpecParserTestCase(unittest.TestCase):
  def setUp(self):
    self.parser = SpecParser()

  def tearDown(self):
    self.parser = None
  
  def testTagOk(self, str, expected):
    result = self.parser.parseTag(str)
    assert result is not None, 'Failed to parse tag "%s"' % str

    self.assertEqual(len(result), 5,
                      'Unexpected number of elements in result')
    self.verifyLookup(result, expected)

  def testTagNotOk(self, str):
    result = self.parser.parseTag(str)
    assert result == None, 'Failed to reject tag ' + str

  def testTemplateOk(self, str, expected):
    result = self.parser.parseTemplate(str)
    assert result is not None, 'Failed to parse "%s"' % str
    self.assertEqual(len(result), len(expected), 'Unexpected number of matches')

    expectedIter = iter(expected)
    for actual in result:
      expect = expectedIter.next()
      assert isinstance(actual, dict), 'Unexpected type for result'
      self.assertEqual(len(actual), 6,
                        'Unexpected number of elements in result')
      self.assertEqual(actual['tag'], expect[0], 'Tag does not match')
      self.verifyLookup(actual, expect[1:])

  def testTemplateNotOk(self, str):
    result = self.parser.parseTemplate(str)
    assert result == None, 'Failed to reject ' + str

  def verifyLookup(self, lookup, expected):
    self.assertEqual(lookup['deck'], expected[0], 'Deck name does not match')
    self.assertEqual(lookup['template'], expected[1],
                      'Template name does not match')
    self.assertEqual(lookup['field'], expected[2], 'Field name does not match')
    match = expected[3] if len(expected) >= 4 else SpecParser.MatchWhole
    self.assertEqual(lookup['match'], match, 'Match type does not match')
    delim = expected[4] if len(expected) >= 5 else None
    self.assertEqual(lookup['delim'], delim, 'Delimter type does not match')

  def runTest(self):
    self.testTagParsing()
    self.testTemplateParsing()

  def testTagParsing(self):
    # Simple case
    self.testTagOk(u"lookup:Deck/Template,by:Field",
      [u"Deck", u"Template", u"Field"])

    # Test deck
    self.testTagNotOk(u"lookup: /Template,by:Field")
    self.testTagNotOk(u"lookup:  /Template,by:Field")
    self.testTagNotOk(u"lookup:/Template,by:Field")
    self.testTagNotOk(u"lookup:\\ /Template,by:Field")
    self.testTagNotOk(u"lookup:\\ \\ /Template,by:Field")
    self.testTagNotOk(u"lookup: \\ /Template,by:Field")
    self.testTagOk(u"lookup:a/Template,by:Field",
      [u"a", u"Template", u"Field"])
    self.testTagOk(u"lookup: a/Template,by:Field",
      [u"a", u"Template", u"Field"])
    self.testTagOk(u"lookup:a /Template,by:Field",
      [u"a", u"Template", u"Field"])
    self.testTagOk(u"lookup: a /Template,by:Field",
      [u"a", u"Template", u"Field"])
    self.testTagOk(u"lookup: a b /Template,by:Field",
      [u"a b", u"Template", u"Field"])
    self.testTagOk(u"lookup:\\a/Template,by:Field",
      [u"a", u"Template", u"Field"])
    self.testTagOk(u"lookup:Deck\\/Template/Template,by:Field",
      [u"Deck/Template", u"Template", u"Field"])
    self.testTagOk(u"lookup:Deck\\\\/Template,by:Field",
      [u"Deck\\", u"Template", u"Field"])
    self.testTagOk(u"lookup:\\\\ /Template,by:Field",
      [u"\\", u"Template", u"Field"])

    # Test template
    self.testTagNotOk(u"lookup:Deck/,by:Field")
    self.testTagNotOk(u"lookup:Deck/ ,by:Field")
    self.testTagNotOk(u"lookup:Deck/  ,by:Field")
    self.testTagNotOk(u"lookup:Deck/\\,by:Field")
    self.testTagNotOk(u"lookup:Deck/ \\,by:Field")
    self.testTagNotOk(u"lookup:Deck/\\ ,by:Field")
    self.testTagNotOk(u"lookup:Deck/\\ \\ ,by:Field")
    self.testTagNotOk(u"lookup:Deck/ \\ ,by:Field")
    self.testTagOk(u"lookup:Deck/a,by:Field", [u"Deck", u"a", u"Field"])
    self.testTagOk(u"lookup:Deck/ a,by:Field", [u"Deck", u"a", u"Field"])
    self.testTagOk(u"lookup:Deck/a ,by:Field", [u"Deck", u"a", u"Field"])
    self.testTagOk(u"lookup:Deck/ a ,by:Field", [u"Deck", u"a", u"Field"])
    self.testTagOk(u"lookup:Deck/ a b ,by:Field", [u"Deck", u"a b", u"Field"])
    self.testTagOk(u"lookup:Deck/\\a,by:Field", [u"Deck", u"a", u"Field"])
    self.testTagOk(u"lookup:Deck/a,b,by:Field", [u"Deck", u"a,b", u"Field"])
    self.testTagOk(u"lookup:Deck/a\\,b,by:Field", [u"Deck", u"a,b", u"Field"])
    self.testTagOk(u"lookup:Deck/a\\,,by:Field", [u"Deck", u"a,", u"Field"])
    self.testTagOk(u"lookup:Deck/\\\\,by:Field", [u"Deck", u"\\", u"Field"])

    # Test optional templates
    self.testTagOk(u"lookup:Deck,by:Field", [u"Deck", None, u"Field"])
    self.testTagOk(u"lookup:Deck\\/,by:Field", [u"Deck/", None, u"Field"])
    self.testTagOk(u"lookup:Deck  ,by:Field", [u"Deck", None, u"Field"])
    self.testTagOk(u"lookup:\\/Template,by:Field",
      ["/Template", None, u"Field"])
    self.testTagOk(u"lookup: \\/Template,by:Field",
      ["/Template", None, u"Field"])
    self.testTagOk(u"lookup:a\\/Template,by:Field",
      ["a/Template", None, u"Field"])

    # Test field
    self.testTagNotOk(u"lookup:Deck/Template,by:")
    self.testTagNotOk(u"lookup:Deck/Template,by: ")
    self.testTagNotOk(u"lookup:Deck/Template,by:  ")
    self.testTagNotOk(u"lookup:Deck/Template,by:\\")
    self.testTagOk(u"lookup:Deck/Template,by:a", [u"Deck", u"Template", u"a"])
    self.testTagOk(u"lookup:Deck/Template,by: a ", [u"Deck", u"Template", u"a"])
    self.testTagOk(u"lookup:Deck/Template,by:\\a", [u"Deck", u"Template", u"a"])

    # Test matching/delimeter
    self.testTagOk(u"lookup:Deck/Template,by:a,match:char",
        [u"Deck", u"Template", u"a", SpecParser.MatchByChar])
    self.testTagOk(u"lookup:Deck/Template,by:a , match: char  ",
        [u"Deck", u"Template", u"a", SpecParser.MatchByChar])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:abc",
        [u"Deck", u"Template", u"a", SpecParser.MatchWhole])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:kanji",
        [u"Deck", u"Template", u"a", SpecParser.MatchByKanji])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:delim:ab",
        [u"Deck", u"Template", u"a", SpecParser.MatchByDelim, u"ab"])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:delim: ab ",
        [u"Deck", u"Template", u"a", SpecParser.MatchByDelim, u"ab"])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:delim: \\\\ ",
        [u"Deck", u"Template", u"a", SpecParser.MatchByDelim, u"\\"])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:delim:,",
        [u"Deck", u"Template", u"a", SpecParser.MatchByDelim, u","])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:delim:a b",
        [u"Deck", u"Template", u"a", SpecParser.MatchByDelim, u"a b"])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:  ",
        [u"Deck", u"Template", u"a", SpecParser.MatchWhole])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:",
        [u"Deck", u"Template", u"a", SpecParser.MatchWhole])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:delim:",
        [u"Deck", u"Template", u"a", SpecParser.MatchWhole])
    self.testTagOk(u"lookup:Deck/Template,by:a,match:delim",
        [u"Deck", u"Template", u"a", SpecParser.MatchWhole])

    # Escaping curly brace
    self.testTagOk(u"lookup:Deck\\}Template,by:Field",
      [u"Deck}Template", None, u"Field"])
    self.testTagOk(u"lookup:Deck\\}Template/Template,by:Field",
      [u"Deck}Template", u"Template", u"Field"])
    self.testTagOk(u"lookup:Deck/Template\\}Template,by:Field",
      [u"Deck", u"Template}Template", u"Field"])

    # Other escapes
    self.testTagOk(u"lookup:Deck\\Tem\plate/Templat\e,by:\\:Fi\\eld",
      [u"DeckTemplate", u"Template", u":Field"])

    # Unicode
    self.testTagOk(u"lookup:デック/テンプレート,by:フィールド,match:delim:・",
      [u"デック", u"テンプレート", u"フィールド",
       SpecParser.MatchByDelim, u"・"])

    # Nothing at all
    self.testTagNotOk(u"")
    self.testTagNotOk(u" ")
    self.testTagNotOk(u"abc")

  def testTemplateParsing(self):
    # Simple case
    self.testTemplateOk(u"{{lookup:Deck/Template,by:Field}}",
      [[u"lookup:Deck/Template,by:Field", u"Deck", u"Template", u"Field"]])

    # Extra brace
    self.testTemplateOk(u"{{{lookup:Deck/Template,by:Field}}}",
      [[u"lookup:Deck/Template,by:Field", u"Deck", u"Template", u"Field"]])

    # Ignore surrounding text
    self.testTemplateOk(u"asdf {{lookup:Deck/Template,by:Field}} adsfasd",
      [[u"lookup:Deck/Template,by:Field", u"Deck", u"Template", u"Field"]])

    # Multiple specs
    twoDecks = \
      [[u"lookup:Deck/Template,by:Field", u"Deck", u"Template", u"Field"],
      [u"lookup:Deck2/Template2,by:Field2", u"Deck2", u"Template2", u"Field2"]]
    self.testTemplateOk(u"asdf " \
      "{{lookup:Deck/Template,by:Field}}{{lookup:Deck2/Template2,by:Field2}} " \
      "adsfasd", twoDecks)
    self.testTemplateOk(u"asdf " \
      "{{lookup:Deck/Template,by:Field}} {{lookup:Deck2/Template2," \
      "by:Field2}} adsfasd", twoDecks)
    self.testTemplateOk(u"asdf " \
      "{{lookup:Deck/Template,by:Field}}abasdf{{lookup:Deck2/Template2," \
      "by:Field2}} adsfasd", twoDecks)
    self.testTemplateOk(u"asdf " \
      "{{lookup:Deck/Template,by:Field}}{{otherField}}{{lookup:" \
      "Deck2/Template2,by:Field2}} adsfasd", twoDecks)
    self.testTemplateOk(u"asdf " \
      "{{lookup:Deck/Template,by:Field}}\r\n{{otherField}}{{lookup:" \
      "Deck2/Template2,by:Field2}} adsfasd", twoDecks)
    self.testTemplateOk(u"asdf " \
      "{{lookup:\nDeck/Template,by:Field}}\r\n{{otherField}}{{lookup:" \
      "Deck2/Template2,by:Field2}} adsfasd",
      [[u"lookup:\nDeck/Template,by:Field", u"Deck", u"Template", u"Field"],
      [u"lookup:Deck2/Template2,by:Field2", u"Deck2", u"Template2", u"Field2"]])

    # First deck is in error
    self.testTemplateOk(u"asdf " \
      "{{lookup:Deck/Template,by:}}\r\n{{otherField}}{{lookup:" \
      "Deck2/Template2,by:Field2}} adsfasd",
      [[u"lookup:Deck2/Template2,by:Field2", u"Deck2", u"Template2", u"Field2"]]
      )

    # Nothing at all
    self.testTemplateNotOk(u"")
    self.testTemplateNotOk(u" ")
    self.testTemplateNotOk(u"abc")

specParserTests = SpecParserTestCase()
runner = unittest.TextTestRunner()
runner.run(specParserTests)
