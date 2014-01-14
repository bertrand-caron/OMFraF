import json


fragments = {
  'fragments': [
    {
      'atoms': [
        {
          'id': 1,
          'charge': 0.123
        },
        {
          'id': 2,
          'charge': 0.223
        },
        {
          'id': 3,
          'charge': 0.323
        },
      ]
    },
    {
      'atoms': [
        {
          'id': 1,
          'charge': 0.423
        },
        {
          'id': 2,
          'charge': 0.523
        },
      ]
    },
    {
      'atoms': [
        {
          'id': 1,
          'charge': 0.623
        },
        {
          'id': 3,
          'charge': 0.723
        },
      ]
    }
  ]
}

print json.dumps(fragments)
