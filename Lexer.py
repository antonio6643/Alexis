from datetime import datetime
import Stick

DebugName = str(datetime.now().strftime("%Y-%m-%d  %H.%M.%S"))

class Token:
	def __init__(self, lineNumber: int, columnNumber: int, truePosition: int, data: str):
		self.line = lineNumber
		self.column = columnNumber
		self.truePosition = truePosition
		self.data = data # TODO: Data validation(don't want tokens with the wrong type)
	
	@classmethod
	def isValidCharacter(cls, char: str): # Can be overridden
		if char in cls.identifiers:
			return True
		return False

	def __repr__(self):
		return "({0}, {1})".format(self.__class__.__name__, self.data)

class TokenRegistry:
	def __init__(self, rawRegistry):
		self.tokenTypes = rawRegistry

	def classifyCharacter(self, char: str):
		for t in self.tokenTypes:
			if t.isValidCharacter(char):
				return t # The idea is that I can just order it in the code. Saves some steps. :)
		return None

class Buffer: # TODO: Process the token data since a string would have the data with the quotations
	def __init__(self, tokenType: Token, startLine: int, startColumn: int, startPosition: int):
		self.seekingToken = tokenType
		self.line = startLine
		self.column = startColumn
		self.position = startPosition
		self.stream = ""

	def scout(self, char: str):
		if self.seekingToken.isValidCharacter(char) and (not hasattr(self.seekingToken, "OnlyOne") or len(self.stream) == 0):
			self.stream += char
			return True
		return False

	def packageToken(self):
		return self.seekingToken(self.line, self.column, self.position, self.stream)

class Lexer:
	def __init__(self, data: str, tRegistry: TokenRegistry, BurnSticks=False):
		self.position = -1
		self._data = data
		self.tokens = []
		self.Buffer = None
		self.registry = tRegistry
		self.Finished = False
		self.line = 1
		self.column = 0
		self.stick = Stick.LogFile(DebugName, BurnSticks)

	def Step(self):
		if self.Finished == False:
			self.position += 1
			self.column += 1
			current = self._data[self.position]
			prefix = "(L:{0}, C:{1}, P:{2}) : ".format(self.line, self.column, self.position)
			if self.Buffer: # Try to add to buffer
				Scouted = self.Buffer.scout(current)
				if Scouted == False: # Pack up and move out
					self.stick.Write(Stick.LOGLABEL.LOG, prefix+"Closing Buffer("+self.Buffer.seekingToken.__class__.__name__+")")
					KnuToken = self.Buffer.packageToken()
					self.stick.Write(Stick.LOGLABEL.LOG, prefix+"Adding Token"+str(KnuToken))
					self.tokens.append(KnuToken)
					nextBuffer = self.registry.classifyCharacter(current)
					if nextBuffer:
						self.Buffer = Buffer(nextBuffer, self.line, self.column, self.position)
						self.stick.Write(Stick.LOGLABEL.LOG, prefix+"Opening Buffer("+nextBuffer.__class__.__name__+")")
						self.Buffer.scout(current)
					else:
						self.Buffer = None
			else: # Check for Knu Buffer
				if current.isspace(): # Whitespace can't constitute a knu buffer
					if current == "\n":
						self.line += 1
						self.column = 0
				else:
					bestGuess = self.registry.classifyCharacter(current)
					if bestGuess:
						self.stick.Write(Stick.LOGLABEL.LOG, prefix+"Opening Buffer("+bestGuess.__class__.__name__+")")
						self.Buffer = Buffer(bestGuess, self.line, self.column, self.position)
						self.Buffer.scout(current)
			if self.position >= len(self._data) - 1:
				self.Finished = True
				if self.Buffer:
					self.stick.Write(Stick.LOGLABEL.LOG, prefix+"Closing Buffer("+self.Buffer.seekingToken.__class__.__name__+")")
					KnuToken = self.Buffer.packageToken()
					self.stick.Write(Stick.LOGLABEL.LOG, prefix+"Adding Token"+str(KnuToken))
					self.tokens.append(KnuToken)
					self.Buffer = None

	def FullParse(self):
		while self.Finished == False:
			self.Step()


if __name__ == "__main__":
	import SampleTokens
	alexis = Lexer("100+100=200", SampleTokens.ArithmeticRegistry)
	alexis.FullParse()
	print(alexis.tokens)