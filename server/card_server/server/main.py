"""
run uvicorn main:app in terminal to run main.py
"""
from Card.use_cases.main import UseCases as cases
from Card.entity.card_types import CardType
from gen_util.error_type import ErrorType
from ariadne import QueryType, MutationType, gql, make_executable_schema
from ariadne.asgi import GraphQL

cases = cases()

type_defs = gql("""
    type Error {
        field: String
        message: String
    }

    input CardInput {
        inside: Int
        mid: Int
        three: Int
        passing: Int
        steal: Int
        block: Int
        accountID: Int
        filename: String
    }

    type CardOutput {
        id: Int
        inside: Int
        mid: Int
        three: Int
        passing: Int
        steal: Int
        block: Int
        accountID: Int
        imgURL: String
    }

    type GQLOutput {
        errors: [Error]
        cards: [CardOutput]
    }

    type Query {
        getAll: GQLOutput!
        getOne(id: Int): GQLOutput!
    }

    type Mutation {
        createCard(card: CardInput!): GQLOutput!
        deleteCard(id: Int): GQLOutput!
    }
    
""")

# Map resolver functions to Query fields using QueryType
query = QueryType()
mutation = MutationType()


@query.field("getAll")
def resolve_get_all(*_):
    res = cases.get_all_cards_case()

    class CardObj():
        def __init__(self, id, account_id, inside, mid, three, passing, steal, block, img_url=None):
            self.id = id
            self.accountID = account_id
            self.inside = inside
            self.mid = mid
            self.three = three
            self.passing = passing
            self.steal = steal
            self.block = block
            self.imgURL = img_url

    cards = []

    for card in res.response:
        cards.append(CardObj(
            id=card[0],
            inside=card[1],
            mid=card[2],
            three=card[3],
            passing=card[4],
            steal=card[5],
            block=card[6],
            img_url=card[7],
            account_id=card[8]
        ))

    return {"cards": cards, "errors": None}


@query.field("getOne")
def resolve_get_one(*_, id):
    res = cases.get_one_card_case(id)

    class CardObj():
        def __init__(self, id, account_id, inside, mid, three, passing, steal, block, img_url=None):
            self.id = id
            self.accountID = account_id
            self.inside = inside
            self.mid = mid
            self.three = three
            self.passing = passing
            self.steal = steal
            self.block = block
            self.imgURL = img_url

    if len(res.response) == 0:
        field = "getOne query"
        message = "ID is not valid"
        error = ErrorType(field=field, message=message)
        return {"cards": None, "errors": [error]}

    card = CardObj(
        id=res.response[0][0],
        inside=res.response[0][1],
        mid=res.response[0][2],
        three=res.response[0][3],
        passing=res.response[0][4],
        steal=res.response[0][5],
        block=res.response[0][6],
        account_id=res.response[0][8],
        img_url=res.response[0][7]
    )

    return {"cards": [card], "errors": None}


@mutation.field("deleteCard")
def resolve_delete_card(*_, id):
    class CardObj():
        def __init__(self, id, account_id, inside, mid, three, passing, steal, block, img_url=None):
            self.id = id
            self.accountID = account_id
            self.inside = inside
            self.mid = mid
            self.three = three
            self.passing = passing
            self.steal = steal
            self.block = block
            self.imgURL = img_url

    res = cases.delete_card_case(id)

    if len(res.response) == 0:
        field = "deleteCard query"
        message = "ID is not valid"
        error = ErrorType(field=field, message=message)
        return {"cards": None, "errors": [error]}

    card = CardObj(
        id=res.response[0][0],
        inside=res.response[0][1],
        mid=res.response[0][2],
        three=res.response[0][3],
        passing=res.response[0][4],
        steal=res.response[0][5],
        block=res.response[0][6],
        account_id=res.response[0][8],
        img_url='xxDeletedxx'
    )

    return {"cards": [card], "errors": None}


@mutation.field("createCard")
def resolve_create_card(*_, card):
    class CardObj():
        def __init__(self, account_id, inside, mid, three, passing, steal, block, id=None, img_url=None):
            self.id = id
            self.accountID = account_id
            self.inside = inside
            self.mid = mid
            self.three = three
            self.passing = passing
            self.steal = steal
            self.block = block
            self.imgURL = img_url

    res = cases.create_card_case(
        account_id=card['accountID'],
        inside=card['inside'],
        mid=card['mid'],
        three=card['three'],
        passing=card['passing'],
        steal=card['steal'],
        block=card['block'],
        filename=card['filename']
    )

    if res.errors:
        errors = []
        for error in res.errors:
            error = ErrorType(field=error.field, message=error.message)
            errors.append(error)
        return {"cards": None, "errors": errors}
    
    returned_card = CardObj(
        account_id=card['accountID'],
        inside=card['inside'],
        mid=card['mid'],
        three=card['three'],
        passing=card['passing'],
        steal=card['steal'],
        block=card['block'],
        img_url='https://sports-trader-card-images.s3.us-east-2.amazonaws.com/{filename}'.format(filename=card['filename'])
    )

    return {"cards": [returned_card], "errors": None}


schema = make_executable_schema(type_defs, [query, mutation])
app = GraphQL(schema, debug=True)

