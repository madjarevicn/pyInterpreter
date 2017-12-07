import math
from math import pi

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER, PLUS, MINUS, MUL, DIV, EOF = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF'
)
LPAREN, RPAREN = (  '(' , ')' )
SIN, COS, TG, LOG =('SIN', 'COS', 'CTG', 'LOG')

#zarez zbog POW(X,Y) - mora se citati kao token
COMMA = 'COMMA'
POW = 'POW'

#naredbe poredjenja
LESS, GREATER, LESS_EQUAL, GREATER_EQUAL, EQUALS = (
    'LESS','GREATER','LESS_EQUAL','GREATER_EQUAL','EQUALS')



#naredba dodele
ASSIGN = 'ASSIGN'
#varijabla
VAR = 'VAR'

PRINT = 'PRINT'
#Mora da bude globalna promenljiva
DICT_TEMP = {}



"""
GRAMATIKA:
    -factor = (LPAREN expr RPAREN) | INTEGER | VAR | FUNCTION(SIN,COS,...)

    -unary = MINUS? factor

    -term = unary((MUL|DIV) unary)*

    -plus_minus = term ((PLUS|MINUS)term)*

    -expr = plus_minus((LESS,GREATER,EQUALS,LESS_EQUAL,GREATER_EQUAL) plus_minus)*

    -high_expr = high_expr = expr

"""
class Token(object):
    def __init__(self, type, value):
        # token type: INTEGER, PLUS, MINUS, MUL, DIV, or EOF
        self.type = type
        # token value: non-negative integer value, '+', '-', '*', '/', or None
        self.value = value

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "3 * 5", "12 / 3 * 4", etc
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    #prelazimo na sledeci
    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]
            
    #preskacemo beline
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    #cita sve int , ne samo jednocifrene
    def integer(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)
    
    #cita ukoliko smo uneli neku rec npr SIN, ili neki naziv promenljive
    def function(self):
        result =''
        while self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()
        return result
    
    #uzimamo sledeci token
    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())
            
            if self.current_char ==',':
                self.advance()
                return Token(COMMA,',')
            
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')
            if self.current_char =='(':
                self.advance()
                return Token(LPAREN,'(')
            
            if self.current_char ==')':
                self.advance()
                return Token(RPAREN,')')

            
            #Proveravamo da li nam je uneta rec neka od funkcija ili je naziv varijable tj.promenljive
            if self.current_char.isalpha():
                name = self.function()
                if name.upper() in (SIN,COS,TG,LOG,POW):
                    return Token(name.upper(),name.upper())
                
                return Token(VAR,name)
                
            if self.current_char =='=':
                self.advance()
                if self.current_char=='=':
                    self.advance()
                    return Token(EQUALS,'==')
                    
                return Token(ASSIGN,'=')
            
            if self.current_char =='<':
                self.advance()
                if self.current_char =='=':
                    self.advance()
                    return Token(LESS_EQUAL,'<=')
                return Token(LESS,'<')
            
            if self.current_char =='>':
                self.advance()
                if self.current_char =='=':
                    self.advance()
                    return Token(GREATER_EQUAL,'>=')
                return Token(GREATER,'>')
            
            
            self.error()
        #ako nije nasao ni jedan token vraca token kraj fajla
        return Token(EOF, None)


class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()
        
    def error(self):
        raise Exception('Invalid syntax')
    
    
    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """
            factor = (LPAREN expr RPAREN) |
            INTEGER | REAL | VAR | FUNCTION(EXPR)
        """
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return token.value
        elif token.type == LPAREN:
            self.eat(LPAREN)
            solution = self.expr()
            self.eat(RPAREN)
            return solution
        elif token.type == SIN:
            self.eat(SIN)
            self.eat(LPAREN)
            solution = math.sin((self.expr()*pi)/180)
            self.eat(RPAREN)
            return solution
        elif token.type == COS:
            self.eat(COS)
            self.eat(LPAREN)
            solution = math.cos((self.expr()*pi)/180)
            self.eat(RPAREN)
            return solution
        elif token.type == TG:
            self.eat(TG)
            self.eat(LPAREN)
            solution = math.tan((self.expr()*pi)/180)
            self.eat(RPAREN)
            return solution
        elif token.type == LOG:
            self.eat(LOG)
            self.eat(LPAREN)
            solution = math.log10(self.expr())
            self.eat(RPAREN)
            return solution
        elif token.type == POW:
            self.eat(POW)
            self.eat(LPAREN)
            base = self.expr()
            self.eat(COMMA)
            exp = self.expr()
            solution = math.pow(base,exp)
            self.eat(RPAREN)
            return solution  
        elif token.type == VAR:
            name = token.value
            self.eat(VAR)
            if self.current_token.type == ASSIGN:
                return name
            if name in DICT_TEMP.keys():
                return DICT_TEMP.get(name)
            else:
                return name
        return token

            
    def unary(self):
        """
            MINUS? FACTOR
        """
        token = self.current_token
        if token.type == MINUS:
            self.eat(MINUS)
            solution = (-1)* self.factor()
        else:
            solution = self.factor()
        return solution
            

    def term(self):
        """term : unary ((MUL | DIV) unary)* """
        result = self.unary()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
                result = result * self.factor()
            elif token.type == DIV:
                self.eat(DIV)
                result = result / self.factor()

        return result

    def plus_minus(self):
        """ term((PLUS|MINUS)term)*"""
        result = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
                result = result + self.term()
            elif token.type == MINUS:
                self.eat(MINUS)
                result = result - self.term()
                
        return result

    def expr(self):
        """
        plus_minus((LESS,GREATER,EQUALS,LESS_EQUAL,GREATER_EQUAL) plus_minus)*
        """
        result = self.plus_minus()

        while self.current_token.type in (LESS,GREATER,EQUALS,LESS_EQUAL,GREATER_EQUAL):
            token = self.current_token
            
            if token.type == EQUALS:
                self.eat(EQUALS)
                x = self.plus_minus()
                return result == x
            elif token.type == LESS:
                self.eat(LESS)
                return result < self.plus_minus()
            elif token.type == GREATER:
                self.eat(GREATER)
                return result > self.plus_minus()
            elif token.type == GREATER_EQUAL:
                self.eat(GREATER_EQUAL)
                return result >= self.plus_minus()
            elif token.type == LESS_EQUAL:
                self.eat(LESS_EQUAL)
                return result <= self.plus_minus()
        return result

    def last_expr(self):
        result = self.expr()
        if self.current_token.type == ASSIGN:
            self.eat(ASSIGN)
            value = self.expr()
            DICT_TEMP[result] = value
            return 'Memorized in dict (key = {result} : value = {value})'.format(
                result = result,
                value = value
                )

        return result




def main():
    
    while True:
        try:
            text = raw_input('>>> ')
            #Ukoliko se unese "EXIT" treba da prekinemo sa izvrsavanjem
            if text.upper() == 'EXIT':
                print 'Bye bye!'
                break
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        result = interpreter.last_expr()
        print(result)
        


if __name__ == '__main__':
    main()
