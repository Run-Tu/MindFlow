from mindflow.computer import Computer

def main():
    computer = Computer()
    print(computer.available())
    
    script = input("code: ") or """print('Hello, World!')"""
    lang = input("lang: ") or "python"
    
    result = computer.run(script, lang)
    print(result)

if __name__ == "__main__":
    main()
