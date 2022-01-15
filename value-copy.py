#!/usr/bin/env python3
import pyperclip

welcome_message = "Copie o texto a ser limpo "
inputValue = ""

inputValue = input(welcome_message)

inputValue = inputValue.replace(".", "").replace(" ", "")

print(f"código de barras final: \n {inputValue}")

pyperclip.copy(inputValue)

pyperclip.paste()
