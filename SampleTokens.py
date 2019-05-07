from Lexer import Token, TokenRegistry

class NumberToken(Token):

	identifiers = "1234567890.,"

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

class OperatorToken(Token):

	identifiers = "+-/*=^"

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

ArithmeticRegistry = TokenRegistry([NumberToken, OperatorToken])