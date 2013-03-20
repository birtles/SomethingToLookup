from anki.utils import stripHTML
from anki.hooks import addHook
from anki.template.template import get_or_attr
import re

class KeyedException(Exception):
  def __init__(self, key, detail=None):
    self.key    = key
    self.detail = detail
  def __str__(self):
    return "%s: %s" & (repr(self.value), repr(self.detail))

def lookup(tag, context):
  # Parse the tag
  parser = SpecParser()
  result = parser.parseTag(tag)
  if result is None:
    raise KeyedException('failed-parse', tag)

  # Look up the field to match on
  key = get_or_attr(context, result['field'], None)
  if key is None:
    raise KeyedException('field-not-found', result['field'])

  # Sanitize field contents
  key = stripHTML(key).strip()
  if not len(key):
    raise KeyedException('field-empty', result['field'])
  return key

def render(txt, extra, context, tag, tag_name):
  try:
    result = lookup(tag_name, context)
  except KeyedException as e:
    if e.key == 'failed-parse':
      # XXX In future just make this the empty string
      # For now however, something more descriptive is useful for debugging
      result = "Failed to parse lookup"
    elif e.key == 'field-not-found':
      result = "'%s' not found" % e.detail
    elif e.key == 'field-empty':
      # XXX This should probably fail silently too
      result = "'%s' is empty" % e.detail
    else:
      result = "Unknown error: %s" % e
  return result

addHook('fmod_lookup', render)

class SpecParser:
  """Parser for deck import specs.

  Format is {{lookup:<Deck>[/<Template>],by:<Field>[,match:<DelimType>]}}
  where <DelimType> = whole|char|kanji|(delim:<str>)"""

  # Delimeter types
  MatchWhole, MatchByChar, MatchByKanji, MatchByDelim = range(4)

  # Compiled regular expressions
  lookup_re = None
  delim_re  = None
  tag_re    = None

  def __init__(self):
    lookup = r"lookup:\s*" \
             r"(?P<deck>([^/]|\\/)*?(?<!\\)(?:\\\\)*)" \
             r"\s*(?:/\s*(?P<template>.*?(?<!\\)(?:\\\\)*))?" \
             r"\s*,\s*by:\s*(?P<field>.*?[^\s\\\\])\s*" \
             r"\s*(?:,\s*match:(?P<match>.*?))?\s*$"
    self.lookup_re = re.compile(lookup)

    delim = r"\s*delim:\s*(?P<type>.+)\s*$"
    self.delim_re = re.compile(delim)

    tag_delims = { 'open': re.escape('{{'), 'close': re.escape('}}') }
    tag = r"%(open)s(?:\{)?\s*(lookup:.+?)\1?%(close)s+"
    self.tag_re = re.compile(tag % tag_delims, re.DOTALL)

  def parseTag(self, tag):
    """Parse a tag name and return a parsed lookup specification
    
    Returns a dict objects with elements
      {virtualField, deck, template, field, delimType, delim}
      where delimType is one of
        SpecParser.MatchWhole,MatchByChar,MatchByKanji,MatchByDelim
    or None if tag is not a valid lookup specification"""

    match = self.lookup_re.match(tag)
    if match is None:
      return None

    groupdict = match.groupdict()

    # Tidy up the results
    result = {}
    result['deck']         = self.stripslashes(groupdict['deck']).strip()
    result['template']     = self.stripslashes(groupdict['template']).strip() \
                             if groupdict['template'] is not None else None
    result['field']        = self.stripslashes(groupdict['field']).strip()

    # If deck, template, or field is an empty string it's not valid
    if not len(result['deck']) or \
       (result['template'] is not None and not len(result['template'])) or \
       not len(result['field']):
        return None

    # Process match portion
    result['delim'] = None
    if groupdict['match'] is None:
      result['match'] = SpecParser.MatchWhole
    else:
      match_str = self.stripslashes(groupdict['match']).strip()
      if match_str == 'char':
        result['match'] = SpecParser.MatchByChar
      elif match_str == 'kanji':
        result['match'] = SpecParser.MatchByKanji
      else:
        # Grr... Python doesn't allow assignment inside a conditional
        match = self.delim_re.match(match_str)
        if match is not None:
          result['match'] = SpecParser.MatchByDelim
          result['delim'] = match.groupdict()['type']
        else:
          result['match'] = SpecParser.MatchWhole

    return result

  def parseTemplate(self, template):
    """Parse a template and return a list of lookup specifications.
    
    Returns an array of dict objects with elements
      {tag, deck, template, field, delimType, delim}
      where delimType is one of
        SpecParser.MatchWhole,MatchByChar,MatchByKanji,MatchByDelim
    or None if no lookup specifications were found"""

    pos = 0
    result = []
    while 1:
      match = self.tag_re.search(template, pos)
      if match is None:
        break

      pos = match.end()
      tag = match.group(1)

      fields = self.parseTag(tag)
      if fields is None:
        continue

      params = {}
      params['tag'] = tag
      params.update(fields);

      result.append(params)

    return result if len(result) else None

  def stripslashes(self, str):
    return re.sub(r"\\(.)", r"\1", str)
