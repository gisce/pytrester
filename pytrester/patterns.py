PATTERNS = [
    (r'^import StringIO$', 'from six.moves import StringIO'),
    (r'^from StringIO import StringIO$', 'from six.moves import StringIO'),
    (r'StringIO.StringIO\(\)', 'StringIO()'),
    (r'^import mock', '''import six
if six.PY2:
    import mock
else:
    from unittest import mock''')
]
