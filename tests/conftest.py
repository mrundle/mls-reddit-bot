import sys
from unittest import mock

# really dumb mock-outs for now
sys.modules['boto3'] = mock.MagicMock()
sys.modules['botocore'] = mock.MagicMock()
sys.modules['botocore.exceptions'] = mock.MagicMock()
