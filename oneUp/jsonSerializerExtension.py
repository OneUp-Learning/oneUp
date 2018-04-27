import json
import decimal

# Simple extended encoder.  Just calls the super method for everything but Decimals
class OneUpExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return {
                "__oneUp_extended_type": "decimal",
                "value": str(obj)
            }
        return super(OneUpExtendedJSONEncoder, self).default(obj)
    
# Simple extended decoded.  Works normally except that there's an object hook which
# checks for objects with our special key __oneUp_extended_type in them and if those
# objects are decimals, then makes actual decimal.Decimals out of them.
# Everything else gets treated in the default manner.
class OneUpExtendedJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '__oneUp_extended_type' not in obj:
            return obj
        typename = obj['__oneUp_extended_type']
        if typename == 'decimal':
            return decimal.Decimal(obj['value'])
        return obj

# Class with needed interface for Django Serializer.
# Really just wraps up native Python JSON library with extra hooks.
class OneUpExtendedJSONSerializer():
    def dumps(self, obj):
        print("Session Object dump:"+json.dumps(obj, cls=OneUpExtendedJSONEncoder))
        return str.encode(json.dumps(obj, cls=OneUpExtendedJSONEncoder))
    def loads(self, data):
        print("\n\nSession data dump:"+str(data))
        obj= json.loads(data.decode('utf-8'), cls=OneUpExtendedJSONDecoder)
        print("Session data object dump:"+json.dumps(obj, cls=OneUpExtendedJSONEncoder))
        print("\n\n")
        return obj
    