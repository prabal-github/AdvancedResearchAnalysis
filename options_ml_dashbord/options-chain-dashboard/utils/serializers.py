from marshmallow import Schema, fields

class OptionChainSerializer(Schema):
    id = fields.Int(required=True)
    symbol = fields.Str(required=True)
    strike_price = fields.Float(required=True)
    expiration_date = fields.Date(required=True)
    option_type = fields.Str(required=True)  # Call or Put
    last_price = fields.Float(required=True)
    bid = fields.Float(required=True)
    ask = fields.Float(required=True)
    volume = fields.Int(required=True)
    open_interest = fields.Int(required=True)
    implied_volatility = fields.Float(required=True)

class OptionDetailSerializer(Schema):
    id = fields.Int(required=True)
    symbol = fields.Str(required=True)
    strike_price = fields.Float(required=True)
    expiration_date = fields.Date(required=True)
    option_type = fields.Str(required=True)  # Call or Put
    last_price = fields.Float(required=True)
    bid = fields.Float(required=True)
    ask = fields.Float(required=True)
    volume = fields.Int(required=True)
    open_interest = fields.Int(required=True)
    implied_volatility = fields.Float(required=True)
    delta = fields.Float(required=True)
    gamma = fields.Float(required=True)
    theta = fields.Float(required=True)
    vega = fields.Float(required=True)
    rho = fields.Float(required=True)

class OptionsAnalysisSerializer(Schema):
    symbol = fields.Str(required=True)
    analysis = fields.Dict(required=True)  # Detailed analysis results
    recommendations = fields.List(fields.Str())  # List of recommendations based on analysis