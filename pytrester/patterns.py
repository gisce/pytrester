PATTERNS = [
    (r'^import StringIO$', 'from six.moves import StringIO'),
    (r'^from StringIO import StringIO$', 'from six.moves import StringIO'),
    (r'StringIO.StringIO\(\)', 'StringIO()'),
    (r'^import mock', '''import six
if six.PY2:
    import mock
else:
    from unittest import mock'''),
    (r'import xmlrpclib$', 'from six.moves import xmlrpc_client as xmlrpclib'),
    ('^try:\n    import cStringIO as StringIO\nexcept ImportError:\n    import StringIO',
         'from six.moves import StringIO'),
]
