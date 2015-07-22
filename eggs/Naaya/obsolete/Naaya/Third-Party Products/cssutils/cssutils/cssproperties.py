"""
Property

TODO:
    Properties should implements DOM Level 2 CSSStyleDeclaration

    return computed values and not literal values
    simplify unit pairs/triples/quadruples  2px 2px 2px 2px
                                    ->      2px for border/padding...
    normalize compound properties like:     background: no-repeat left url()  #fff
                                    ->      background: #fff url() no-repeat left     
"""
__version__ = u'0.41'

import xml.dom 

import cssutils
import cssvalue


class Property(object):
    "(cssutils) a property of a StyleDeclaration"

    _PAGED_MEDIA_MODULE = []
    _RUBY_MODULE = []
    _GENERAL_AND_REPLACED_CONTENT_MODULE = [u'quotes', u'content', u'counter-increment', u'counter-reset'] # u'display'
    _BASIC_UI_MODULE = [u'cursor']# ...        
    _TEXT_MODULE = [u'direction', u'text-align', u'text-decoration', u'text-indent', u'text-shadow', u'text-transform', u'unicode-bidi', 
        u'letter-spacing', u'word-spacing', u'white-space'
        ]
    _FONT_MODULE = [u'font', u'font-style', u'font-variant', u'font-weight', u'font-size', u'font-size-adjust', u'font-family',
        u'font-stretch' 
        ]
    _LINE_MODULE = [u'line-height', u'vertical-align'] # ... text-height ...
    _LIST_MODULE = [u'list-style', u'list-style-type', u'list-style-image', u'list-style-position']
    # other properties
    _PRINT_PROFILE = [u'clip', u'position', u'right', u'left', u'top', u'bottom', u'z-index',        
        u'caption-side', u'table-layout', u'empty-cells', u'border-collapse', u'border-spacing']
    _COLOR_MODULE = [u'color', u'opacity'] # ... @color-profile u'color-profile', u'rendering-intent'
    _BACKGROUNDS_MODULE = [u'background', u'background-color', u'background-image', u'background-repeat', u'background-attachment', u'background-position']
    _BOX_MODEL_MODULE = [u'display', u'visibility', u'float', u'clear',
        u'overflow', u'overflow-x', u'overflow-y',
        u'width', u'height', u'max-height', u'max-width', u'min-height', u'min-width',
        u'padding', u'padding-top', u'padding-right', u'padding-bottom', u'padding-left',
        u'margin', u'margin-top', u'margin-right', u'margin-bottom', u'margin-left'
        ]
    _BORDER_MODULE = [u'border', u'border-top', u'border-right', u'border-bottom', u'border-left',
        u'border-color', u'border-top-color', u'border-right-color', u'border-bottom-color', u'border-left-color',
        u'border-style', u'border-top-style', u'border-right-style', u'border-bottom-style', u'border-left-style',
        u'border-width', u'border-top-width', u'border-right-width', u'border-bottom-width', u'border-left-width',
        ]
    _properties = []
    _properties.extend(_BASIC_UI_MODULE)
    _properties.extend(_TEXT_MODULE)
    _properties.extend(_FONT_MODULE)
    _properties.extend(_LINE_MODULE)
    _properties.extend(_LIST_MODULE)
    _properties.extend(_PRINT_PROFILE)
    _properties.extend(_COLOR_MODULE)
    _properties.extend(_BACKGROUNDS_MODULE)
    _properties.extend(_BOX_MODEL_MODULE)
    _properties.extend(_BORDER_MODULE)
    
    def __init__(self, name, value, priority=''):
        "name and value must be given, priority is optional (may be u'important')"
        # normalize
        name = u' u'.join(name.split())

        # valid?        
        if name not in self._properties:
            raise xml.dom.SyntaxErr('"%s" is not a recognized Property.' % name)
        
        self._name = name
        self._value = cssvalue.Value(value)
        self._priority = priority

    def getName(self):
        return self._name

    def getValue(self):
        return self._value.cssText

    def getCSSValue(self):
        return self._value

    def getPriority(self):
        return self._priority

    def _getFormatted(self):
        prio = self._priority
        if prio == u'important':
            prio = u' !' + prio
        return u'%s: %s%s;' % (self._name, self._value.cssText, prio)

    cssText = property(_getFormatted, doc='readonly string representation of this property')


