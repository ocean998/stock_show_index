def outer( input ):
    print(input)
    def inner( input2 ):
        print(input+input2)

    return  inner

out = outer('abc')
print('xxxxxxx')
out('def')
out('ghi')
out('123')

def nth_power(exponent):
    def exponent_of(base):
        return base ** exponent
    return exponent_of # 返回值是 exponent_of 函数

square = nth_power(2) # 计算一个数的平方
cube = nth_power(3) # 计算一个数的立方

print(square(2))  # 计算 2 的平方
print(cube(2)) # 计算 2 的立方